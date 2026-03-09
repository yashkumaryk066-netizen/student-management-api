from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # Core Auth & Profile
    SecuredTokenObtainPairView, ProfileView, TeamManagementView, ChangePasswordView,
    
    # Dashboards & Stats
    DashboardStatsView, StudentDashboardView, TeacherDashboardView, ParentDashboardView,
    SuperAdminDashboardView, SuperAdminAdvancedDashboardView, GlobalSearchView,
    AdminApprovalActionView, InstitutionROIView,
    
    # Students
    StudentListCreateView, StudentDetailsView, StudentTodayView, StudentPerformanceView, StudentAnalyticsView,
    GenerateBulkAdmitCardView, GenerateBulkIDCardView,
    
    # Attendance
    AttendenceCreateView, AttendenceDetailsView, GeoFencedAttendanceView, AttendanceScanView,
    
    # Academic & Modules
    DepartmentListCreateView, LibraryBookListCreateView, LibraryBookDetailView, BookIssueListCreateView,
    HostelListCreateView, RoomListCreateView, HostelAllocationListCreateView, HostelAnalyticsView,
    VehicleListCreateView, RouteListCreateView, TransportAllocationListCreateView,
    EmployeeListCreateView, LeaveRequestListCreateView,
    ExamListCreateView, GradeListCreateView, EventListCreateView,
    ClassroomViewSet, ClassScheduleViewSet,
    CourseListCreateView, CourseDetailView, BatchListCreateView, EnrollmentListCreateView,
    LiveClassListCreateView, LiveClassDetailView,
    
    # Finance
    PaymentListCreateView, PaymentDetailsView, PaymentStatusUpdateView, InvoiceDownloadView,
    ManualPaymentSubmitView, PendingPaymentsListView, AdminPaymentApprovalView,
    InitEazypayPaymentView, EazypayCallbackView,
    FinancialForecastView, DefaulterAnalysisView, ExportFinancialReportView,
    
    # Certificates & SEO
    GenerateCertificateView, GenerateIDCardView, GenerateAdmitCardView, GenerateReportCardView,
    MyReportCardView, MyResultsView,
    LegacyGenerateIDCardView, LegacyGenerateAdmitCardView, LegacyGenerateReportCardView,
    LegacyGenerateCertificateView, LegacyGenerateBulkIDCardView, LegacyGenerateBulkAdmitCardView,
    LandingPageView, LoginPageView, DemoRequestView, DeveloperProfileView, ResumeView,
    
    # Subscription
    ClientSubscriptionView, SubscriptionRenewalView, PublicSubscriptionSubmitView,
    UserPlanFeaturesView, OnboardingPaymentView, OnboardingBulkImportView,
    SubscriptionStatusView,
    
    
    # AI Tools & Chat
    AIAuthView, AIChatView, AITutorView, UnifiedAITutorView, AIProvidersListView,
    QuizGeneratorView, ExamPaperGeneratorView, ContentSummarizerView,
    AssignmentGraderView, ConceptExplainerView, ContentTranslatorView,
    LessonPlanGeneratorView, WritingAnalyzerView,
    AIPaymentSubmitView,
    ChatSendMessageView, ChatConversationListView, ChatHistoryView, ChatHistoryLegacyView,
    ChatConversationDetailLegacyView, ChatSearchLegacyView,
    
    # Online Exam System
    OnlineExamViewSet, OnlineExamInteractionView, OnlineExamInteractionActionAliasView, OnlineExamTemplateView, OnlineExamResultView,
    OnlineExamCertificateDownloadView, StudentPerformanceInsightView, PublicResultVerificationView, ExamPortalView,
    
    # Premium ViewSets
    StudentLeadViewSet, SubstituteAllocationViewSet, StudentDiaryViewSet, LMSMaterialViewSet,
    LMSAssignmentViewSet, AssignmentSubmissionViewSet, InventoryItemViewSet,
    InstitutionExpenseViewSet, StudentLeaveRequestViewSet, SubjectViewSet,
    PayrollViewSet,
    
    # Misc
    AuditLogView, HolidayListCreateView, RoutineListCreateView, BulkImportView,
    NotificationListView, NotificationCreateView, NotificationMarkReadView, NotificationMarkAllReadView,
    VerifyIdentityView, CheckPublicAvailabilityView, RequestPasswordResetView, VerifyAndResetPasswordView,
    CheckInstitutionView, CheckUsernameView,
    ReportListView, ReportDownloadView,
    InstitutionSettingsView, DataBackupView, TriggerAutomationView,
    SupportTicketViewSet, GlobalAnnouncementViewSet
)
from .sa_views import (
    SuperAdminClientsView,
    SuperAdminImpersonateView,
    SuperAdminSubscriptionOverviewView,
    SuperAdminClientActionView,
)
from .resume_views import DownloadResumeView
from .subscription_apis import (
    SubscriptionApprovalAPI,
    SubscriptionRejectAPI,
    ClientBlockAPI,
    ClientUnblockAPI,
    ClientDeleteAPI,
    ClientCredentialsAPI,
)

urlpatterns = [
    # Frontend Pages (Legacy/Compatibility)
    path('', LandingPageView.as_view(), name='landing'),
    path('login/', LoginPageView.as_view(), name='login'),
    
    # Resume Download (Public)
    path('resume/download/', DownloadResumeView.as_view(), name='resume-download'),

    # Demo Request (Public - from Landing Page)
    path('demo/request/', DemoRequestView.as_view(), name='demo-request'),
    path('demo-request/', DemoRequestView.as_view(), name='demo-request-alt'),  # Backward compat

    # Auth Endpoints
    path('auth/login/', SecuredTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # CRITICAL FOR STAYING LOGGED IN
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_legacy'),
    path('token/', SecuredTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/identity/', VerifyIdentityView.as_view(), name='identity-check'),
    path('auth/verify-identity/', VerifyIdentityView.as_view(), name='verify-identity'),
    path('auth/availability/', CheckPublicAvailabilityView.as_view(), name='check-availability-legacy'),
    path('auth/check-availability/', CheckPublicAvailabilityView.as_view(), name='check-availability'),
    path('auth/check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('auth/check-institution/', CheckInstitutionView.as_view(), name='check-institution'),
    path('auth/password-reset/request/', RequestPasswordResetView.as_view(), name='password-reset-request'),
    path('auth/password-reset/verify/', VerifyAndResetPasswordView.as_view(), name='password-reset-verify'),
    path('auth/password-reset/confirm/', VerifyAndResetPasswordView.as_view(), name='password-reset-confirm'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Profile & Team
    path('profile/', ProfileView.as_view(), name='profile-detail'),
    path('team/manage/', TeamManagementView.as_view(), name='team-manage'),
    
    # Dashboards & Stats (JSON APIs)
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/student/', StudentDashboardView.as_view(), name='api-student-dashboard'),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name='api-teacher-dashboard'),
    path('dashboard/parent/', ParentDashboardView.as_view(), name='api-parent-dashboard'),
    
    path('super-admin/stats/', DashboardStatsView.as_view(), name='super-admin-stats'),
    path('super-admin/dashboard/', SuperAdminDashboardView.as_view(), name='super-admin-dashboard'),
    path('super-admin/clients/', SuperAdminClientsView.as_view(), name='super-admin-clients'),
    path('super-admin/impersonate/<int:pk>/', SuperAdminImpersonateView.as_view(), name='super-admin-impersonate'),
    path('admin/advanced/dashboard/', SuperAdminAdvancedDashboardView.as_view(), name='admin-advanced-dashboard'),
    path('admin/action/<str:action_type>/<int:item_id>/', AdminApprovalActionView.as_view(), name='admin-advanced-action'),
    path('global-search/', GlobalSearchView.as_view(), name='global-search'),
    path('search/', GlobalSearchView.as_view(), name='api-magic-search'),
    path('search/global/', GlobalSearchView.as_view(), name='api-search-global'),
    
    # Student Management
    path('students/', StudentListCreateView.as_view(), name='student-list'),
    path('students/<int:id>/', StudentDetailsView.as_view(), name='student-detail'),
    path('students/today/', StudentTodayView.as_view(), name='student-today'),
    path('students/analytics/', StudentAnalyticsView.as_view(), name='student-analytics'), # Premium Stats
    path('students/<int:student_id>/performance/', StudentPerformanceView.as_view(), name='student-performance'),
    path('students/bulk-admit-cards/', GenerateBulkAdmitCardView.as_view(), name='bulk-admit-cards'),
    
    # Attendance
    path('attendence/', AttendenceCreateView.as_view(), name='attendance-list'),
    path('attendence/<int:pk>/', AttendenceDetailsView.as_view(), name='attendance-detail'),
    path('attendence/mark-geo/', GeoFencedAttendanceView.as_view(), name='attendance-mark-geo'),
    
    # Modules
    path('departments/', DepartmentListCreateView.as_view(), name='department-list'),
    path('library/books/', LibraryBookListCreateView.as_view(), name='library-books'),
    path('library/books/<int:pk>/', LibraryBookDetailView.as_view(), name='library-book-detail'),
    path('library/issues/', BookIssueListCreateView.as_view(), name='library-issues'),
    
    path('hostel/', HostelListCreateView.as_view(), name='hostel-list'),
    path('hostel/rooms/', RoomListCreateView.as_view(), name='room-list'),
    path('hostel/allocations/', HostelAllocationListCreateView.as_view(), name='hostel-allocations'),
    path('hostel/analytics/', HostelAnalyticsView.as_view(), name='hostel-analytics'),
    
    path('transport/vehicles/', VehicleListCreateView.as_view(), name='transport-vehicles'),
    path('transport/routes/', RouteListCreateView.as_view(), name='transport-routes'),
    path('transport/allocations/', TransportAllocationListCreateView.as_view(), name='transport-allocations'),
    
    path('hr/employees/', EmployeeListCreateView.as_view(), name='hr-employees'),
    path('hr/staff/', EmployeeListCreateView.as_view(), name='hr-staff-api'), # Alias for api.js
    path('hr/leaves/', LeaveRequestListCreateView.as_view(), name='hr-leaves'),
    path('leave-requests/', LeaveRequestListCreateView.as_view(), name='leave-requests-alias'),
    
    path('exams/', ExamListCreateView.as_view(), name='exam-list'),
    path('grades/', GradeListCreateView.as_view(), name='grade-list'),
    path('events/', EventListCreateView.as_view(), name='event-list'),
    
    path('courses/', CourseListCreateView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('batches/', BatchListCreateView.as_view(), name='batch-list'),
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list'),
    
    path('live-classes/', LiveClassListCreateView.as_view(), name='live-classes'),
    path('live-classes/<int:pk>/', LiveClassDetailView.as_view(), name='live-class-detail'),
    
    # Finance
    path('payments/', PaymentListCreateView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', PaymentDetailsView.as_view(), name='payment-detail'),
    path('payments/<int:pk>/update_status/', PaymentStatusUpdateView.as_view(), name='payment-update-status'),
    path('invoice/<int:pk>/download/', InvoiceDownloadView.as_view(), name='invoice-download'),
    path('analytics/finance/forecast/', FinancialForecastView.as_view(), name='finance-forecast'),
    path('analytics/finance/defaulters/', DefaulterAnalysisView.as_view(), name='finance-defaulters'),
    path('analytics/finance/export/', ExportFinancialReportView.as_view(), name='finance-export'),
    path('payments/approve/', AdminPaymentApprovalView.as_view(), name='admin-approve-payment'),
    # Backward-compatible alias used by dashboard JS
    path('admin/payments/approve/', AdminPaymentApprovalView.as_view(), name='admin-approve-payment-compat'),
    path('payments/eazypay/init/', InitEazypayPaymentView.as_view(), name='payment-eazypay-init'),
    path('payments/eazypay/callback/', EazypayCallbackView.as_view(), name='payment-eazypay-callback'),
    path('manual-payment-submit/', ManualPaymentSubmitView.as_view(), name='manual-payment-submit'),
    path('payment/manual/submit/', ManualPaymentSubmitView.as_view(), name='manual-payment-submit-alt'),
    path('admin/subscriptions/overview/', SuperAdminSubscriptionOverviewView.as_view(), name='admin-subscriptions-overview'),
    path('admin/client-actions/', SuperAdminClientActionView.as_view(), name='admin-client-actions'),
    
    # Subscription
    path('subscription/', ClientSubscriptionView.as_view(), name='subscription-detail'),
    path('subscription/status/', SubscriptionStatusView.as_view(), name='subscription-status'),
    
    path('subscription/renew/', SubscriptionRenewalView.as_view(), name='subscription-renew'),
    path('subscription/submit/', PublicSubscriptionSubmitView.as_view(), name='subscription-submit'),
    # Legacy super-admin subscription actions
    path('subscription/approve/', SubscriptionApprovalAPI.as_view(), name='subscription-approve'),
    path('subscription/reject/', SubscriptionRejectAPI.as_view(), name='subscription-reject'),
    path('client/block/', ClientBlockAPI.as_view(), name='client-block'),
    path('client/unblock/', ClientUnblockAPI.as_view(), name='client-unblock'),
    path('client/<int:user_id>/delete/', ClientDeleteAPI.as_view(), name='client-delete'),
    path('client/<int:user_id>/credentials/', ClientCredentialsAPI.as_view(), name='client-credentials'),
    path('subscription/plans/features/', UserPlanFeaturesView.as_view(), name='plan-features-full'),
    path('plan/features/', UserPlanFeaturesView.as_view(), name='plan-features'),
    path('user/plan/', UserPlanFeaturesView.as_view(), name='plan-features-user'),
    
    # AI Hub & Chat
    path('chat/send/', ChatSendMessageView.as_view(), name='chat-send'),
    path('chat/conversations/', ChatConversationListView.as_view(), name='chat-conversations'),
    path('chat/history/<int:conversation_id>/', ChatHistoryView.as_view(), name='chat-history'),
    # Legacy chat endpoints used by older dashboard scripts
    path('chat/history/', ChatHistoryLegacyView.as_view(), name='chat-history-legacy'),
    path('chat/conversation/<int:conversation_id>/', ChatConversationDetailLegacyView.as_view(), name='chat-conversation-legacy'),
    path('chat/search/', ChatSearchLegacyView.as_view(), name='chat-search-legacy'),

    path('ai/auth/', AIAuthView.as_view(), name='ai-auth'),
    path('ai/chat/', AIChatView.as_view(), name='ai-chat'),
    path('ai/payment/submit/', AIPaymentSubmitView.as_view(), name='ai-payment-submit'),
    path('ai/tutor/', AITutorView.as_view(), name='ai-tutor'),
    path('ai/unified/tutor/', UnifiedAITutorView.as_view(), name='ai-unified-tutor'),
    path('ai/unified/providers/', AIProvidersListView.as_view(), name='ai-providers-list'),
    path('ai/quiz/', QuizGeneratorView.as_view(), name='ai-quiz'),
    path('ai/exam-generator/', ExamPaperGeneratorView.as_view(), name='ai-exam-generator'),
    path('ai/lesson-plan-generator/', LessonPlanGeneratorView.as_view(), name='ai-lesson-plan-generator'),
    path('ai/grader/', AssignmentGraderView.as_view(), name='ai-assignment-grader'),
    path('ai/writing-analyzer/', WritingAnalyzerView.as_view(), name='ai-writing-analyzer'),
    path('ai/summarizer/', ContentSummarizerView.as_view(), name='ai-content-summarizer'),
    path('ai/translator/', ContentTranslatorView.as_view(), name='ai-content-translator'),
    path('ai/explainer/', ConceptExplainerView.as_view(), name='ai-concept-explainer'),
    
    # Online Exam System interaction
    path('portal/exam/<int:exam_id>/', ExamPortalView.as_view(), name='student-take-exam'),
    path('online-exam/', OnlineExamTemplateView.as_view(), name='online-exam-template'),
    path('online-exam-session/<int:exam_id>/', OnlineExamInteractionView.as_view(), name='online-exam-details'),
    path('online-exam-session/<int:exam_id>/<str:action>/', OnlineExamInteractionActionAliasView.as_view(), name='online-exam-interaction'),
    path('online-exam-result/<int:attempt_id>/', OnlineExamResultView.as_view(), name='online-exam-result'),
    path('online-exam-verify/', PublicResultVerificationView.as_view(), name='online-exam-verify'),
    path('online-exam-certificate/<int:attempt_id>/', OnlineExamCertificateDownloadView.as_view(), name='online-exam-certificate'),
    path('ai/student-insights/', StudentPerformanceInsightView.as_view(), name='ai-student-insights'),
    
    # Documents
    path('generate-id-card/<int:student_id>/', GenerateIDCardView.as_view(), name='generate-id-card'),
    path('generate-admit-card/<int:student_id>/', GenerateAdmitCardView.as_view(), name='generate-admit-card'),
    path('generate-report-card/<int:student_id>/', GenerateReportCardView.as_view(), name='generate-report-card'),
    path('generate-certificate/<int:student_id>/', GenerateCertificateView.as_view(), name='generate-certificate'),
    path('generate-bulk-id-cards/', GenerateBulkIDCardView.as_view(), name='bulk-id-cards'),
    path('generate-bulk-admit-cards/', GenerateBulkAdmitCardView.as_view(), name='bulk-admit-cards-alt'),
    path('my-report-card/', MyReportCardView.as_view(), name='my-report-card'),
    path('my-results/', MyResultsView.as_view(), name='my-results'),
    
    # Analytics & Extra
    path('analytics/roi/', InstitutionROIView.as_view(), name='analytics-roi'),
    path('attendance/scan/', AttendanceScanView.as_view(), name='attendance-scan'),
    path('bulk-import/', BulkImportView.as_view(), name='bulk-import'),
    path('audit/logs/client/', AuditLogView.as_view(), name='audit-logs-client'),
    path('audit/logs/global/', AuditLogView.as_view(), name='audit-logs-global'),

    # ✅ Class Timetable / Routine (FIX: was missing - frontend calls this)
    path('academic/routine/', RoutineListCreateView.as_view(), name='routine-list'),

    # ✅ Holiday Calendar (FIX: was missing - frontend calendar calls this)
    path('calendar/holidays/', HolidayListCreateView.as_view(), name='holiday-list'),
    path('calendar/holidays/<int:pk>/', HolidayListCreateView.as_view(), name='holiday-detail'),

    # Notifications API
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/create/', NotificationCreateView.as_view(), name='notifications-create'),
    path('notifications/<int:id>/read/', NotificationMarkReadView.as_view(), name='notifications-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notifications-mark-all-read'),

    # Legacy document routes used by existing JS
    path('generate/id-card/<int:student_id>/', LegacyGenerateIDCardView.as_view(), name='legacy-generate-id-card'),
    path('generate/admit-card/<int:student_id>/', LegacyGenerateAdmitCardView.as_view(), name='legacy-generate-admit-card'),
    path('generate/report-card/<int:student_id>/', LegacyGenerateReportCardView.as_view(), name='legacy-generate-report-card'),
    path('generate/admission-letter/<int:student_id>/', LegacyGenerateCertificateView.as_view(), name='legacy-generate-admission-letter'),
    path('generate/certificate/<int:student_id>/', LegacyGenerateCertificateView.as_view(), name='legacy-generate-certificate'),
    path('generate/bulk-id-cards/', LegacyGenerateBulkIDCardView.as_view(), name='legacy-bulk-id-cards'),
    path('generate/bulk-admit-cards/', LegacyGenerateBulkAdmitCardView.as_view(), name='legacy-bulk-admit-cards'),
    
    # Reports
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/download/<int:pk>/', ReportDownloadView.as_view(), name='report-download'),
    
    # Advanced Settings (Magic Features)
    path('settings/config/', InstitutionSettingsView.as_view(), name='institution-config'),
    path('settings/backup/download/', DataBackupView.as_view(), name='data-backup'),
    path('settings/automation/trigger/', TriggerAutomationView.as_view(), name='automation-trigger'),
]

# Register ViewSets with Router
router = DefaultRouter()
router.register(r'leads', StudentLeadViewSet, basename='leads')
router.register(r'substitutes', SubstituteAllocationViewSet, basename='substitutes')
router.register(r'inventory', InventoryItemViewSet, basename='inventory')
router.register(r'diary', StudentDiaryViewSet, basename='diary')
router.register(r'lms/materials', LMSMaterialViewSet, basename='lms-materials')
router.register(r'lms/assignments', LMSAssignmentViewSet, basename='lms-assignments')
router.register(r'lms/submissions', AssignmentSubmissionViewSet, basename='lms-submissions')
router.register(r'expenses', InstitutionExpenseViewSet, basename='expenses')
router.register(r'leave-requests', StudentLeaveRequestViewSet, basename='student-leave-requests')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'online-exams', OnlineExamViewSet, basename='online-exams')
router.register(r'payroll', PayrollViewSet, basename='payroll')
router.register(r'classrooms', ClassroomViewSet, basename='classrooms')
router.register(r'class-schedules', ClassScheduleViewSet, basename='class-schedules')
router.register(r'support-tickets', SupportTicketViewSet, basename='support-tickets')
router.register(r'announcements', GlobalAnnouncementViewSet, basename='announcements')

urlpatterns += [
    path('', include(router.urls)),
]
