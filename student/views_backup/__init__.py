# Base & Utilities
from .base import get_owner_user, filter_by_owner

# Academic
from .academic import (
    StudentListCreateView, StudentDetailsView, 
    DepartmentListCreateView
)

# Finance
from .finance import (
    PaymentListCreateView, PaymentDetailsView, InvoiceDownloadView
)

# Attendance
from .attendance import (
    AttendenceCreateView, AttendenceDetailsView, StudentTodayView
)

# Users (Staff, Profile, Subscription)
from .users import (
    TeamManagementView, ProfileView, 
    ClientSubscriptionView, SubscriptionRenewalView,
    ClientAuditLogListView
)

# Hostel
from .hostel import (
    HostelListCreateView, RoomListCreateView, HostelAllocationListCreateView
)

# Transport
from .transport import (
    VehicleListCreateView, RouteListCreateView, TransportAllocationListCreateView
)

# Library
from .library import (
    LibraryBookListCreateView, LibraryBookDetailView, BookIssueListCreateView
)

# HR
from .hr import (
    EmployeeListCreateView, LeaveRequestListCreateView
)

# Exam
from .exam import (
    ExamListCreateView
)

# Event
from .event import (
    EventListCreateView
)

# Coaching
from .coaching import (
    CourseListCreateView, CourseDetailView, 
    BatchListCreateView, EnrollmentListCreateView, 
    LiveClassListCreateView, LiveClassListView
)

# Communication
from .communication import (
    NotificationListView, NotificationMarkReadView, 
    NotificationCreateView, DemoRequestView
)

# Dashboard & Templates
from .dashboard import (
    LandingPageView, LoginPageView, DemoPageView, 
    DeveloperProfileView, ResumeView,
    AdminDashboardTemplateView, SuperAdminDashboardTemplateView,
    TeacherDashboardTemplateView, StudentDashboardTemplateView, 
    ParentDashboardTemplateView,
    StudentDashboardView, TeacherDashboardView, ParentDashboardView,
    DashboardStatsView
)

# Search, Calendar, Bulk
from .search import GlobalSearchView
from .calendar import HolidayListCreateView, RoutineListCreateView
from .bulk import BulkImportView

# Reports (PDFs)
from .report import (
    GenerateAdmitCardView, GenerateReportCardView, GenerateIDCardView
)

# SEO & PWA
from .seo import robots_txt, sitemap_xml, google_verification
from .pwa import service_worker
