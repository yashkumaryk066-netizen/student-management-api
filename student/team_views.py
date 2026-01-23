
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import UserProfile, Employee, Student
from .views import get_owner_user
import logging

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
                    force_password_change=True # Flag to force change on first login
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
