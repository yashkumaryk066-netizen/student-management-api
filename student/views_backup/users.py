from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from datetime import date

from student.models import Employee, UserProfile, ClientSubscription, AuditLog
from student.serializers import EmployeeSerializer, UserProfileSerializer, AuditLogSerializer
from student.permissions import IsPlanFeatureEnabled
from .base import filter_by_owner, get_owner_user

class TeamManagementView(APIView):
    permission_classes = [IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'users'

    def get(self, request):
        """List all staff and teachers in the institution"""
        # Get employees with related user and department
        employees = filter_by_owner(
            Employee.objects.select_related('user', 'user__profile', 'department', 'designation').all(), 
            request.user
        )
        
        return Response({
            "employees": EmployeeSerializer(employees, many=True).data,
            "roles": [
                {"id": "TEACHER", "name": "Teacher"},
                {"id": "ADMIN", "name": "Admin"},
                {"id": "STUDENT", "name": "Student"}
            ]
        })

    def post(self, request):
        """Add new staff member with permissions"""
        try:
            data = request.data
            # Ensure only Client Admin (Owner) can add staff
            if hasattr(request.user, 'profile') and request.user.profile.role != 'CLIENT':
                 return Response({"error": "Only the Account Owner can add team members"}, status=403)
                 
            owner = request.user 
            
            # 1. Create User
            if User.objects.filter(username=data['username']).exists():
                return Response({"error": "Username already taken"}, status=400)
                
            user = User.objects.create_user(
                username=data['username'],
                email=data.get('email', ''),
                password=data['password'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', '')
            )
            
            # 2. Create Profile with Role & Permissions
            # Inherit institution type and plan expiry from Owner
            UserProfile.objects.create(
                user=user,
                role=data.get('role', 'STAFF'),
                institution_type=owner.profile.institution_type,
                permissions=data.get('permissions', {}), # Store granular permissions
                subscription_expiry=owner.profile.subscription_expiry 
            )
            
            # 3. Create Employee Record
            # Handle optional foreign keys safely
            dept_id = data.get('department_id') or None
            desig_id = data.get('designation_id') or None
            
            Employee.objects.create(
                user=user,
                created_by=owner,
                joining_date=data.get('joining_date', timezone.now().date()),
                basic_salary=data.get('basic_salary', 0),
                contract_type=data.get('contract_type', 'PERMANENT'),
                designation_id=desig_id,
                department_id=dept_id
            )
            
            return Response({"message": "Team member added successfully", "user_id": user.id}, status=201)
            
        except Exception as e:
            # Cleanup if partially created
            if 'user' in locals() and user.id: 
                user.delete()
            return Response({"error": str(e)}, status=400)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        import traceback
        try:
            from student.plan_permissions import get_user_plan, PLAN_FEATURES
            
            user = request.user
            print(f"📡 API PROFILE ACCESS: {user.username} (SuperUser: {user.is_superuser})")
            
            # 1. GOD MODE: Immediate Return for SuperUser
            # Bypass all other checks if superuser
            if user.is_superuser:
                return Response({
                    "username": user.username,
                    "email": user.email,
                    "role": "ADMIN",
                    "id": user.id,
                    "is_superuser": True,
                    "user_full_name": user.get_full_name() or "Super Administrator",
                    "available_features": PLAN_FEATURES.get('SUPER_ADMIN', []),
                    # Mock profile data to prevent frontend crashes
                    "institution_name": "Y.S.M CENTRAL COMMAND", 
                    "phone": "",
                    "address": "System Root",
                    "institution_type": "EDUCATION SYSTEM",
                    "subscription_plan": "ENTERPRISE",
                })
            
            # Check profile and role
            profile = getattr(user, 'profile', None)
            role = profile.role if profile else 'STUDENT'
            
            # Get Features
            plan = get_user_plan(user)
            features = PLAN_FEATURES.get(plan, [])

            data = {
                "username": user.username,
                "email": user.email,
                "role": role,
                "id": user.id,
                "is_superuser": user.is_superuser,
                "user_full_name": user.get_full_name(),
                "available_features": features
            }
            
            if profile:
                 profile_data = UserProfileSerializer(profile).data
                 # Ensure full URLs for images
                 if profile.institution_logo:
                     profile_data['institution_logo'] = request.build_absolute_uri(profile.institution_logo.url)
                 if profile.digital_signature:
                     profile_data['digital_signature'] = request.build_absolute_uri(profile.digital_signature.url)
                 data.update(profile_data)
                 
            return Response(data)
        except Exception as e:
            print("❌ CRITICAL ERROR IN PROFILE VIEW ❌")
            traceback.print_exc()
            return Response({"error": str(e), "trace": traceback.format_exc()}, status=500)
    
    def put(self, request):
        """Update user profile information"""
        user = request.user
        data = request.data
        
        # Update User model fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
        
        user.save()
        
        # Update Profile model fields if profile exists
        if hasattr(user, 'profile'):
            profile = user.profile
            if 'phone' in data:
                profile.phone = data['phone']
            if 'institution_name' in data:
                profile.institution_name = data['institution_name']
            if 'address' in data:
                profile.address = data['address']
            
            # File Uploads (Branding)
            # request.FILES contains the files when using MultiPartParser
            if 'institution_logo' in request.FILES:
                profile.institution_logo = request.FILES['institution_logo']
            
            if 'digital_signature' in request.FILES:
                profile.digital_signature = request.FILES['digital_signature']

            profile.save()
        
        return Response({
            "message": "Profile updated successfully",
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })
    
    def patch(self, request):
        return self.put(request)

class ClientSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Auto-create subscription if missing (Advance Level User Experience)
        if not hasattr(request.user, 'subscription'):
            try:
                # Create an EXPIRED 'COACHING' subscription to minimize access risk
                ClientSubscription.objects.create(
                    user=request.user,
                    plan_type='COACHING',
                    status='EXPIRED',
                    start_date=date.today(),
                    end_date=date.today()
                )
            except Exception:
                pass # Fallback to NO_SUBSCRIPTION response if creation fails

        if hasattr(request.user, 'subscription'):
             sub = request.user.subscription
             return Response({
                 "plan_type": sub.plan_type,
                 "status": sub.status,
                 "valid_until": sub.end_date,
                 "days_left": sub.days_remaining,
                 "plan": sub.plan_type, # Backward compat
                 "amount_paid": sub.amount_paid,
                 "start_date": sub.start_date,
                 "end_date": sub.end_date,
             })
        return Response({"status": "NO_SUBSCRIPTION", "days_left": 0})

class SubscriptionRenewalView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
         return Response({"message": "Renewal initiated"})

class ClientAuditLogListView(APIView):
    permission_classes = [IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'logs'

    def get(self, request):
        owner = get_owner_user(request.user)
        # Show logs for the owner and their staff
        logs = AuditLog.objects.filter(
            Q(created_by=owner) | 
            Q(created_by__employee_profile__created_by=owner)
        ).order_by('-created_at')[:100]
        
        return Response(AuditLogSerializer(logs, many=True).data)
