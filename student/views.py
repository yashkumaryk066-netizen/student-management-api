from rest_framework.views import APIView
from django.views.generic import TemplateView
from django.db.models import Q
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.response import Response
from .models import Student, Attendence, UserProfile, Payment, Notification
from .Serializer import StudentSerializer, AttendenceSerializer, UserProfileSerializer, PaymentSerializer, NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .permissions import IsStudent, IsTeacher, IsParent, IsAdminRole, IsTeacherOrAdmin
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
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def get(self, request):
        search = request.query_params.get("search","").strip()
        students = Student.objects.all()
        if search:
            students= students.filter(
                Q(name__icontains=search)|
                Q(gender__icontains=search)
            )
        if not students.exists():
            return Response(
                {"message": "Student does not exist"}, 
                status=status.HTTP_404_NOT_FOUND
            )
 
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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
        return Response({
            "username": request.user.username
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        return self.get(request)

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

class ParentDashboardTemplateView(TemplateView):
    template_name = "dashboard/parent.html"

