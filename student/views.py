from rest_framework.views import APIView
from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.response import Response
from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Course, Batch, Enrollment
)
from .Serializer import (
    StudentSerializer, AttendenceSerializer, UserProfileSerializer, PaymentSerializer, NotificationSerializer,
    CourseSerializer, BatchSerializer, EnrollmentSerializer
)
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .permissions import IsStudent, IsTeacher, IsParent, IsAdminRole, IsTeacherOrAdmin, IsClient, StudentLimitPermission
from datetime import date, timedelta

@extend_schema_view(
    get=extend_schema(
        tags=['Student'],
        operation_id='listStudents',
        summary='List all students',
        description='Retrieve a list of all students with optional search by name or gender',
        responses={200: StudentSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search students by name or gender',
                required=False,
            ),
        ],
    ),
    post=extend_schema(
        tags=['Student'],
        operation_id='createStudent',
        summary='Create a new student',
        description='Create a new student record',
        request=StudentSerializer,
        responses={201: StudentSerializer},
    ),
)
class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin, StudentLimitPermission]
    required_feature = 'students'  # For plan-based access control
    
    def get(self, request):
        search = request.query_params.get("search","").strip()
        batch_id = request.query_params.get("batch_id")
        institution_type = request.query_params.get("institution_type")
        grade = request.query_params.get("grade")
        
        students = Student.objects.all()
        
        # --- SAAS DATA ISOLATION ---
        if not request.user.is_superuser:
            if hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT':
                 # Client sees only their students
                 students = students.filter(created_by=request.user)
            elif hasattr(request.user, 'employee_profile') and request.user.employee_profile.created_by:
                 # Staff sees students created by their Employer (Client)
                 students = students.filter(created_by=request.user.employee_profile.created_by)
            elif hasattr(request.user, 'profile') and request.user.profile.role == 'STUDENT':
                 # Student sees only themselves? (Or disabled here)
                 # Usually separate view, but allowed for filtering own record?
                 pass 
        # ---------------------------

        if not request.user.is_superuser and hasattr(request.user, 'profile'):
             # ENFORCE: Only show students for the user's institution type (redundant if isolation valid, but safety net)
             if request.user.profile.role != 'CLIENT' and not hasattr(request.user, 'employee_profile'):
                 institution_type = request.user.profile.institution_type
                 students = students.filter(institution_type=institution_type)
        elif institution_type:
            # For Superadmin, allow filtering via param
            students = students.filter(institution_type=institution_type)

        if grade:
            students = students.filter(grade=grade)
        
        if batch_id:
            students = students.filter(enrollments__batch_id=batch_id, enrollments__status='ACTIVE')
            
        if search:
            students= students.filter(
                Q(name__icontains=search)|
                Q(gender__icontains=search)
            )
            
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            # Auto-assign Institution Type based on Admin's Profile (if not superuser)
            institution_type = serializer.validated_data.get('institution_type', 'SCHOOL')
            owner = None

            if not request.user.is_superuser:
                 # Determine Owner (Client)
                 if hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT':
                      owner = request.user
                 elif hasattr(request.user, 'employee_profile'):
                      owner = request.user.employee_profile.created_by

                 if hasattr(request.user, 'profile'):
                      user_plan = request.user.profile.institution_type
                      
                      # Strict Plan Enforcement
                      if user_plan == 'COACHING':
                          institution_type = 'COACHING' # Lock to Coaching
                      elif user_plan == 'SCHOOL':
                           if institution_type not in ['SCHOOL', 'COACHING']:
                               institution_type = 'SCHOOL' 
                      elif user_plan == 'INSTITUTE':
                           pass
              
            save_kwargs = {'institution_type': institution_type}
            if owner:
                save_kwargs['created_by'] = owner
            
            serializer.save(**save_kwargs)
                 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=['Student'],
        operation_id='getStudent',
        summary='Get student details',
        description='Retrieve details of a specific student by ID',
        responses={200: StudentSerializer},
    ),
    put=extend_schema(
        tags=['Student'],
        operation_id='updateStudent',
        summary='Update student',
        description='Update an existing student record',
        request=StudentSerializer,
        responses={200: StudentSerializer},
    ),
    delete=extend_schema(
        tags=['Student'],
        operation_id='deleteStudent',
        summary='Delete student',
        description='Delete a student record',
        responses={204: None},
    ),
)
class StudentDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def get(self, request, id):
        student = Student.objects.filter(id=id).first()
        if not student:
            return Response(
                {"error": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        student = Student.objects.filter(id=id).first()
        if not student:
            return Response(
                {"error": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        student = Student.objects.filter(id=id).first()
        if not student:
            return Response(
                {"error": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(
            {"message": "Student deleted"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
@extend_schema_view(
    get=extend_schema(
        tags=['Student'],
        operation_id='getTodayAttendance',
        summary="Get today's attendance summary",
        description="Get attendance summary for today including present and absent students",
    ),
)
class StudentTodayView(APIView):
    
    def get(self, request):
        today = timezone.now().date()

        total_students = Student.objects.count()

        today_attendance = Attendence.objects.filter(date=today).select_related('student')

        present_students = today_attendance.filter(is_present=True)
        absent_students = today_attendance.filter(is_present=False)

        present_serializer = StudentSerializer(
            [a.student for a in present_students], many=True
        )

        absent_serializer = StudentSerializer(
            [a.student for a in absent_students], many=True
        )

        return Response({
            "date": str(today),
            "total_students": total_students,
            "present_count": present_students.count(),
            "absent_count": absent_students.count(),
            "present_students": present_serializer.data,
            "absent_students": absent_serializer.data
        }, status=status.HTTP_200_OK)
        
@extend_schema_view(
    get=extend_schema(
        tags=['Attendance'],
        operation_id='listAttendance',
        summary='List all attendance records',
        description='Retrieve all attendance records',
        responses={200: AttendenceSerializer(many=True)},
    ),
    post=extend_schema(
        tags=['Attendance'],
        operation_id='markAttendance',
        summary='Mark attendance',
        description='Mark attendance for a student. Prevents duplicate entries for the same date.',
        request=AttendenceSerializer,
        responses={201: AttendenceSerializer},
    ),
)
class AttendenceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def get(self, request):
        attendence = Attendence.objects.all()
        serializer = AttendenceSerializer(attendence, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if isinstance(request.data, list):
            # Bulk Create
            created_records = []
            errors = []
            
            for item in request.data:
                student_id = item.get("student")
                date = item.get("date")
                if not date:
                    date = timezone.now().date()
                    item['date'] = date
                    
                # Skip duplicate
                if Attendence.objects.filter(student_id=student_id, date=date).exists():
                    continue
                    
                serializer = AttendenceSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    created_records.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            
            return Response(created_records, status=status.HTTP_201_CREATED)
            
        else:
            # Single Create
            student_id = request.data.get("student")
            date = request.data.get("date")
            if not date:
                date = timezone.now().date()
            if Attendence.objects.filter(student_id=student_id, date=date).exists():
                return Response(
                    {"message": "Attendance already marked"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = AttendenceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=['Attendance'],
        operation_id='getAttendance',
        summary='Get attendance details',
        description='Retrieve details of a specific attendance record by ID',
        responses={200: AttendenceSerializer},
    ),
    put=extend_schema(
        tags=['Attendance'],
        operation_id='updateAttendance',
        summary='Update attendance',
        description='Update an existing attendance record',
        request=AttendenceSerializer,
        responses={200: AttendenceSerializer},
    ),
    delete=extend_schema(
        tags=['Attendance'],
        operation_id='deleteAttendance',
        summary='Delete attendance',
        description='Delete an attendance record',
        responses={204: None},
    ),
)
class AttendenceDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def get(self, request, id):
        attendence = Attendence.objects.filter(id=id).first()
        if not attendence:
            return Response(
                {"error": "Attendence not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendenceSerializer(attendence)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        attendence = Attendence.objects.filter(id=id).first()
        if not attendence:
            return Response(
                {"error": "Attendence not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendenceSerializer(attendence, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        attendence = Attendence.objects.filter(id=id).first()
        if not attendence:
            return Response(
                {"error": "Attendence not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        attendence.delete()
        return Response(
            {"message": "Attendence deleted"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    

@extend_schema_view(
    get=extend_schema(
        tags=['Profile'],
        operation_id='getProfile',
        summary='Get user profile',
        description='Get the authenticated user profile information',
    ),
    post=extend_schema(
        tags=['Profile'],
        operation_id='getProfilePost',
        summary='Get user profile (POST)',
        description='Get the authenticated user profile information via POST',
    ),
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.get_full_name(),
                "date_joined": user.date_joined,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
            
            # Try to get UserProfile details if they exist
            if hasattr(user, 'profile'):
                profile = user.profile
                data.update({
                    "role": profile.role,
                    "institution_type": profile.institution_type,
                    "phone": profile.phone,
                    "profile_id": profile.id
                })
            else:
                data.update({
                    "role": "ADMIN" if user.is_superuser else "STUDENT", # Default to STUDENT not USER for safety
                    "phone": "",
                    "profile_id": None
                })
                
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"❌ Profile View Error: {str(e)}")
            return Response({
                "error": "Profile Error",
                "message": str(e),
                "role": "student" # Fallback role to prevent frontend crash
            }, status=status.HTTP_200_OK) # Return 200 with error so frontend parsing works (or handle 500 in frontend)

    def post(self, request):
        return self.get(request)
    
    def put(self, request):
        user = request.user
        data = request.data
        
        # Update User fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
            
        user.save()
        
        # Update Profile fields if profile exists
        if hasattr(user, 'profile'):
            profile = user.profile
            if 'phone' in data:
                profile.phone = data['phone']
            profile.save()
            
        return self.get(request)
        
    def patch(self, request):
        return self.put(request)

# Role-Based Dashboard and New Feature Views
# Add these to existing views.py

from .models import UserProfile, Payment, Notification
from .Serializer import UserProfileSerializer, PaymentSerializer, NotificationSerializer
from .permissions import IsStudent, IsTeacher, IsParent, IsAdminRole, IsTeacherOrAdmin
from django.db.models import Count, Q
from datetime import date, timedelta

# ==================== ROLE-BASED DASHBOARDS ====================

class StudentDashboardView(APIView):
    """Dashboard for students - own attendance, fees, notifications"""
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
            
            # Get attendance records
            total_days = Attendence.objects.filter(student=student).count()
            present_days = Attendence.objects.filter(student=student, is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Get payment info
            pending_payments = Payment.objects.filter(student=student, status__in=['PENDING', 'OVERDUE'])
            total_due = sum(p.amount for p in pending_payments)
            
            # Get recent notifications
            notifications = Notification.objects.filter(
                Q(recipient=request.user) | Q(recipient_type='STUDENT') | Q(recipient_type='ALL'),
                is_read=False
            )[:5]
            
            return Response({
                'role': 'STUDENT',
                'student': StudentSerializer(student).data,
                'attendance': {
                    'total_days': total_days,
                    'present_days': present_days,
                    'attendance_percentage': round(attendance_percentage, 2)
                },
                'payments': {
                    'total_due': float(total_due),
                    'pending_count': pending_payments.count(),
                    'payments': PaymentSerializer(pending_payments, many=True).data
                },
                'notifications': NotificationSerializer(notifications, many=True).data
            }, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

class TeacherDashboardView(APIView):
    """Dashboard for teachers - all students, mark attendance, send notifications"""
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Get all students
        total_students = Student.objects.count()
        
        # Today's attendance
        today_attendance = Attendence.objects.filter(date=today)
        present_today = today_attendance.filter(is_present=True).count()
        absent_today = today_attendance.filter(is_present=False).count()
        
        # Pending payments count
        overdue_payments = Payment.objects.filter(status='OVERDUE').count()
        
        # Unread notifications
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='TEACHER') | Q(recipient_type='ALL'),
            is_read=False
        )[:5]
        
        return Response({
            'role': 'TEACHER',
            'stats': {
                'total_students': total_students,
                'present_today': present_today,
                'absent_today': absent_today,
                'not_marked': total_students - present_today - absent_today,
                'overdue_payments': overdue_payments
            },
            'notifications': NotificationSerializer(notifications, many=True).data
        }, status=status.HTTP_200_OK)

class ParentDashboardView(APIView):
    """Dashboard for parents - children's data, payments, notifications"""
    permission_classes = [IsAuthenticated, IsParent]
    
    def get(self, request):
        # Get all children linked to this parent
        children = Student.objects.filter(parent=request.user)
        
        if not children.exists():
            return Response({'error': 'No children linked to this account'}, status=status.HTTP_404_NOT_FOUND)
        
        children_data = []
        total_due = 0
        
        for child in children:
            # Get attendance
            total_days = Attendence.objects.filter(student=child).count()
            present_days = Attendence.objects.filter(student=child, is_present=True).count()
            
            # Get payments
            pending_payments = Payment.objects.filter(student=child, status__in=['PENDING', 'OVERDUE'])
            child_due = sum(p.amount for p in pending_payments)
            total_due += child_due
            
            children_data.append({
                'student': StudentSerializer(child).data,
                'attendance': {
                    'total_days': total_days,
                    'present_days': present_days,
                    'percentage': round((present_days / total_days * 100) if total_days > 0 else 0, 2)
                },
                'payments': {
                    'due_amount': float(child_due),
                    'pending_count': pending_payments.count()
                }
            })
        
        # Get notifications
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='PARENT') | Q(recipient_type='ALL'),
            is_read=False
        )[:5]
        
        return Response({
            'role': 'PARENT',
            'children': children_data,
            'total_due': float(total_due),
            'notifications': NotificationSerializer(notifications, many=True).data
        }, status=status.HTTP_200_OK)

# ==================== PAYMENT VIEWS ====================

class PaymentListCreateView(APIView):
    """List and create payments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'ADMIN'
        
        if user_role == 'PARENT':
            # Parents see only their children's payments
            children = Student.objects.filter(parent=request.user)
            payments = Payment.objects.filter(student__in=children)
        elif user_role == 'STUDENT':
            # Students see only their own payments
            try:
                student = Student.objects.get(user=request.user)
                payments = Payment.objects.filter(student=student)
            except Student.DoesNotExist:
                return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Teachers and admins see all
            payments = Payment.objects.all()
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        # Only admin and teachers can create payments - enforced via decorator
        user_role = request.user.profile.role if hasattr(request.user, 'profile') else None
        if user_role not in ['ADMIN', 'TEACHER']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Create notification for parent
            student = payment.student
            if student.parent:
                Notification.objects.create(
                    recipient_type='PARENT',
                    recipient=student.parent,
                    title=f'New Payment Due for {student.name}',
                    message=f'A payment of ₹{payment.amount} is due on {payment.due_date.strftime("%d-%b-%Y")}. {payment.description}'
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentDetailsView(APIView):
    """View and update specific payment"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        try:
            payment = Payment.objects.get(id=id)
            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            payment = Payment.objects.get(id=id)
            payment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, id):
        try:
            payment = Payment.objects.get(id=id)
            
            # Mark as paid
            if request.data.get('mark_paid'):
                payment.status = 'PAID'
                payment.paid_date = timezone.now().date()
                payment.save()
                
                # Notify parent
                if payment.student.parent:
                    Notification.objects.create(
                        recipient_type='PARENT',
                        recipient=payment.student.parent,
                        title='Payment Confirmed',
                        message=f'Payment of ₹{payment.amount} for {payment.student.name} has been confirmed. Thank you!'
                    )
                
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
            
            # Update payment details
            serializer = PaymentSerializer(payment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

# ==================== NOTIFICATION VIEWS ====================

class NotificationListView(APIView):
    """Get notifications for current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'ADMIN'
        
        # Get notifications for this user's role or specifically for them
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | 
            Q(recipient_type=user_role) | 
            Q(recipient_type='ALL')
        )
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationMarkReadView(APIView):
    """Mark notification as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        try:
            notification = Notification.objects.get(id=id)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

class NotificationCreateView(APIView):
    """Create notification (admin/teacher only)"""
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ==================== FRONTEND VIEWS ====================

class LandingPageView(TemplateView):
    template_name = "index.html"

class LoginPageView(TemplateView):
    template_name = "login.html"

class AdminDashboardTemplateView(TemplateView):
    template_name = "dashboard/admin.html"

class TeacherDashboardTemplateView(TemplateView):
    template_name = "dashboard/teacher.html"

class StudentDashboardTemplateView(TemplateView):
    template_name = "dashboard/student.html"

class DemoPageView(TemplateView):
    template_name = "demo.html"

class ParentDashboardTemplateView(TemplateView):
    template_name = "dashboard/parent.html"

class DeveloperProfileView(TemplateView):
    template_name = "developer.html"

class ResumeView(TemplateView):
    template_name = "resume.html"

# ==================== NEW MODULE API VIEWS ====================

from rest_framework import generics
from .Serializer import (
    LibraryBookSerializer, BookIssueSerializer, 
    HostelSerializer, RoomSerializer, HostelAllocationSerializer,
    VehicleSerializer, RouteSerializer, TransportAllocationSerializer,
    EmployeeSerializer, LeaveRequestSerializer, DepartmentSerializer, DesignationSerializer,
    ExamSerializer, EventSerializer
)
from .models import (
    LibraryBook, BookIssue, Hostel, Room, HostelAllocation,
    Vehicle, Route, TransportAllocation, Employee, LeaveRequest, Department, Designation,
    Exam, Event
)

# --- LIBRARY ---
class LibraryBookListCreateView(generics.ListCreateAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated]

class LibraryBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated]

class BookIssueListCreateView(generics.ListCreateAPIView):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]

# --- HOSTEL ---
class HostelListCreateView(generics.ListCreateAPIView):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [IsAuthenticated]

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

class HostelAllocationListCreateView(generics.ListCreateAPIView):
    queryset = HostelAllocation.objects.all()
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsAuthenticated]

# --- TRANSPORT ---
class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

# --- HR ---
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Employee.objects.all()
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'CLIENT':
                qs = qs.filter(created_by=self.request.user)
            elif hasattr(self.request.user, 'employee_profile') and self.request.user.employee_profile.created_by:
                qs = qs.filter(created_by=self.request.user.employee_profile.created_by)
            else:
                 return Employee.objects.none()
        return qs

    def perform_create(self, serializer):
        owner = None
        user = self.request.user
        if not user.is_superuser:
             if hasattr(user, 'profile') and user.profile.role == 'CLIENT':
                  owner = user
             elif hasattr(user, 'employee_profile'):
                  owner = user.employee_profile.created_by
        
        if owner:
            serializer.save(created_by=owner)
        else:
            serializer.save()

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

# --- EXAMS ---
class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Exam.objects.all()
        batch_id = self.request.query_params.get('batch_id')
        grade = self.request.query_params.get('grade')

        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        if grade:
            # Assuming input is just "10", but DB has "Class 10" or similar.
            # Or we can exact match if frontend sends "Class 10"
            queryset = queryset.filter(grade_class__icontains=grade)
        return queryset

# --- EVENTS ---
class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]



# ==================== DEMO REQUEST VIEW ====================

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .demo_serializers import DemoRequestSerializer
from .models import DemoRequest


class DemoRequestView(generics.CreateAPIView):
    """
    API endpoint for submitting demo requests
    Public endpoint (no authentication required)
    Automatically sends WhatsApp and SMS notifications to admin
    """
    queryset = DemoRequest.objects.all()
    serializer_class = DemoRequestSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Thank you for your interest! We will contact you shortly.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

# ==================== COACHING/COURSE MANAGEMENT VIEWS ====================

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
