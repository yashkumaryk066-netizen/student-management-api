from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from student.models import Student, Department, AuditLog
from student.serializers import StudentSerializer, DepartmentSerializer
from student.permissions import IsTeacherOrAdmin, IsPlanFeatureEnabled
from .base import filter_by_owner, get_owner_user

class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin, IsPlanFeatureEnabled]
    required_feature = 'students'
    required_permission = 'students.view'

    def get(self, request):
        students = Student.objects.select_related('parent', 'department').all()
        students = filter_by_owner(students, request.user)

        search = request.query_params.get("search")
        batch_id = request.query_params.get("batch_id")
        grade = request.query_params.get("grade")
        department_id = request.query_params.get("department_id")

        if department_id:
            students = students.filter(department_id=department_id)

        if grade:
            students = students.filter(grade=grade)

        if batch_id:
            students = students.filter(enrollments__batch_id=batch_id)

        if search:
            students = students.filter(
                Q(name__icontains=search) |
                Q(gender__icontains=search)
            )

        return Response(StudentSerializer(students, many=True).data)

    def post(self, request):
        from django.db import transaction
        from django.contrib.auth.models import User
        from student.models import UserProfile
        from student.services.permission_service import PermissionService
        import random, string

        def generate_password():
            chars = string.ascii_letters + string.digits + "!@#$"
            return ''.join(random.choice(chars) for _ in range(10))

        # Check Plan Limits First
        owner = get_owner_user(request.user)
        # (Assuming StudentLimitPermission handles the count check on entrance, 
        # but manual double check is good if we are inside method logic overrides)

        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            
            try:
                with transaction.atomic():
                    # 1. Logic for Approval
                    is_approved = True
                    msg = "Student created successfully"
                    if request.user != owner:
                        is_approved = False
                        msg = "Student request submitted for Admin Verification"

                    # 2. Extract Credential Flags
                    create_student_login = request.data.get('create_login', False)
                    create_parent_login = request.data.get('create_parent_login', False)
                    
                    student_user = None
                    parent_user = None
                    credentials = {}

                    # 3. Create Student User
                    if create_student_login:
                        s_username = request.data.get('student_username') or f"u{random.randint(10000,99999)}_{serializer.validated_data['name'].replace(' ', '').lower()}"
                        if User.objects.filter(username=s_username).exists():
                            return Response({"error": f"Student Username {s_username} taken"}, status=400)
                        
                        s_password = request.data.get('student_password') or generate_password()
                        student_user = User.objects.create_user(username=s_username, password=s_password)
                        
                        # Profile & Permissions
                        custom_perms = request.data.get('student_permissions', {})
                        # Fallback to default if empty provided
                        final_perms = custom_perms if custom_perms else PermissionService.get_role_template('STUDENT')

                        UserProfile.objects.create(
                            user=student_user,
                            role='STUDENT',
                            institution_type=owner.profile.institution_type,
                            permissions=final_perms,
                            subscription_expiry=owner.profile.subscription_expiry
                        )
                        credentials['student'] = {'username': s_username, 'password': s_password}

                    # 4. Create Parent User
                    if create_parent_login:
                        # Logic to link existing parent user if username provided?
                        # For now, assume creating new.
                        p_username = request.data.get('parent_username') or f"p{random.randint(10000,99999)}"
                        if User.objects.filter(username=p_username).exists():
                             return Response({"error": f"Parent Username {p_username} taken"}, status=400)

                        p_password = request.data.get('parent_password') or generate_password()
                        parent_user = User.objects.create_user(username=p_username, password=p_password)
                        
                        final_p_perms = request.data.get('parent_permissions', {}) or PermissionService.get_role_template('PARENT')
                        
                        UserProfile.objects.create(
                            user=parent_user,
                            role='PARENT',
                            institution_type=owner.profile.institution_type,
                            permissions=final_p_perms,
                            subscription_expiry=owner.profile.subscription_expiry
                        )
                        credentials['parent'] = {'username': p_username, 'password': p_password}

                    # 5. Save Student Record (Linking Users)
                    student = serializer.save(
                        created_by=owner, 
                        is_approved=is_approved,
                        user=student_user,
                        parent=parent_user
                    )
                    
                    # Log Activity
                    AuditLog.objects.create(
                        created_by=request.user,
                        action='STUDENT_REQUEST' if not is_approved else 'STUDENT_CREATED',
                        description=f"{'Requested' if not is_approved else 'Added'} new student: {student.name}",
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    
                    response_data = serializer.data
                    response_data['message'] = msg
                    response_data['is_approved'] = is_approved
                    if credentials:
                        response_data['credentials'] = credentials
                    
                    return Response(response_data, status=201)

            except Exception as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)


class StudentDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_object(self, user, student_id):
        qs = Student.objects.filter(id=student_id)
        qs = filter_by_owner(qs, user)
        return qs.first()

    def get(self, request, id):
        student = self.get_object(request.user, id)
        if not student:
            return Response({"error": "Student not found"}, status=404)
        return Response(StudentSerializer(student).data)

    def put(self, request, id):
        student = self.get_object(request.user, id)
        if not student:
            return Response({"error": "Student not found"}, status=404)
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        student = self.get_object(request.user, id)
        if not student:
            return Response({"error": "Student not found"}, status=404)
        student.delete()
        return Response(status=204)

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
