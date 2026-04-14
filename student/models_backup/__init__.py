"""
Backup model snapshots for reference tooling and one-off scripts.

This package intentionally avoids importing Django model classes at module import
time. Django's test discovery imports packages while scanning the app, and eager
imports here would register a second copy of the student models and crash tests.
"""

from importlib import import_module

_MODEL_EXPORTS = {
    'AuditModel': ('base', 'AuditModel'),
    'ClientSubscription': ('users', 'ClientSubscription'),
    'UserProfile': ('users', 'UserProfile'),
    'PasswordResetOTP': ('users', 'PasswordResetOTP'),
    'Department': ('academic', 'Department'),
    'Student': ('academic', 'Student'),
    'Subject': ('academic', 'Subject'),
    'Classroom': ('academic', 'Classroom'),
    'ClassSchedule': ('academic', 'ClassSchedule'),
    'Holiday': ('academic', 'Holiday'),
    'ClassRoutine': ('academic', 'ClassRoutine'),
    'Attendence': ('attendance', 'Attendence'),
    'Payment': ('finance', 'Payment'),
    'Hostel': ('hostel', 'Hostel'),
    'Room': ('hostel', 'Room'),
    'HostelAllocation': ('hostel', 'HostelAllocation'),
    'Vehicle': ('transport', 'Vehicle'),
    'Route': ('transport', 'Route'),
    'TransportAllocation': ('transport', 'TransportAllocation'),
    'LibraryBook': ('library', 'LibraryBook'),
    'BookIssue': ('library', 'BookIssue'),
    'HRDepartment': ('hr', 'HRDepartment'),
    'Designation': ('hr', 'Designation'),
    'Employee': ('hr', 'Employee'),
    'LeaveRequest': ('hr', 'LeaveRequest'),
    'Payroll': ('hr', 'Payroll'),
    'Exam': ('exam', 'Exam'),
    'Grade': ('exam', 'Grade'),
    'ResultCard': ('exam', 'ResultCard'),
    'Event': ('event', 'Event'),
    'EventParticipant': ('event', 'EventParticipant'),
    'Notification': ('communication', 'Notification'),
    'DemoRequest': ('communication', 'DemoRequest'),
    'SupportTicket': ('communication', 'SupportTicket'),
    'GlobalAnnouncement': ('communication', 'GlobalAnnouncement'),
    'GeneratedReport': ('communication', 'GeneratedReport'),
    'AuditLog': ('communication', 'AuditLog'),
    'Course': ('coaching', 'Course'),
    'Batch': ('coaching', 'Batch'),
    'Enrollment': ('coaching', 'Enrollment'),
    'LiveClass': ('coaching', 'LiveClass'),
    'AISubscription': ('ai', 'AISubscription'),
}

__all__ = list(_MODEL_EXPORTS)


def __getattr__(name):
    if name not in _MODEL_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, export_name = _MODEL_EXPORTS[name]
    module = import_module(f'{__name__}.{module_name}')
    return getattr(module, export_name)
