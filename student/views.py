from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from datetime import date, timedelta

from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Course, Batch, Enrollment, LiveClass,
    LibraryBook, BookIssue, Hostel, Room, HostelAllocation,
    Vehicle, Route, TransportAllocation,
    Employee, LeaveRequest, Department, Designation,
    Exam, Event, DemoRequest, ClientSubscription
)

from .Serializer import *
from .permissions import *


# =====================================================
# COMMON HELPERS (SAAS ISOLATION)
# =====================================================

def get_owner_user(user):
    if user.is_superuser:
        return None
    if hasattr(user, 'profile') and user.profile.role == 'CLIENT':
        return user
    if hasattr(user, 'employee_profile'):
        return user.employee_profile.created_by
    return None


def filter_by_owner(qs, user):
    owner = get_owner_user(user)
    if owner:
        return qs.filter(created_by=owner)
    return qs


# =====================================================
# STUDENT LIST / CREATE
# =====================================================

class StudentListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin, StudentLimitPermission]
    required_feature = 'students'

    def get(self, request):
        students = Student.objects.all()
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
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            owner = get_owner_user(request.user)
            serializer.save(created_by=owner)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# =====================================================
# STUDENT DETAILS
# =====================================================

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


# =====================================================
# TODAY ATTENDANCE (FIXED – NO DATA LEAK)
# =====================================================

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


# =====================================================
# ATTENDANCE CREATE
# =====================================================

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

            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AttendenceDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_object(self, id):
        return Attendence.objects.filter(id=id).first()

    def get(self, request, id):
        attendance = self.get_object(id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        return Response(AttendenceSerializer(attendance).data)
    
    def put(self, request, id):
        attendance = self.get_object(id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        serializer = AttendenceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, id):
        attendance = self.get_object(id)
        if not attendance:
            return Response({"error": "Not found"}, status=404)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# =====================================================
# PAYMENTS (FIXED OWNERSHIP)
# =====================================================

class PaymentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Payment.objects.all()

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


# =====================================================
# NOTIFICATIONS (FIXED SECURITY)
# =====================================================

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


# =====================================================
# LIVE CLASSES (PLACEHOLDER REMOVED)
# =====================================================

class LiveClassListView(APIView):
    permission_classes = [IsAuthenticated, HasPlanAccess]
    required_feature = 'coaching_classes'

    def get(self, request):
        today = timezone.now().date()
        qs = LiveClass.objects.filter(start_time__date=today, is_active=True)

        if request.user.profile.role == 'TEACHER':
            qs = qs.filter(teacher=request.user)

        return Response(LiveClassSerializer(qs, many=True).data)


# =====================================================
# RESTORED MISSING VIEWS
# =====================================================

class ClientSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if hasattr(request.user, 'subscription'):
             return Response({
                 "plan": request.user.subscription.plan_type,
                 "status": request.user.subscription.status,
                 "valid_until": request.user.subscription.end_date
             })
        return Response({"status": "No Subscription"})

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

class LibraryBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryBook.objects.all()
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

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

class TransportAllocationListCreateView(generics.ListCreateAPIView):
    queryset = TransportAllocation.objects.all()
    serializer_class = TransportAllocationSerializer
    permission_classes = [IsAuthenticated]

# --- HR ---
class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminUser]

    def get_queryset(self):
         return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        serializer.save(created_by=owner)

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

# --- ACADEMIC / EXAMS ---
class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

# --- COACHING ---
class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

class LiveClassListCreateView(generics.ListCreateAPIView):
    queryset = LiveClass.objects.all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
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
             data.update(UserProfileSerializer(user.profile).data)
        return Response(data)

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

# =====================================================
# FRONTEND TEMPLATES (UNCHANGED)
# =====================================================

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
