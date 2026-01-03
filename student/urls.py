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
    DemoRequestView,
    DeveloperProfileView,
    ResumeView,
    # New Views
    LibraryBookListCreateView, LibraryBookDetailView, BookIssueListCreateView,
    HostelListCreateView, RoomListCreateView, HostelAllocationListCreateView,
    VehicleListCreateView, RouteListCreateView,
    EmployeeListCreateView, LeaveRequestListCreateView,
    ExamListCreateView, EventListCreateView,
    CourseListCreateView, CourseDetailView, BatchListCreateView, EnrollmentListCreateView
)
from .onboarding_views import OnboardingPaymentView
from .payment_gateway_views import CreateOrderView

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
    
    # DEMO REQUEST
    path('demo-request/', DemoRequestView.as_view(), name='demo-request'),
    
    # DEVELOPER PROFILE
    path('developer/', DeveloperProfileView.as_view(), name='developer-profile'),
    path('resume/', ResumeView.as_view(), name='resume-view'),

    # ==================== NEW MODULE URLS ====================
    # LIBRARY
    path('library/books/', LibraryBookListCreateView.as_view(), name='library-books'),
    path('library/books/<int:pk>/', LibraryBookDetailView.as_view(), name='library-book-detail'),
    path('library/issues/', BookIssueListCreateView.as_view(), name='library-issues'),

    # HOSTEL
    path('hostel/', HostelListCreateView.as_view(), name='hostel-list'),
    path('hostel/rooms/', RoomListCreateView.as_view(), name='hostel-rooms'),
    path('hostel/allocations/', HostelAllocationListCreateView.as_view(), name='hostel-allocations'),

    # TRANSPORT
    path('transport/vehicles/', VehicleListCreateView.as_view(), name='transport-vehicles'),
    path('transport/routes/', RouteListCreateView.as_view(), name='transport-routes'),

    # HR
    path('hr/employees/', EmployeeListCreateView.as_view(), name='hr-employees'),
    path('hr/leaves/', LeaveRequestListCreateView.as_view(), name='hr-leaves'),

    # EXAMS
    path('exams/', ExamListCreateView.as_view(), name='exam-list'),

    # EVENTS
    path('events/', EventListCreateView.as_view(), name='event-list'),

    # COACHING
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('batches/', BatchListCreateView.as_view(), name='batch-list'),
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    
    # ONBOARDING
    path('onboarding/pay/', OnboardingPaymentView.as_view(), name='onboarding-pay'),
    # RAZORPAY
    path('payment/create-order/', CreateOrderView.as_view(), name='payment-create-order'),
]
