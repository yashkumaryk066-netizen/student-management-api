from django.urls import path
from .views import (
    StudentListCreateView,
    StudentDetailsView,
    StudentTodayView,
    AttendenceCreateView,
    AttendenceDetailsView,
    ProfileView,
    StudentDashboardView,
    TeacherDashboardView,
    ParentDashboardView,
    PaymentListCreateView,
    PaymentDetailsView,
    NotificationListView,
    NotificationMarkReadView,
    NotificationCreateView,
    LandingPageView,
    LoginPageView,
    AdminDashboardTemplateView,
    TeacherDashboardTemplateView,
    StudentDashboardTemplateView,
    ParentDashboardTemplateView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    #STUDENTS
    path("students/", StudentListCreateView.as_view(), name="student-create-list"),
    path("students/<int:id>/", StudentDetailsView.as_view(), name="student-details"),
    path("students/today/", StudentTodayView.as_view(), name="student-today"),
    #ATTENDENCE 
    path("attendence/", AttendenceCreateView.as_view(), name="attendance-create-list"),
    path("attendence/<int:id>/", AttendenceDetailsView.as_view(), name="attendence-details"),
    #AUTH (JWT)
    path("auth/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    #PROFILE
    path("profile/", ProfileView.as_view(), name="profile"),
    
    # ROLE-BASED DASHBOARDS
    path("dashboard/student/", StudentDashboardView.as_view(), name="student-dashboard"),
    path("dashboard/teacher/", TeacherDashboardView.as_view(), name="teacher-dashboard"),
    path("dashboard/parent/", ParentDashboardView.as_view(), name="parent-dashboard"),
    
    # PAYMENTS
    path("payments/", PaymentListCreateView.as_view(), name="payment-list-create"),
    path("payments/<int:id>/", PaymentDetailsView.as_view(), name="payment-details"),
    
    # NOTIFICATIONS
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:id>/read/", NotificationMarkReadView.as_view(), name="notification-read"),
    path("notifications/create/", NotificationCreateView.as_view(), name="notification-create"),
]

# Demo Request
path('demo-request/', DemoRequestView.as_view(), name='demo-request'),
