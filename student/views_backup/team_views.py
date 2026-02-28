from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from student.models import UserProfile, Employee
from student.services.permission_service import PermissionService
from student.permissions import IsPlanFeatureEnabled
import random
import string

class PermissionTemplatesView(APIView):
    """
    Returns the default permission sets for different roles.
    Used by Frontend to populate the "Add Staff/Team" form checkboxes.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(PermissionService.get_all_templates())


class TeamMemberManagementView(APIView):
    """
    Manage Team Members (Teachers, HR, Accountants, etc.)
    with Granular Permissions.
    """
    permission_classes = [permissions.IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'users' # Requires 'users' feature in Plan

    def _generate_password(self):
        """Generate a random strong password"""
        chars = string.ascii_letters + string.digits + "!@#$"
        return ''.join(random.choice(chars) for _ in range(10))

    def get(self, request):
        """List all team members for the institution"""
        # Logic to filter only staff created by this Client
        # Assumes request.user is the Client/Owner or has permission to view
        owner = request.user
        if hasattr(owner, 'profile') and owner.profile.role != 'CLIENT':
             # If strictly checking ownership, might need helper. For now assume Client.
             pass
             
        # Filter profiles linked to this institution (via owner match or institution_id match if implemented)
        # Using simple created_by logic on Employee for now
        employees = Employee.objects.filter(created_by=owner).select_related('user', 'user__profile')
        
        data = []
        for emp in employees:
            user = emp.user
            profile = getattr(user, 'profile', None)
            data.append({
                "id": user.id,
                "name": user.get_full_name(),
                "username": user.username,
                "role": profile.role if profile else "N/A",
                "department": emp.department.name if emp.department else None,
                "permissions": profile.permissions if profile else {},
                "is_active": user.is_active
            })
            
        return Response(data)

    def post(self, request):
        """
        Create a new Team Member with specific Granular Permissions.
        """
        data = request.data
        owner = request.user
        
        # 1. Validation
        if User.objects.filter(username=data.get('username')).exists():
            return Response({"error": "Username already taken"}, status=400)
            
        role = data.get('role', 'TEACHER')
        
        # 2. Permission Logic
        # Client sends a dict of permissions. If empty/partial, merge with defaults?
        # Strategy: Use provided permissions as the Source of Truth.
        # Frontend should have pre-filled standard defaults which user modified.
        custom_permissions = data.get('permissions', {})
        if not custom_permissions:
            # Fallback to defaults if nothing provided
            custom_permissions = PermissionService.get_role_template(role)

        password = data.get('password') or self._generate_password()

        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create_user(
                    username=data['username'],
                    password=password,
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    email=data.get('email', '')
                )
                
                # Create Profile
                # Inherit Plan State from Owner
                owner_profile = owner.profile
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    institution_type=owner_profile.institution_type,
                    permissions=custom_permissions, # <--- KEY: Storing granular permissions
                    subscription_expiry=owner_profile.subscription_expiry or timezone.now().date(),
                    # Optional: Link to same institution identifier logic if/when added
                )
                
                # Create Employee Record
                Employee.objects.create(
                    user=user,
                    created_by=owner,
                    designation_id=data.get('designation_id'),
                    department_id=data.get('department_id'),
                    joining_date=data.get('joining_date', timezone.now().date())
                )

                # Return Credentials for immediate display/copying
                return Response({
                    "message": "Team member created successfully",
                    "credentials": {
                        "username": user.username,
                        "password": password, # Only show once!
                        "role": role
                    },
                    "permissions_granted": custom_permissions
                }, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class StaffPermissionUpdateView(APIView):
    """
    Update permissions for an existing Team Member
    """
    permission_classes = [permissions.IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'users'

    def put(self, request, user_id):
        # 1. Validation: Ensure user belongs to this client
        try:
            target_user = User.objects.get(id=user_id)
            # Check ownership via Employee or Profile hierarchy
            # Simplest: Check if target's profile has same institution type/owner logic
            # or check Employee created_by
            if not Employee.objects.filter(user=target_user, created_by=request.user).exists():
                 return Response({"error": "Staff member not found or access denied"}, status=403)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
            
        # 2. Update Permissions
        new_permissions = request.data.get('permissions', {})
        
        target_profile = target_user.profile
        target_profile.permissions = new_permissions
        target_profile.save()
        
        return Response({
            "message": "Permissions updated successfully",
            "user_id": user_id,
            "new_permissions": new_permissions
        })


class StaffPasswordResetView(APIView):
    """
    Client Admin resets password for a Team Member
    """
    permission_classes = [permissions.IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'users'

    def post(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
            # Check ownership
            if not Employee.objects.filter(user=target_user, created_by=request.user).exists():
                 return Response({"error": "Staff member not found or access denied"}, status=403)
                 
            # Generate or use provided password
            new_password = request.data.get('new_password')
            if not new_password:
                chars = string.ascii_letters + string.digits + "!@#$"
                new_password = ''.join(random.choice(chars) for _ in range(10))
            
            target_user.set_password(new_password)
            target_user.save()
            
            return Response({
                "message": "Password reset successfully",
                "new_password": new_password
            })
            
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
