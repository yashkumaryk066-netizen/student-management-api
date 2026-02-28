from .base import AuditModel
from .users import ClientSubscription, UserProfile, PasswordResetOTP
from .academic import Department, Student, Subject, Classroom, ClassSchedule, Holiday, ClassRoutine
from .attendance import Attendence
from .finance import Payment
from .hostel import Hostel, Room, HostelAllocation
from .transport import Vehicle, Route, TransportAllocation
from .library import LibraryBook, BookIssue
from .hr import HRDepartment, Designation, Employee, LeaveRequest, Payroll
from .exam import Exam, Grade, ResultCard
from .event import Event, EventParticipant
from .communication import Notification, DemoRequest, SupportTicket, GlobalAnnouncement, GeneratedReport, AuditLog
from .coaching import Course, Batch, Enrollment, LiveClass
from .ai import AISubscription

# Import Chat models to maintain compatibility
# These are in sibling file chat_models.py (student/chat_models.py)
# Since we are in student/models/__init__.py, ".." refers to student/
from ..chat_models import ChatConversation, ChatMessage, UserNotification
