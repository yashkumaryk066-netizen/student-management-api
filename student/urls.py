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
    # New Views for Client Subscriptions (Moved to subscription_views)
    # ClientSubscriptionView, SubscriptionRenewalView, RenewalSubmissionView,
    # New Module Views
    LibraryBookListCreateView, LibraryBookDetailView, BookIssueListCreateView,
    HostelListCreateView, RoomListCreateView, HostelAllocationListCreateView,
    VehicleListCreateView, RouteListCreateView, TransportAllocationListCreateView,
    EmployeeListCreateView, LeaveRequestListCreateView,
    ExamListCreateView, EventListCreateView,
    CourseListCreateView, CourseDetailView, BatchListCreateView, EnrollmentListCreateView, InvoiceDownloadView,
    LiveClassListCreateView, DepartmentListCreateView,
    ClientAuditLogListView, DashboardStatsView,
    GenerateIDCardView, GenerateAdmitCardView, GenerateReportCardView,
    GlobalSearchView, HolidayListCreateView, RoutineListCreateView, BulkImportView
)
from .report_views import ReportListView, ReportDownloadView
from .subscription_views import ClientSubscriptionView, SubscriptionRenewalView, RenewalSubmissionView
from .student_portal_views import (
    StudentMyResultView, 
    StudentDownloadReportCardView, 
    StudentDownloadAdmitCardView
)
from .attendance_geo_views import GeoFencedAttendanceView
from .team_views import TeamManagementView
from .eazypay_views import InitEazypayPaymentView, EazypayCallbackView
from .manual_payment_views import ManualPaymentSubmitView

from .admin_dashboard_views import (
    AdminPaymentApprovalView, PendingPaymentsListView, PublicSubscriptionSubmitView,
    SuperAdminClientActionView, SuperAdminDashboardView
)
from .super_admin_views import SuperAdminAdvancedDashboardView, AuditLogView, AdminApprovalActionView
from .services.invoice_service import generate_invoice_pdf
from .services.email_service import send_credentials_with_invoice
# Removed unused legacy imports
from .report_views import ReportListView, ReportDownloadView
from .plan_features_views import UserPlanFeaturesView
from .onboarding_views import OnboardingPaymentView, OnboardingBulkImportView
from .payment_gateway_views import CreateOrderView
from .password_reset_views import RequestPasswordResetView, VerifyAndResetPasswordView
from .chatgpt_views import (
    ChatGPTHealthCheckView, AITutorView, QuizGeneratorView,
    ContentSummarizerView, AssignmentGraderView, ConceptExplainerView,
    ContentTranslatorView, LessonPlanGeneratorView, WritingAnalyzerView,
    CustomAIPromptView
)
from .approval_views import StudentApprovalView
from .unified_ai_views import (
    AIProvidersListView, UnifiedAITutorView, UnifiedQuizGeneratorView,
    UnifiedContentSummarizerView, UnifiedConceptExplainerView,
    UnifiedContentTranslatorView
)
from .ai_chat_views import AIChatView, AIPaymentSubmitView
from .ai_auth_views import AIAuthView
from .ai_logout_view import AILogoutView

# REAL CHAT API IMPORTS
from .chat_api import (
    ChatSendMessageView, ChatHistoryView, ChatLoadConversationView,
    ChatSearchView, NotificationListView as ChatNotificationListView,
    ChatDeleteView
)


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/bulk-import/', OnboardingBulkImportView.as_view(), name='bulk-import'),

    #STUDENTS
    path("students/", StudentListCreateView.as_view(), name="student-create-list"),
    path("students/<int:id>/", StudentDetailsView.as_view(), name="student-details"),
    path("students/today/", StudentTodayView.as_view(), name="student-today"),
    
    # STUDENT PORTAL (SELF SERVICE)
    path("my-results/", StudentMyResultView.as_view(), name="my-results"),
    path("my-report-card/", StudentDownloadReportCardView.as_view(), name="my-report-card"),
    path("my-admit-card/", StudentDownloadAdmitCardView.as_view(), name="my-admit-card"),
    
    path("attendence/mark-geo/", GeoFencedAttendanceView.as_view(), name="mark-geo-attendance"),

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
    
    # INSTITUTE
    path('departments/', DepartmentListCreateView.as_view(), name='department-list'),
    
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
    path('subscription/submit-renewal/', RenewalSubmissionView.as_view(), name='subscription-submit-renewal'),
    
    # ADMIN PAYMENT VERIFICATION
    path('admin/payments/pending/', PendingPaymentsListView.as_view(), name='admin-pending-payments'),
    path('admin/payments/approve/', AdminPaymentApprovalView.as_view(), name='admin-approve-payment'),
    
    # SUPER ADMIN DASHBOARD
    path('admin/subscriptions/overview/', SuperAdminDashboardView.as_view(), name='superadmin-overview'),
    path('admin/client-actions/', SuperAdminClientActionView.as_view(), name='admin-client-actions'), # Legacy
    path('admin/advanced/dashboard/', SuperAdminAdvancedDashboardView.as_view(), name='superadmin-advanced-dashboard'),
    
    # NEW: Admin Approval Actions
    path('admin/action/<str:action_type>/<int:item_id>/', AdminApprovalActionView.as_view(), name='admin-approval-action'),

    path('team/manage/', TeamManagementView.as_view(), name='team-manage'),
    path('audit/logs/client/', ClientAuditLogListView.as_view(), name='client-audit-logs'),

    # REPORTS
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/download/<int:pk>/', ReportDownloadView.as_view(), name='report-download'),
    
    # Invoice
    path('invoice/<int:payment_id>/download/', InvoiceDownloadView.as_view(), name='invoice-download'),
    
    # ==================== CHATGPT AI ENDPOINTS ====================
    # AI Service Health Check
    path('ai/chatgpt/health/', ChatGPTHealthCheckView.as_view(), name='chatgpt-health'),
    
    # AI Tutoring
    path('ai/tutor/', AITutorView.as_view(), name='ai-tutor'),
    
    # Quiz Generation
    path('ai/quiz/generate/', QuizGeneratorView.as_view(), name='ai-quiz-generate'),
    
    # Content Summarization
    path('ai/summarize/', ContentSummarizerView.as_view(), name='ai-summarize'),
    
    # Assignment Grading
    path('ai/grade/', AssignmentGraderView.as_view(), name='ai-grade'),
    
    # Concept Explanation
    path('ai/explain/', ConceptExplainerView.as_view(), name='ai-explain'),
    
    # Content Translation
    path('ai/translate/', ContentTranslatorView.as_view(), name='ai-translate'),
    
    # Lesson Plan Generation
    path('ai/lesson-plan/', LessonPlanGeneratorView.as_view(), name='ai-lesson-plan'),
    
    # Writing Analysis
    path('ai/writing/analyze/', WritingAnalyzerView.as_view(), name='ai-writing-analyze'),
    
    # Custom AI Prompt
    path('ai/prompt/', CustomAIPromptView.as_view(), name='ai-custom-prompt'),
    
    # DASHBOARD STATS (PLAN SPECIFIC)
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('search/global/', GlobalSearchView.as_view(), name='global-search'),
    path('calendar/holidays/', HolidayListCreateView.as_view(), name='calendar-holidays'),
    path('academic/routine/', RoutineListCreateView.as_view(), name='academic-routine'),
    path('management/bulk-import/', BulkImportView.as_view(), name='bulk-import'),
    path('reports/', ReportListView.as_view(), name='reports-list'),
    path('reports/download/<int:pk>/', ReportDownloadView.as_view(), name='reports-download'),

    # ==================== NEW AI CHAT INTERFACE ====================
    path('ai/chat/', AIChatView.as_view(), name='ai-chat-interface'),
    path('ai/auth/', AIAuthView.as_view(), name='ai-auth-portal'),
    path('ai/logout/', AILogoutView.as_view(), name='ai-logout'),
    path('ai/payment/submit/', AIPaymentSubmitView.as_view(), name='ai-payment-submit'),

    # ==================== UNIFIED MULTI-MODEL AI ENDPOINTS ====================
    # List all available AI providers
    path('ai/providers/', AIProvidersListView.as_view(), name='ai-providers-list'),
    
    # Unified endpoints with provider selection (ChatGPT, Gemini, Claude)
    path('ai/unified/tutor/', UnifiedAITutorView.as_view(), name='ai-unified-tutor'),
    path('ai/unified/quiz/', UnifiedQuizGeneratorView.as_view(), name='ai-unified-quiz'),
    path('ai/unified/summarize/', UnifiedContentSummarizerView.as_view(), name='ai-unified-summarize'),
    path('ai/unified/explain/', UnifiedConceptExplainerView.as_view(), name='ai-unified-explain'),
    path('ai/unified/translate/', UnifiedContentTranslatorView.as_view(), name='ai-unified-translate'),
    
    # ==================== REAL CHAT API (NEW) ====================
    # Send message to AI and save to database
    path('api/chat/send/', ChatSendMessageView.as_view(), name='chat-send-message'),
    
    # Get all conversations
    path('api/chat/history/', ChatHistoryView.as_view(), name='chat-history'),
    
    # Load specific conversation
    path('api/chat/conversation/<int:conversation_id>/', ChatLoadConversationView.as_view(), name='chat-load-conversation'),
    
    # Search in chats
    path('api/chat/search/', ChatSearchView.as_view(), name='chat-search'),
    
    # Get notifications
    path('api/notifications/', ChatNotificationListView.as_view(), name='chat-notifications'),
    
    # Delete conversation
    path('api/chat/delete/<int:conversation_id>/', ChatDeleteView.as_view(), name='chat-delete'),
]

# =====================================================
# PDF REPORT GENERATION URLS
# =====================================================

urlpatterns += [
    path('generate/id-card/<int:student_id>/', GenerateIDCardView.as_view(), name='generate-id-card'),
    path('generate/admit-card/<int:student_id>/', GenerateAdmitCardView.as_view(), name='generate-admit-card'),
    path('generate/report-card/<int:student_id>/', GenerateReportCardView.as_view(), name='generate-report-card'),
]

# Temporarily appended to fix check
# This line is intentionally left blank to ensure newline
