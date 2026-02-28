from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from student.models import Student, Payment, Course, Batch, Exam, Attendence
from .base import filter_by_owner, get_owner_user

# TEMPLATE VIEWS

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

# DASHBOARD API VIEWS

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
            'total_revenue': Payment.objects.filter(user=owner, status='APPROVED').aggregate(total=Sum('amount'))['total'] or 0,
            'recent_payments': Payment.objects.filter(user=owner).order_by('-created_at')[:5].values('amount', 'status', 'created_at'),
            'attendance_today': int(Attendence.objects.filter(student__created_by=owner, date=timezone.now().date(), is_present=True).count()),
        }
        
        # --- ENHANCED PLAN SPECIFIC DATA ---
        
        if plan in ['COACHING', 'INSTITUTE']:
            stats['courses_count'] = Course.objects.filter(created_by=owner).count()
            stats['batches_count'] = Batch.objects.filter(created_by=owner).count()
            
        if plan in ['SCHOOL', 'INSTITUTE']:
            # Real teacher count (assuming staff role)
            from django.contrib.auth.models import User
            stats['teachers_count'] = UserProfile.objects.filter(owner=owner, role='TEACHER').count()
            stats['exams_count'] = Exam.objects.filter(created_by=owner).count()
            
            # Real Attendance Percentage
            total_students = stats['students_count']
            if total_students > 0:
                stats['attendance_percentage'] = int((stats['attendance_today'] / total_students) * 100)
            else:
                stats['attendance_percentage'] = 0
            
        if plan == 'INSTITUTE':
            # Real Facility Stats
            from student.models import HostelAllocation
            from student.models import Vehicle
            stats['hostel_occupancy'] = HostelAllocation.objects.filter(student__created_by=owner, status='ACTIVE').count()
            stats['transport_routes'] = Vehicle.objects.filter(created_by=owner).count()
            
        return Response(stats)
