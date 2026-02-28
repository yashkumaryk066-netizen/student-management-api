from .base import *
from student.models import Student, UserProfile, Payment, Grade, Exam
from student.serializers import StudentSerializer
from student.services.permission_service import PermissionService
from student.tasks import run_in_background, task_send_welcome_email, task_send_parent_email
from student.models import AuditLog
from drf_spectacular.utils import extend_schema

class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin, IsPlanFeatureEnabled]
    required_feature = 'students'
    required_permission = 'students.view'

    @track_performance
    @cache_api_response(timeout=300, key_prefix='students_list')
    @extend_schema(operation_id='students_list', responses=StudentSerializer(many=True))
    def get(self, request):
        try:
            students = Student.objects.select_related('parent', 'department').prefetch_related('enrollments').all()
            students = filter_by_owner(students, request.user)

            search = request.query_params.get("search")
            batch_id = request.query_params.get("batch_id")
            grade = request.query_params.get("grade")
            department_id = request.query_params.get("department_id")
            institution_type = request.query_params.get("institution_type")

            if institution_type:
                students = students.filter(institution_type=institution_type)

            if department_id:
                students = students.filter(department_id=department_id)

            if grade:
                students = students.filter(grade=grade)

            if batch_id:
                students = students.filter(enrollments__batch_id=batch_id)


            if search:
                # SECURITY FIX #6: Sanitize search query to prevent SQL injection
                from student.security_utils import sanitize_search_query
                search_clean = sanitize_search_query(search)
                
                students = students.filter(
                    Q(name__icontains=search_clean) |
                    Q(gender__icontains=search_clean)
                )

            return Response(StudentSerializer(students, many=True, context={'request': request}).data)
        except Exception as e:
            logger.error(f"Failed to fetch students: {str(e)}", exc_info=True)
            return Response({"error": "Failed to fetch students. Please try again."}, status=500)

    @extend_schema(operation_id='students_create', request=StudentSerializer, responses=StudentSerializer)
    def post(self, request):
        # SECURITY FIX #9: Use secure password generation
        from student.security_utils import generate_secure_password

        def generate_password():
            return generate_secure_password(length=16)

        owner = get_owner_user(request.user)
        
        # SECURITY FIX #3: Validate photo upload before processing
        from student.security_utils import validate_file_upload
        from django.core.exceptions import ValidationError
        
        if 'photo' in request.FILES:
            try:
                validated_photo = validate_file_upload(
                    request.FILES['photo'],
                    allowed_types=['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
                    max_size_mb=5
                )
                request.FILES['photo'] = validated_photo
            except ValidationError as e:
                return Response({"error": f"Invalid photo: {str(e)}"}, status=400)
        
        data = request.data.copy()
        
        provided_type = data.get('institution_type')
        if not request.user.is_superuser:
            provided_type = owner.profile.institution_type
            data['institution_type'] = provided_type
        elif not provided_type:
             data['institution_type'] = 'SCHOOL'
        
        serializer = StudentSerializer(data=data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    is_approved = True
                    msg = "Student created successfully"
                    if request.user != owner:
                        is_approved = False
                        msg = "Student request submitted for Admin Verification"

                    final_roll_number = request.data.get('roll_number')

                    create_student_login = request.data.get('create_login', False)
                    create_parent_login = request.data.get('create_parent_login', False)
                    
                    student_user = None
                    parent_user = None
                    credentials = {}

                    if create_student_login:
                        s_username = request.data.get('student_username')
                        if not s_username:
                            random_suffix = ''.join(random.choices('0123456789', k=4))
                            s_username = f"{serializer.validated_data['name'].replace(' ', '').lower()}{random_suffix}"
                        
                        while User.objects.filter(username=s_username).exists():
                             s_username = f"{s_username}{random.randint(10, 99)}"

                        s_password = request.data.get('student_password') or generate_password()
                        student_user = User.objects.create_user(
                            username=s_username, 
                            password=s_password,
                            email=data.get('email')
                        )
                        
                        custom_perms = request.data.get('student_permissions', {})
                        final_perms = custom_perms if custom_perms else PermissionService.get_role_template('STUDENT')

                        UserProfile.objects.get_or_create(
                            user=student_user,
                            defaults={
                                'role': 'STUDENT',
                                'institution_type': owner.profile.institution_type,
                                'permissions': final_perms,
                                'subscription_expiry': owner.profile.subscription_expiry
                            }
                        )
                        credentials['student'] = {'username': s_username, 'password': s_password}

                    if create_parent_login:
                        fixed_p_username = request.data.get('parent_username')
                        if fixed_p_username:
                            p_username = fixed_p_username
                        else:
                            p_username = f"p{random.randint(10000,99999)}"
                            while User.objects.filter(username=p_username).exists():
                                p_username = f"p{random.randint(10000,99999)}"

                        p_password = request.data.get('parent_password') or generate_password()
                        parent_user = User.objects.create_user(username=p_username, password=p_password, email=data.get('email'))
                        
                        UserProfile.objects.get_or_create(
                            user=parent_user,
                            defaults={
                                'role': 'PARENT',
                                'institution_type': owner.profile.institution_type,
                                'permissions': PermissionService.get_role_template('PARENT'),
                                'subscription_expiry': owner.profile.subscription_expiry
                            }
                        )
                        credentials['parent'] = {'username': p_username, 'password': p_password}

                    student = serializer.save(
                        created_by=owner, 
                        is_approved=is_approved,
                        user=student_user,
                        parent=parent_user,
                        roll_number=final_roll_number,
                        institution_type=provided_type,
                        photo=request.FILES.get('photo')
                    )

                    payment_obj = None
                    admission_fee = request.data.get('admission_fee')
                    if admission_fee:
                        try:
                            fee_val = float(admission_fee)
                            if fee_val > 0:
                                payment_obj = Payment.objects.create(
                                    student=student,
                                    amount=fee_val,
                                    payment_category='ADMISSION',
                                    payment_mode=request.data.get('payment_mode', 'CASH'),
                                    status='PAID',
                                    description=f"Initial Admission fee for {student.name}"
                                )
                        except (ValueError, TypeError):
                            pass
                    
                    # FEATURE: Auto-Enrollment in Batch (Premium)
                    batch_id = request.data.get('batch_id')
                    if batch_id:
                        from student.models import Batch, Enrollment
                        try:
                            batch = Batch.objects.filter(id=batch_id).first()
                            if batch:
                                Enrollment.objects.get_or_create(
                                    student=student,
                                    batch=batch,
                                    defaults={'status': 'ACTIVE', 'enrolled_at': timezone.now()}
                                )
                        except Exception:
                            logger.error(f"Failed to auto-enroll student {student.id} in batch {batch_id}", exc_info=True)

                    if student_user and student.email:
                        run_in_background(
                            task_send_welcome_email,
                            student_email=student.email,
                            student_name=student.name,
                            username=student_user.username,
                            password=credentials['student']['password'] if 'student' in credentials else "Previously Set",
                            institution_name=owner.profile.institution_name or "Our Institution",
                            institution_type=owner.profile.institution_type,
                            payment_id=payment_obj.id if payment_obj else None
                        )
                    
                    if parent_user:
                        p_email = student.parent_email or student.email
                        run_in_background(
                            task_send_parent_email,
                            parent_email=p_email,
                            parent_name=student.relation or "Parent/Guardian",
                            student_name=student.name,
                            username=parent_user.username,
                            password=credentials['parent']['password'] if 'parent' in credentials else "Previously Set",
                            institution_name=owner.profile.institution_name or "Our Institution",
                            institution_type=owner.profile.institution_type
                        )

                    AuditLog.objects.create(
                        created_by=request.user,
                        action='STUDENT_REQUEST' if not is_approved else 'STUDENT_CREATED',
                        description=f"{'Requested' if not is_approved else 'Added'} new student: {student.name} | Credentials Sent",
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    
                    response_data = serializer.data
                    response_data['message'] = msg if is_approved else "Admission Successful. Credentials sent to student email."
                    response_data['is_approved'] = is_approved
                    if credentials:
                        response_data['credentials'] = credentials

                    invalidate_cache('students_list*')
                    invalidate_cache('dashboard_stats*')

                    return Response(response_data, status=201)

            except Exception as e:
                logger.error(f"Error creating student: {e}", exc_info=True)
                return Response({"error": str(e)}, status=400)
            
            invalidate_cache('students_list*')
            invalidate_cache('dashboard_stats*')

        return Response(serializer.errors, status=400)


class StudentDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


    def get_object(self, user, student_id):
        qs = Student.objects.filter(id=student_id)
        if user.is_superuser:
            return qs.first()
        qs = filter_by_owner(qs, user)
        return qs.first()

    @track_performance
    @cache_api_response(timeout=300, key_prefix='student_detail')
    @extend_schema(operation_id='students_retrieve', responses=StudentSerializer)
    def get(self, request, id):
        student = self.get_object(request.user, id)
        if not student:
            return Response({"error": "Student not found or access denied"}, status=404)
        return Response(StudentSerializer(student, context={'request': request}).data)

    @extend_schema(operation_id='students_update', request=StudentSerializer, responses=StudentSerializer)
    def put(self, request, id):
        student = self.get_object(request.user, id)
        if not student:
            return Response({"error": "Student not found"}, status=404)
        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            invalidate_cache('students_list*')
            invalidate_cache(f'student_detail_{id}*')
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @extend_schema(operation_id='students_partial_update', request=StudentSerializer, responses=StudentSerializer)
    def patch(self, request, id):
        return self.put(request, id)

    @extend_schema(operation_id='students_delete')
    def delete(self, request, id):
        student = self.get_object(request.user, id)
        if not student:
            return Response({"error": "Student not found"}, status=404)
        student.delete()
        return Response(status=204)

class StudentPerformanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            if not request.user.is_superuser and student.created_by != get_owner_user(request.user):
                 return Response({"error": "Access Denied"}, status=403)
            
            grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('exam__exam_date')
            
            performance = []
            for g in grades:
                exam_name = g.exam.name if g.exam else "Unknown Exam"
                subject_name = g.exam.subject.name if (g.exam and g.exam.subject) else "General"
                
                try:
                    marks = float(g.marks_obtained) if g.marks_obtained is not None else 0.0
                except (ValueError, TypeError):
                    marks = 0.0
                    
                try:
                    percentage = float(g.percentage) if g.percentage is not None else 0.0
                except (ValueError, TypeError):
                    percentage = 0.0

                performance.append({
                    "exam_id": g.exam.id if g.exam else 0,
                    "exam_name": exam_name,
                    "date": g.exam.exam_date if g.exam else None,
                    "marks": marks,
                    "total": g.exam.total_marks if g.exam else 100,
                    "percentage": percentage,
                    "status": g.status,
                    "subject": subject_name
                })
            
            return Response(performance)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

class StudentTodayView(APIView):
    """
    Get a 'Today at a Glance' summary for the student dashboards.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "Only students can access daily summaries"}, status=403)
            
        student = request.user.student_profile
        today = timezone.now().date()
        
        # 1. Attendance Check
        from student.models import Attendence
        is_present = Attendence.objects.filter(student=student, date=today, is_present=True).exists()
        
        # 2. Upcoming Exams/Assignments
        from student.models import Exam, LMSAssignment
        upcoming_exams = Exam.objects.filter(
            grade_class=student.grade, 
            exam_date__gte=today
        ).order_by('exam_date')[:3]
        
        # 3. Fees Status
        from student.models import Payment
        pending_fees_total = Payment.objects.filter(
            student=student, 
            status='PENDING'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            "summary": f"Welcome back, {student.name}!",
            "attendance_today": "Marked" if is_present else "Not Marked",
            "upcoming_exams_count": upcoming_exams.count(),
            "pending_fees": float(pending_fees_total),
            "date": today.isoformat()
        })


class StudentAnalyticsView(APIView):
    """
    Premium: Server-side aggregation for Student Stats.
    Replaces heavy client-side calculation.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        try:
            # Base Query
            students = Student.objects.all()
            if not request.user.is_superuser:
                students = filter_by_owner(students, request.user)

            # Optional Filtering (Premium Context Awareness)
            institution_type = request.query_params.get('institution_type')
            if institution_type:
                students = students.filter(institution_type=institution_type)

            total_students = students.count()
            active_list = students.filter(is_active=True)
            active_students = active_list.count()
            
            # Gender Demographics
            boys = active_list.filter(gender__iexact='MALE').count()
            girls = active_list.filter(gender__iexact='FEMALE').count()
            
            # Attendance Today (Requires related lookup)
            from student.models import Attendence
            today = timezone.now().date()
            # Optimization: Use Count with filter instead of fetch
            attendance_today = Attendence.objects.filter(
                student__in=active_list, 
                date=today, 
                is_present=True
            ).count()

            # Financial Health (Pending Fees from Students)
            from student.models import Payment
            from django.db.models import Sum
            pending_fees = Payment.objects.filter(
                student__in=students, # Check all students (even inactive might owe)
                status='PENDING'
            ).aggregate(total=Sum('amount'))['total'] or 0.0

            return Response({
                "total_students": total_students,
                "active_students": active_students,
                "inactive_students": total_students - active_students,
                "gender_distribution": {
                    "boys": boys,
                    "girls": girls,
                    "other": active_students - (boys + girls)
                },
                "attendance": {
                    "present_today": attendance_today,
                    "date": today
                },
                "financials": {
                    "pending_fees_total": float(pending_fees)
                }
            })
        except Exception as e:
            logger.error(f"Analytics Error: {e}", exc_info=True)
            return Response({"error": "Failed to calculate analytics"}, status=500)
