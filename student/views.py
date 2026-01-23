from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from datetime import date, timedelta

from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Course, Batch, Enrollment, LiveClass,
    LibraryBook, BookIssue, Hostel, Room, HostelAllocation,
    Vehicle, Route, TransportAllocation,
    Employee, LeaveRequest, Department, Designation,
    Exam, Event, DemoRequest, ClientSubscription, AuditLog
)

from .Serializer import *
from .permissions import *


# COMMON HELPERS (SAAS ISOLATION)

def get_owner_user(user):
    """
    Get the owner user for data filtering (multi-tenancy isolation)
    Returns the user who 'owns' the data being accessed
    """
    # Super admin: return special marker to filter their own data separately
    if user.is_superuser:
        return user  # Super admin sees only their own created data
    
    # CLIENT or ADMIN role: they are the owner of their data
    if hasattr(user, 'profile') and user.profile.role in ['CLIENT', 'ADMIN']:
        return user
    
    # Teacher/Staff: find their client/owner
    if hasattr(user, 'employee_profile'):
        return user.employee_profile.created_by
    
    # Parent/Student: should see data from their associated client
    if hasattr(user, 'profile') and user.profile.role in ['PARENT', 'STUDENT']:
        return getattr(user.profile, 'created_by', user)
    
    return user


def filter_by_owner(qs, user):
    """
    Filter queryset to show only data owned by the current user
    CRITICAL: Ensures complete data isolation between clients and super admin
    """
    owner = get_owner_user(user)
    if owner:
        # Filter by created_by to show only this owner's data
        return qs.filter(created_by=owner)
    
    # Fallback: return empty queryset for safety
    return qs.none()


# STUDENT LIST / CREATE

class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin, StudentLimitPermission]
    required_feature = 'students'

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

# ... [Skipping unchanged lines] ...

class BookIssueListCreateView(generics.ListCreateAPIView):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('book', 'student'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# ... [Skipping unchanged lines] ...

class HostelAllocationListCreateView(generics.ListCreateAPIView):
    queryset = HostelAllocation.objects.all()
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('student', 'room__hostel'),
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# ... [Skipping unchanged lines] ...

class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('vehicle'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class TransportAllocationListCreateView(generics.ListCreateAPIView):
    queryset = TransportAllocation.objects.all()
    serializer_class = TransportAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('student', 'route'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# ... [Skipping unchanged lines] ...

class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('subject', 'batch'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            owner = get_owner_user(request.user)
            
            # CHECK APPROVAL LOGIC
            # If the creator (request.user) is NOT the owner (Client Admin),
            # then it's a staff member creating a student -> REQUIRE APPROVAL.
            is_approved = True
            msg = "Student created successfully"
            
            if request.user != owner:
                is_approved = False
                msg = "Student request submitted for Admin Verification"

            student = serializer.save(created_by=owner, is_approved=is_approved)
            
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
            
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)


# STUDENT DETAILS

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


# SYSTEM LOGS / AUDIT (CLIENT LEVEL)

class ClientAuditLogListView(APIView):
    permission_classes = [IsAuthenticated, HasPlanAccess]
    required_feature = 'logs'

    def get(self, request):
        owner = get_owner_user(request.user)
        # Show logs for the owner and their staff
        logs = AuditLog.objects.filter(
            Q(created_by=owner) | 
            Q(created_by__employee_profile__created_by=owner)
        ).order_by('-created_at')[:100]
        
        return Response(AuditLogSerializer(logs, many=True).data)


# TEAM MANAGEMENT (STAFF/TEACHERS)

class TeamManagementView(APIView):
    permission_classes = [IsAuthenticated, HasPlanAccess]
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


# TODAY ATTENDANCE (FIXED – NO DATA LEAK)

class StudentTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        students = filter_by_owner(Student.objects.all(), request.user)

        attendance = Attendence.objects.filter(student__in=students, date=today)

        present = attendance.filter(is_present=True)
        absent = attendance.filter(is_present=False)

        return Response({
            "date": str(today),
            "total_students": students.count(),
            "present_count": present.count(),
            "absent_count": absent.count(),
            "present_students": StudentSerializer(
                [a.student for a in present], many=True
            ).data,
            "absent_students": StudentSerializer(
                [a.student for a in absent], many=True
            ).data
        })


# ATTENDANCE CREATE

class AttendenceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request):
        serializer = AttendenceSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
            if not filter_by_owner(Student.objects.filter(id=student.id), request.user).exists():
                return Response({"error": "Permission denied"}, status=403)

            if Attendence.objects.filter(
                student=student,
                date=serializer.validated_data.get('date', date.today())
            ).exists():
                return Response({"error": "Already marked"}, status=400)

            owner = get_owner_user(request.user)
            serializer.save(created_by=owner)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AttendenceDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_object(self, user, id):
        qs = Attendence.objects.filter(id=id)
        return filter_by_owner(qs, user).first()

    def get(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        return Response(AttendenceSerializer(attendance).data)
    
    def put(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        serializer = AttendenceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
            return Response({"error": "Not found"}, status=404)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# PAYMENTS (FIXED OWNERSHIP)

class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Optimize with select_related to prevent N+1 queries
        qs = Payment.objects.select_related('student', 'student__parent', 'user').all()

        if request.user.profile.role == 'PARENT':
            qs = qs.filter(student__parent=request.user)
        elif request.user.profile.role == 'STUDENT':
            qs = qs.filter(student__user=request.user)
        else:
            qs = filter_by_owner(qs, request.user)

        return Response(PaymentSerializer(qs, many=True).data)


class PaymentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        qs = Payment.objects.filter(id=id)
        qs = filter_by_owner(qs, request.user)
        payment = qs.first()

        if not payment:
            return Response({"error": "Payment not found"}, status=404)

        return Response(PaymentSerializer(payment).data)


# NOTIFICATIONS (FIXED SECURITY)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.profile.role
        qs = Notification.objects.filter(
            Q(recipient=request.user) |
            Q(recipient_type=role) |
            Q(recipient_type='ALL')
        )
        return Response(NotificationSerializer(qs, many=True).data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        notification = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='ALL'),
            id=id
        ).first()

        if not notification:
            return Response({"error": "Not found"}, status=404)

        notification.is_read = True
        notification.save()
        return Response({"message": "Marked as read"})


# LIVE CLASSES (PLACEHOLDER REMOVED)

class LiveClassListView(APIView):
    permission_classes = [IsAuthenticated, HasPlanAccess]
    required_feature = 'live_classes'

    def get(self, request):
        today = timezone.now().date()
        qs = LiveClass.objects.filter(start_time__date=today, is_active=True)
        qs = filter_by_owner(qs, request.user) # SaaS Isolation

        if request.user.profile.role == 'TEACHER':
            qs = qs.filter(teacher=request.user)

        data = LiveClassSerializer(qs, many=True).data
        if not data:
            return Response({"code": "NO_LIVE_CLASSES", "message": "No active classes found"}, status=200)

        return Response(data)


# RESTORED MISSING VIEWS

class ClientSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        # Auto-create subscription if missing (Advance Level User Experience)
        if not hasattr(request.user, 'subscription'):
            try:
                from .models import ClientSubscription
                from datetime import date
                # Create an EXPIRED 'COACHING' subscription to minimize access risk
                ClientSubscription.objects.create(
                    user=request.user,
                    plan_type='COACHING', # Corrected from INSTITUTE to COACHING
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
         # logic to redirect to payment or generate order
         return Response({"message": "Renewal initiated"})

# --- LIBRARY ---
class LibraryBookListCreateView(generics.ListCreateAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LibraryBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

class BookIssueListCreateView(generics.ListCreateAPIView):
    queryset = BookIssue.objects.all()
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- HOSTEL ---
class HostelListCreateView(generics.ListCreateAPIView):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class HostelAllocationListCreateView(generics.ListCreateAPIView):
    queryset = HostelAllocation.objects.all()
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- TRANSPORT ---
class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class TransportAllocationListCreateView(generics.ListCreateAPIView):
    queryset = TransportAllocation.objects.select_related('student', 'route', 'vehicle').all()
    serializer_class = TransportAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- HR ---
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.select_related('user', 'user__profile', 'department', 'designation').all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
         return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        serializer.save(created_by=owner)

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.select_related('employee', 'employee__user', 'approved_by').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- ACADEMIC / EXAMS ---
class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.select_related('course').prefetch_related('students').all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.prefetch_related('participants').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- COACHING ---
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.select_related('department').prefetch_related('batches').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.select_related('department').prefetch_related('batches').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.select_related('course').prefetch_related('enrollments', 'enrollments__student').all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.select_related('student', 'student__user', 'batch', 'batch__course').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LiveClassListCreateView(generics.ListCreateAPIView):
    queryset = LiveClass.objects.select_related('course', 'teacher', 'teacher__user').all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        from .plan_permissions import get_user_features
        
        user = request.user
        data = {
            "username": user.username,
            "email": user.email,
            "role": user.profile.role if hasattr(user, 'profile') else 'UNKNOWN',
            "id": user.id,
            "is_superuser": user.is_superuser,
            "user_full_name": user.get_full_name(),
            "available_features": list(get_user_features(user).keys())
        }
        if hasattr(user, 'profile'):
             profile_data = UserProfileSerializer(user.profile).data
             # Ensure full URLs for images
             if user.profile.institution_logo:
                 profile_data['institution_logo'] = request.build_absolute_uri(user.profile.institution_logo.url)
             if user.profile.digital_signature:
                 profile_data['digital_signature'] = request.build_absolute_uri(user.profile.digital_signature.url)
             data.update(profile_data)
             
        return Response(data)
    
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
        """Partial update - same as PUT for now"""
        return self.put(request)

class NotificationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"stats": "Student stats placeholder"})

class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"stats": "Teacher stats placeholder"})

class ParentDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"stats": "Parent stats placeholder"})

class InvoiceDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
            # Security: Allow if superuser or if the payment belongs to the user
            if not request.user.is_superuser and payment.user != request.user:
                return Response({"error": "Permission denied"}, status=403)
            
            sub = ClientSubscription.objects.filter(user=payment.user).first()
            if not sub:
                return Response({"error": "Subscription not found"}, status=404)
                
            from .services.invoice_service import generate_invoice_pdf
            pdf_buffer = generate_invoice_pdf(payment.user, sub, payment)
            
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{payment.id}.pdf"'
            return response
        except Payment.DoesNotExist:
             return Response({"error": "Payment not found"}, status=404)
        except Exception as e:
             return Response({"error": str(e)}, status=500)

class DemoRequestView(APIView):
    permission_classes = [permissions.AllowAny] 
    
    def post(self, request):
        data = request.data
        try:
            demo = DemoRequest.objects.create(
                name=data.get('name'),
                phone=data.get('phone'),
                email=data.get('email'),
                institution_name=data.get('institution_name', ''),
                institution_type=data.get('institution_type', ''),
                message=data.get('message', '')
            )
            return Response({"message": "Demo request submitted successfully", "id": demo.id}, status=201)
        except Exception as e:
             return Response({"error": str(e)}, status=400)

# FRONTEND TEMPLATES (UNCHANGED)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LandingPageView(TemplateView):
    """Landing page with CSRF cookie enabled for payment forms"""
    template_name = "index.html"

class LoginPageView(TemplateView):
    template_name = "login.html"

class AdminDashboardTemplateView(TemplateView):
    template_name = "dashboard/admin.html"

class SuperAdminDashboardTemplateView(TemplateView):
    template_name = "dashboard/super_admin.html"

class TeacherDashboardTemplateView(TemplateView):
    template_name = "dashboard/teacher.html"

class StudentDashboardTemplateView(TemplateView):
    template_name = "dashboard/student.html"

class ParentDashboardTemplateView(TemplateView):
    template_name = "dashboard/parent.html"

class DemoPageView(TemplateView):
    template_name = "demo.html"

class DeveloperProfileView(TemplateView):
    template_name = "developer.html"

class ResumeView(TemplateView):
    template_name = "resume.html"

class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
# PREMIUM DASHBOARD API
class DashboardStatsView(APIView):
    """
    Returns Plan-Specific Statistics for the Dashboard.
    Filters data visibility based on User's Plan (Coaching/School/Institute).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        owner = get_owner_user(user)
        
        # Get Plan
        plan = 'SCHOOL' # Default
        if hasattr(user, 'profile'):
            plan = user.profile.institution_type
            
        stats = {
            'plan': plan,
            'students_count': Student.objects.filter(created_by=owner).count(),
            'recent_payments': Payment.objects.filter(user=owner).order_by('-created_at')[:5].values('amount', 'status', 'created_at'),
        }
        
        # --- PLAN SPECIFIC DATA ---
        
        # 1. COACHING PLAN Focus
        if plan in ['COACHING', 'INSTITUTE']:
            stats['courses_count'] = Course.objects.filter(created_by=owner).count()
            stats['batches_count'] = Batch.objects.filter(created_by=owner).count()
            
        # 2. SCHOOL/INSTITUTE Focus
        if plan in ['SCHOOL', 'INSTITUTE']:
            stats['teachers_count'] = 0 # Placeholder if teacher model exists
            stats['exams_count'] = Exam.objects.filter(created_by=owner).count()
            
            # Attendance Stats (Today)
            today = timezone.now().date()
            present_count = Attendence.objects.filter(student__created_by=owner, date=today, is_present=True).count()
            total_students = stats['students_count']
            stats['attendance_percentage'] = int((present_count / total_students * 100)) if total_students > 0 else 0
            
        # 3. EXTRA MODULES (Institute Only)
        if plan == 'INSTITUTE':
            stats['hostel_occupancy'] = 0 # Placeholder
            stats['transport_routes'] = 0 # Placeholder
            
        return Response(stats)

# PREMIUM REPORT GENERATION (Advance Level)
from .report_utils import generate_admit_card_pdf, generate_report_card_pdf
from .id_card_utils import generate_id_card_pdf

class GenerateAdmitCardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    required_feature = 'exams'

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            # Ensure owner isolation
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Permission Denied"}, status=403)
                
            exam_name = request.query_params.get('exam', 'Final Examination 2024')
            
            pdf = generate_admit_card_pdf(student, exam_name, '2025-03-15', 'Main Hall, Block A')
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="AdmitCard_{student.name}.pdf"'
            return response
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

class GenerateReportCardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    required_feature = 'exams'

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            # Ensure owner isolation
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Permission Denied"}, status=403)
            
            # Mock Data for now (In real app, fetch from ExamResult model)
            results = [
                {'subject': 'Mathematics', 'total': 100, 'marks': 95},
                {'subject': 'Physics', 'total': 100, 'marks': 88},
                {'subject': 'Chemistry', 'total': 100, 'marks': 92},
                {'subject': 'English', 'total': 100, 'marks': 85},
                {'subject': 'Computer Science', 'total': 100, 'marks': 98},
            ]
            
            pdf = generate_report_card_pdf(student, results)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ReportCard_{student.name}.pdf"'
            return response
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

class GenerateIDCardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    required_feature = 'id_cards'

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            # Ensure owner isolation
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Permission Denied"}, status=403)

            pdf = generate_id_card_pdf(student)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="IDCard_{student.name}.pdf"'
            return response
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)



# PWA SERVICE WORKER VIEW - PREMIUM AUTO-UPDATE VERSION
def service_worker(request):
    js_content = """
const VERSION = 'v3.0.0';
const CACHE_NAME = `ysm-ai-${VERSION}`;
const RUNTIME_CACHE = `ysm-runtime-${VERSION}`;

// Core assets to cache immediately
const CORE_ASSETS = [
  '/ai-chat/',
  '/static/manifest.json',
  '/static/assets/ysm_icon.png',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// Install - cache core assets
self.addEventListener('install', event => {
  console.log(`[SW] Installing ${VERSION}`);
  self.skipWaiting(); // Force activation
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(CORE_ASSETS))
      .catch(err => console.log('[SW] Cache install error:', err))
  );
});

// Activate - clean old caches & notify clients
self.addEventListener('activate', event => {
  console.log(`[SW] Activating ${VERSION}`);
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all([
        // Delete old caches
        ...keys.filter(key => key !== CACHE_NAME && key !== RUNTIME_CACHE)
             .map(key => caches.delete(key)),
        // Claim all clients
        self.clients.claim()
      ]);
    }).then(() => {
      // Notify all clients about update
      return self.clients.matchAll().then(clients => {
        clients.forEach(client => {
          client.postMessage({
            type: 'APP_UPDATE',
            version: VERSION,
            message: 'App updated to ' + VERSION
          });
        });
      });
    })
  );
});

// Fetch - Network first for API, Cache first for static
self.addEventListener('fetch', event => {
  const { request } = event;
  
  // Skip non-GET requests
  if (request.method !== 'GET') return;
  
  // For API calls - always try network first
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request).then(cached => {
            if (cached) return cached;
            // Return offline fallback
            return new Response(
              JSON.stringify({ error: 'Offline', cached: false }),
              { headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }
  
  // For static assets - cache first
  event.respondWith(
    caches.match(request)
      .then(cached => {
        if (cached) return cached;
        
        return fetch(request).then(response => {
          if (response && response.status === 200) {
            const responseClone = response.clone();
            caches.open(RUNTIME_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
      .catch(err => {
        console.log('[SW] Fetch failed:', request.url);
      })
  );
});

// Background sync for offline messages
self.addEventListener('sync', event => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});

async function syncMessages() {
  console.log('[SW] Syncing offline messages...');
}

// Push notifications (future)
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.body || 'New update available',
    icon: '/static/assets/ysm_icon.png',
    badge: '/static/assets/ysm_icon.png',
    vibrate: [200, 100, 200]
  };
  event.waitUntil(
    self.registration.showNotification(data.title || 'Y.S.M AI', options)
  );
});
"""
    return HttpResponse(js_content, content_type="application/javascript")

# SEO Views
def robots_txt(request):
    base_url = request.build_absolute_uri('/')
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /dashboard/",
        "Disallow: /api/",
        "Allow: /",
        f"Sitemap: {base_url}sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    base_url = request.build_absolute_uri('/')
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{base_url}</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>

  <url>
    <loc>{base_url}ai-chat/</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{base_url}developer/</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{base_url}resume/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{base_url}demo/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>{base_url}login/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
    return HttpResponse(xml, content_type="application/xml")

def google_verification(request):
    return HttpResponse("google-site-verification: google7ec15807e3134773.html", content_type="text/plain")



# GLOBAL SEARCH
# =========================

class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response([])

        user = request.user
        results = []

        # 1. Search Students
        students = Student.objects.select_related('parent').filter(
            Q(name__icontains=query) | 
            Q(roll_number__icontains=query) |
            Q(parent__username__icontains=query)
        )
        # Apply Isolation
        students = filter_by_owner(students, user)[:5]
        
        for s in students:
            results.append({
                'type': 'Student',
                'title': s.name,
                'subtitle': f"Roll: {s.roll_number} | Class: {s.grade}",
                'url': f"#students/{s.id}",
                'icon': '👤'
            })

        # 2. Search Courses/Batches (Coaching/Institute)
        if hasattr(user, 'profile') and user.profile.institution_type != 'SCHOOL':
            courses = Course.objects.filter(name__icontains=query)
            courses = filter_by_owner(courses, user)[:3]
            for c in courses:
                results.append({
                    'type': 'Course',
                    'title': c.name,
                    'subtitle': f"Fee: ₹{c.fee}",
                    'url': f"#courses/{c.id}",
                    'icon': '📚'
                })

        # 3. Search Batches
        batches = Batch.objects.select_related('course').filter(name__icontains=query)
        batches = filter_by_owner(batches, user)[:3]
        for b in batches:
             results.append({
                'type': 'Batch',
                'title': b.name,
                'subtitle': f"Course: {b.course.name if b.course else 'N/A'}",
                'url': f"#batches",
                'icon': '👥'
            })
        
        return Response(results)

# =========================
# HOLIDAY CALENDAR API
# =========================
from .models import Holiday

class HolidayListCreateView(generics.ListCreateAPIView):
    serializer_class = None # We'll build response manually for speed or add serializer later
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Strict Isolation
        holidays = Holiday.objects.filter(owner=user.profile.get_owner() if hasattr(user, 'profile') else user)
        # Also include owner's own holidays (if user is owner)
        holidays |= Holiday.objects.filter(owner=user)
        
        holidays = holidays.distinct().order_by('date')
        
        data = [{
            'id': h.id,
            'title': h.name,
            'start': h.date,
            'end': h.end_date, 
            'type': h.type,
            'description': h.description,
            'className': f"holiday-{h.type.lower()}" # CSS class for fullcalendar
        } for h in holidays]
        
        return Response(data)

    def post(self, request):
        if not request.user.profile.is_admin_or_owner():
             return Response({"error": "Permission Denied"}, status=403)
             
        data = request.data
        Holiday.objects.create(
            owner=request.user,
            name=data.get('name'),
            date=data.get('date'),
            type=data.get('type', 'ACADEMIC'),
            description=data.get('description')
        )
        return Response({"message": "Holiday Created"}, status=201)

# =========================
# TIMETABLE API
# =========================
from .models import ClassRoutine, Batch

class RoutineListCreateView(generics.ListCreateAPIView):
    serializer_class = None 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        routines = ClassRoutine.objects.filter(owner=user.profile.get_owner() if hasattr(user, 'profile') else user)
        
        # Filter by specific context
        batch_id = request.query_params.get('batch_id')
        grade = request.query_params.get('grade')
        
        if batch_id:
            routines = routines.filter(batch_id=batch_id)
        if grade:
            routines = routines.filter(grade=grade)
            
        data = [{
            'id': r.id,
            'day': r.day_of_week,
            'subject': r.subject,
            'teacher': r.teacher_name,
            'start': r.start_time.strftime('%H:%M'),
            'end': r.end_time.strftime('%H:%M'),
            'room': r.room_number,
            'batch_name': r.batch.name if r.batch else (f"Class {r.grade}" if r.grade else "General")
        } for r in routines]
        
        return Response(data)

    def post(self, request):
        if not request.user.profile.is_admin_or_owner():
             return Response({"error": "Permission Denied"}, status=403)
             
        data = request.data
        b_id = data.get('batch_id')
        batch = Batch.objects.get(id=b_id) if b_id else None
        
        ClassRoutine.objects.create(
            owner=request.user,
            batch=batch,
            grade=data.get('grade'),
            subject=data.get('subject'),
            teacher_name=data.get('teacher'),
            day_of_week=data.get('day'),
            start_time=data.get('start'),
            end_time=data.get('end'),
            room_number=data.get('room')
        )
        return Response({"message": "Routine Added"}, status=201)


# =========================
# BULK IMPORT OPERATIONS
# =========================
import csv
import io

class BulkImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not request.user.profile.is_admin_or_owner():
            return Response({"error": "Permission Denied"}, status=403)

        file_obj = request.FILES.get('file')
        import_type = request.data.get('type')
        
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        # Basic CSV Parsing
        try:
            decoded_file = file_obj.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            count = 0
            errors = []
            
            for row in reader:
                try:
                    self._process_row(row, import_type, request.user)
                    count += 1
                except Exception as e:
                    errors.append(f"Row {count+1}: {str(e)}")
            
            return Response({
                "message": f"Successfully imported {count} records.",
                "errors": errors
            })
            
        except Exception as e:
            return Response({"error": f"Import failed: {str(e)}"}, status=500)

    def _process_row(self, row, type, user):
        # Helper to route to specific logic
        from .models import Student, LibraryBook, Employee
        
        if type == 'STUDENT':
            Student.objects.create(
                user=user, # Link to owner
                name=row.get('name'),
                phone=row.get('phone', ''),
                email=row.get('email', ''),
                address=row.get('address', '')
                # Add more fields as per CSV headers
            )
        elif type == 'BOOK':
             LibraryBook.objects.create(
                created_by=user,
                title=row.get('title'),
                author=row.get('author'),
                isbn=row.get('isbn', '0000000000'),
                total_copies=int(row.get('copies', 1)),
                price=0
             )
        elif type == 'STAFF':
            Employee.objects.create(
                user=user, # Temporarily link user as placeholder
                first_name=row.get('first_name'),
                last_name=row.get('last_name'),
                email=row.get('email'),
                phone=row.get('phone')
            )
        else:
            raise ValueError("Invalid Import Type")
