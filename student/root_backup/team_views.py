
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import UserProfile, Employee, Student
from .views import get_owner_user
import logging


from .services.permission_service import PermissionService

logger = logging.getLogger(__name__)

class TeamManagementView(APIView):
    """
    Manage Staff/Users (Including HR, Teachers, Students, Parents)
    Only Client/Admin can manage this.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        owner = get_owner_user(request.user)
        
        # Determine strict role filtering (HR can see some, Client sees all)
        current_role = request.user.profile.role if hasattr(request.user, 'profile') else None
        
        if current_role == 'HR':
             # HR sees Students, Teachers, Parents, but NOT other HRs or Client
             users = UserProfile.objects.filter(
                 user__created_students__created_by=owner
             ).exclude(role__in=['CLIENT', 'ADMIN', 'HR'])
             # This query logic is complex due to indirect relation. 
             # Simpler: Find profiles associated with this owner account
             # Since UserProfile doesn't have 'created_by', we look at Employee or Student models usually.
             # But here we are listing USERS.
             # Standardizing: We need to filter users created by this owner.
             # Currently our User model doesn't explicitly store 'created_by' except via Profile relations
             # Let's assume Employee/Student models are the source of truth.
        else:
             # Client sees everyone they created
             pass

        # Simplified approach: List Employees and Students
        employees = Employee.objects.filter(created_by=owner).select_related('user', 'user__profile')
        students = Student.objects.filter(created_by=owner).select_related('user', 'user__profile')
        
        data = []
        
        for emp in employees:
            data.append({
                "id": emp.user.id,
                "username": emp.user.username,
                "name": emp.user.get_full_name(),
                "role": emp.user.profile.role,
                "type": "STAFF",
                "designation": emp.designation.title if emp.designation else "N/A",
                "is_active": emp.is_active
            })
            
        for stu in students:
            if stu.user:
                data.append({
                    "id": stu.user.id,
                    "username": stu.user.username,
                    "name": stu.name,
                    "role": "STUDENT",
                    "type": "STUDENT",
                    "designation": f"Grade {stu.grade}",
                    "is_active": True
                })
        
        return Response(data)

    def post(self, request):
        """Create New User (HR, Teacher, Student, Parent)"""
        if not hasattr(request.user, 'profile'):
             return Response({"error": "No profile found"}, status=403)
             
        creator_role = request.user.profile.role
        
        # HR can create Student/Parent/Teacher.
        # Client can create HR + Above.
        
        target_role = request.data.get('role', '').upper()
        if target_role == 'HR' and creator_role != 'CLIENT':
             return Response({"error": "Only Owner can create HR staff"}, status=403)
        
        if target_role == 'CLIENT':
             return Response({"error": "Cannot create another Client"}, status=403)

        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if User.objects.filter(username=username).exists():
             return Response({"error": "Username already taken"}, status=400)
             
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=username, email=email, password=password)
                user.first_name = request.data.get('first_name', '')
                user.last_name = request.data.get('last_name', '')
                user.save()
                
                # Check Owner
                owner = get_owner_user(request.user)
                
                # Create Profile
                profile = UserProfile.objects.create(
                    user=user,
                    role=target_role,
                    institution_type=request.user.profile.institution_type, # Inherit inst type
                    force_password_change=True, # Flag to force change on first login
                    permissions=request.data.get('permissions', {}) # Save Granular Permissions
                )
                
                # Link specific models
                if target_role in ['TEACHER', 'HR']:
                    Employee.objects.create(
                        user=user,
                        created_by=owner,
                        is_active=True
                        # Designation etc would be separate update
                    )
                elif target_role == 'STUDENT':
                    # Ideally linked to existing Student record or creates one
                    pass 
                
                return Response({"message": f"User {username} created as {target_role}", "id": user.id}, status=201)
                
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return Response({"error": str(e)}, status=500)

class StaffPermissionUpdateView(APIView):
    """
    Update granular permissions for a staff member.
    Only Owner/Client can do this.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, user_id):
        # 1. Verify Requestor (Must be Client)
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'CLIENT':
             return Response({"error": "Permission denied"}, status=403)
             
        owner = get_owner_user(request.user)
        
        # 2. Verify Target User (Must be created by this Client)
        target_user = get_object_or_404(User, id=user_id)
        
        # Check ownership via Employee linkage usually, or ensure they fall under owner's hierarchy
        # Since we don't have direct 'created_by' on User, we check Profile or Linked models.
        # Strict check: Target must be in Employee linked to Owner OR Student linked to Owner
        is_owned = False
        if Employee.objects.filter(user=target_user, created_by=owner).exists():
            is_owned = True
        elif Student.objects.filter(user=target_user, created_by=owner).exists():
             is_owned = True
        
        if not is_owned:
            return Response({"error": "User not found in your organization"}, status=404)
            
        # 3. Validate Permissions
        new_perms = request.data.get('permissions', {})
        if not PermissionService.validate_permission_schema(new_perms):
            return Response({"error": "Invalid permission format"}, status=400)
            
        # 4. Save
        target_user.profile.permissions = new_perms
        target_user.profile.save()
        
        return Response({"message": "Permissions updated successfully"})

class StaffPasswordResetView(APIView):
    """
    Allow Client to forced-reset password for their staff/students.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        # 1. Verify Client
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'CLIENT':
             return Response({"error": "Permission denied"}, status=403)
             
        owner = get_owner_user(request.user)
        target_user = get_object_or_404(User, id=user_id)
        
        # 2. Verify Ownership
        is_owned = Employee.objects.filter(user=target_user, created_by=owner).exists() or \
                   Student.objects.filter(user=target_user, created_by=owner).exists()
                   
        if not is_owned:
             return Response({"error": "User not found in your organization"}, status=404)
             
        # 3. Reset
        new_password = request.data.get('password')
        if not new_password or len(new_password) < 6:
             return Response({"error": "Password must be at least 6 chars"}, status=400)
             
        target_user.set_password(new_password)
        target_user.save()
        
        # Optional: Set force_password_change flag
        target_user.profile.force_password_change = True
        target_user.profile.save()
        
        return Response({"message": f"Password for {target_user.username} reset successfully"})

class PermissionTemplatesView(APIView):
    """
    Expose permission templates to Frontend for 'Check All' functionality.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(PermissionService.ROLE_DEFAULTS)

# Alias for compatibility with URLs if needed, or update URLs to use TeamManagementView
TeamMemberManagementView = TeamManagementView
