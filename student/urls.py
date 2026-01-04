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
    # New Views for Client Subscriptions
    ClientSubscriptionView, SubscriptionRenewalView,
    # New Module Views
    LibraryBookListCreateView, LibraryBookDetailView, BookIssueListCreateView,
    HostelListCreateView, RoomListCreateView, HostelAllocationListCreateView,
    VehicleListCreateView, RouteListCreateView, TransportAllocationListCreateView,
    EmployeeListCreateView, LeaveRequestListCreateView,
    ExamListCreateView, EventListCreateView,
    CourseListCreateView, CourseDetailView, BatchListCreateView, EnrollmentListCreateView, InvoiceDownloadView,
    LiveClassListCreateView
)
from .eazypay_views import InitEazypayPaymentView, EazypayCallbackView
from .manual_payment_views import ManualPaymentSubmitView

# Remove invalid imports - these are now part of views.py or no longer needed
from .admin_dashboard_views import (
    AdminPaymentApprovalView, PendingPaymentsListView, PublicSubscriptionSubmitView,
    SuperAdminClientActionView, SuperAdminDashboardView
)
from .super_admin_views import SuperAdminAdvancedDashboardView, AuditLogView
from .subscription_views import (
    SubscriptionPurchaseView, SubscriptionStatusView, SubscriptionRenewView,
    verify_payment_api
)
from .plan_features_views import UserPlanFeaturesView
from .report_views import ReportListView, ReportDownloadView
from .onboarding_views import OnboardingPaymentView
from .payment_gateway_views import CreateOrderView
from .password_reset_views import RequestPasswordResetView, VerifyAndResetPasswordView

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
    
    # PLAN FEATURES (Check user's plan access)
    path("plan/features/", UserPlanFeaturesView.as_view(), name="plan-features"),
    
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
    
    # LIVE CLASSES
    path('live-classes/', LiveClassListCreateView.as_view(), name='live-classes'),

    # COACHING
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('batches/', BatchListCreateView.as_view(), name='batch-list'),
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    
    # ONBOARDING
    path('onboarding/pay/', OnboardingPaymentView.as_view(), name='onboarding-pay'),
    # RAZORPAY
    path('payment/create-order/', CreateOrderView.as_view(), name='payment-create-order'),
    
    # PASSWORD RESET
    path('auth/password-reset/request/', RequestPasswordResetView.as_view(), name='password-reset-request'),
    path('auth/password-reset/confirm/', VerifyAndResetPasswordView.as_view(), name='password-reset-confirm'),

    # EAZYPAY
    path('payment/eazypay/init/', InitEazypayPaymentView.as_view(), name='payment-eazypay-init'),
    path('payment/eazypay/callback/', EazypayCallbackView.as_view(), name='payment-eazypay-callback'),
    
    # MANUAL PAYMENT
    path('payment/manual/submit/', ManualPaymentSubmitView.as_view(), name='payment-manual-submit'),
    
    # SUBSCRIPTION (MANUAL BANK TRANSFER)
    path('subscription/status/', ClientSubscriptionView.as_view(), name='subscription-status'),
    path('subscription/renew/', SubscriptionRenewalView.as_view(), name='subscription-renew'),
    path('subscription/submit/', PublicSubscriptionSubmitView.as_view(), name='subscription-submit-public'),
    
    # Old/Unused - Commenting out to avoid import errors
    # path('subscription/buy/', SubscriptionPurchaseView.as_view(), name='subscription-buy'),  
    # path('subscription/verify-payment/', verify_payment_api, name='subscription-verify-payment'),
    # path('admin/payments/pending/', PendingPaymentsListView.as_view(), name='admin-pending-payments'),
    # path('admin/payments/approve/', AdminPaymentApprovalView.as_view(), name='admin-approve-payment'),
    
    # ADMIN PAYMENT VERIFICATION
    path('admin/payments/pending/', PendingPaymentsListView.as_view(), name='admin-pending-payments'),
    path('admin/payments/approve/', AdminPaymentApprovalView.as_view(), name='admin-approve-payment'),
    
    # SUPER ADMIN DASHBOARD
    path('admin/subscriptions/overview/', SuperAdminDashboardView.as_view(), name='superadmin-overview'),
    path('admin/client-actions/', SuperAdminClientActionView.as_view(), name='admin-client-actions'),
    path('admin/advanced/dashboard/', SuperAdminAdvancedDashboardView.as_view(), name='superadmin-advanced-dashboard'),
    path('admin/audit-logs/', AuditLogView.as_view(), name='admin-audit-logs'),

    # REPORTS
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/download/<int:pk>/', ReportDownloadView.as_view(), name='report-download'),
    
    # Invoice
    path('invoice/<int:payment_id>/download/', InvoiceDownloadView.as_view(), name='invoice-download'),
]
