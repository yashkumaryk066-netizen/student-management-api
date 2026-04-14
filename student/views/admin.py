from .base import *
from student.models import Employee, UserProfile, AuditLog, Student, Batch, Course, SupportTicket, GlobalAnnouncement
from student.serializers import (
    EmployeeSerializer, UserProfileSerializer, AuditLogSerializer,
    StudentSerializer, BatchSerializer, CourseSerializer,
    SupportTicketSerializer, GlobalAnnouncementSerializer
)
from django.contrib.auth.models import User

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

    @transaction.atomic
    def post(self, request):
        """Add new staff member with permissions"""
        try:
            data = request.data
            # Ensure only Client Admin (Owner) can add staff (Superuser bypass)
            if not request.user.is_superuser:
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
            # Get owner profile safely
            owner_profile = getattr(owner, 'profile', None)
            if not owner_profile:
                 # Should not happen for valid clients, but safety check
                 raise ValueError("Owner profile not found")

            UserProfile.objects.create(
                user=user,
                role=data.get('role', 'STAFF'),
                institution_type=owner_profile.institution_type,
                permissions=data.get('permissions', {}), # Store granular permissions
                subscription_expiry=owner_profile.subscription_expiry 
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
            # Transaction will rollback automatically
            message = str(e)
            if "UNIQUE constraint failed" in message:
                message = "User already exists or duplicate entry."
            return Response({"error": message}, status=400)

class AuditLogView(APIView):
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

class GlobalSearchView(APIView):
    """
    Global search across students, employees, and other entities
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response({"error": "Query must be at least 2 characters"}, status=400)
        
        owner = get_owner_user(request.user)
        results = {
            "students": [],
            "employees": [],
            "batches": [],
            "courses": []
        }
        
        # Search Students
        students = Student.objects.filter(
            created_by=owner
        ).filter(
            Q(name__icontains=query) | Q(roll_number__icontains=query) | Q(email__icontains=query)
        )[:10]
        results["students"] = StudentSerializer(students, many=True, context={'request': request}).data
        
        # Search Employees
        employees = Employee.objects.filter(
            created_by=owner
        ).filter(
            Q(user__first_name__icontains=query) | 
            Q(user__last_name__icontains=query) | 
            Q(user__username__icontains=query)
        )[:10]
        results["employees"] = EmployeeSerializer(employees, many=True).data
        
        # Search Batches
        batches = Batch.objects.filter(
            created_by=owner,
            name__icontains=query
        )[:10]
        results["batches"] = BatchSerializer(batches, many=True).data
        
        # Search Courses
        courses = Course.objects.filter(
            created_by=owner,
            name__icontains=query
        )[:10]
        results["courses"] = CourseSerializer(courses, many=True).data
        
        return Response(results)

class AdminApprovalActionView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request, action_type, item_id):
        action = (request.data.get('action') or 'APPROVE').upper()
        action_type = (action_type or '').upper()

        if action_type == 'SUBSCRIPTION':
            from student.models import Payment
            from student.views.finance import approve_subscription_payment

            payment = get_object_or_404(Payment, id=item_id, payment_type='SUBSCRIPTION')
            if not request.user.is_superuser:
                return Response({"error": "Only Super Admin can manage subscription approvals"}, status=403)

            pending_states = {'PENDING', 'PENDING_VERIFICATION', 'OVERDUE'}

            if action == 'APPROVE':
                if payment.status == 'APPROVED':
                    return Response({"message": "Subscription payment already approved", "already_processed": True})
                if payment.status == 'REJECTED':
                    return Response({"error": "Rejected payment cannot be approved"}, status=400)
                if payment.status not in pending_states:
                    return Response({"error": f"Cannot approve payment in status '{payment.status}'"}, status=400)

                with transaction.atomic():
                    payment.status = 'APPROVED'
                    payment.paid_date = timezone.now().date()
                    payment.save(update_fields=['status', 'paid_date', 'updated_at'])
                    email_dispatched, email_reason = approve_subscription_payment(payment)

                AuditLog.objects.create(
                    created_by=request.user,
                    action='SUBSCRIPTION_APPROVED',
                    description=f"Approved subscription payment #{payment.id}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return Response({
                    "message": "Subscription approved successfully",
                    "email_dispatched": bool(email_dispatched),
                    "email_dispatched_reason": email_reason,
                })

            if action == 'REJECT':
                if payment.status == 'REJECTED':
                    return Response({"message": "Subscription payment already rejected", "already_processed": True})
                if payment.status == 'APPROVED':
                    return Response({"error": "Approved payment cannot be rejected"}, status=400)

                payment.status = 'REJECTED'
                payment.save(update_fields=['status', 'updated_at'])
                AuditLog.objects.create(
                    created_by=request.user,
                    action='SUBSCRIPTION_REJECTED',
                    description=f"Rejected subscription payment #{payment.id}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return Response({"message": "Subscription rejected successfully"})

            return Response({"error": "Invalid action. Use APPROVE or REJECT"}, status=400)

        if action_type in {'STUDENT', 'STUDENT_REQUEST'}:
            from student.models import Student

            qs = Student.objects.filter(id=item_id)
            student = qs.first() if request.user.is_superuser else filter_by_owner(qs, request.user).first()
            if not student:
                return Response({"error": "Student request not found or access denied"}, status=404)

            if action == 'APPROVE':
                if student.is_approved:
                    return Response({"message": "Student already approved", "already_processed": True})

                student.is_approved = True
                student.save(update_fields=['is_approved'])
                invalidate_cache('students_list*')
                invalidate_cache('dashboard_stats*')
                AuditLog.objects.create(
                    created_by=request.user,
                    action='STUDENT_APPROVED',
                    description=f"Approved pending student: {student.name}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return Response({"message": "Student approved successfully"})

            if action == 'REJECT':
                student_name = student.name
                student.delete()
                invalidate_cache('students_list*')
                invalidate_cache('dashboard_stats*')
                AuditLog.objects.create(
                    created_by=request.user,
                    action='STUDENT_REJECTED',
                    description=f"Rejected pending student request: {student_name}",
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return Response({"message": "Student request rejected successfully"})

            return Response({"error": "Invalid action. Use APPROVE or REJECT"}, status=400)

        return Response({"error": f"Unsupported action type '{action_type}'"}, status=400)

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return SupportTicket.objects.all()
        return SupportTicket.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class GlobalAnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = GlobalAnnouncementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return GlobalAnnouncement.objects.all()
        # Non-superusers can only view active announcements
        return GlobalAnnouncement.objects.filter(is_active=True)

    def perform_create(self, serializer):
        # Only super admins or authorized roles should create global announcements
        if not self.request.user.is_superuser:
             raise PermissionDenied("Only system administrators can create global announcements.")
        serializer.save(created_by=self.request.user)
