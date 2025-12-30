from django.contrib import admin
from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Subject, Classroom, ClassSchedule,
    Hostel, Room, HostelAllocation,
    Event, EventParticipant,
    DemoRequest
)


# ==================== STUDENT MANAGEMENT ====================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'age', 'gender', 'grade', 'dob', 'parent']
    list_filter = ['gender', 'grade']
    search_fields = ['name', 'relation']
    list_per_page = 50
    ordering = ['-id']


@admin.register(Attendence)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'is_present']
    list_filter = ['is_present', 'date']
    search_fields = ['student__name']
    date_hierarchy = 'date'
    list_per_page = 100


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'status', 'due_date', 'paid_date', 'description']
    list_filter = ['status', 'due_date', 'paid_date']
    search_fields = ['student__name', 'description']
    list_editable = ['status']
    date_hierarchy = 'due_date'
    ordering = ['-due_date']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient_type', 'recipient', 'is_read', 'created_at']
    list_filter = ['recipient_type', 'is_read', 'created_at']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'
    list_editable = ['is_read']


# ==================== ACADEMICS ====================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['code']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'capacity', 'floor', 'building']
    list_filter = ['room_type', 'floor', 'building']
    search_fields = ['room_number', 'building']
    ordering = ['building', 'floor', 'room_number']


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['section', 'subject', 'teacher', 'classroom', 'day_of_week', 'start_time', 'end_time', 'academic_year']
    list_filter = ['day_of_week', 'academic_year', 'section']
    search_fields = ['section', 'subject__name', 'teacher__username']
    ordering = ['day_of_week', 'start_time']


# ==================== HOSTEL MANAGEMENT ====================

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostel_type', 'total_rooms', 'warden']
    list_filter = ['hostel_type']
    search_fields = ['name', 'address']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'room_number', 'floor', 'capacity', 'current_occupancy', 'available_beds', 'room_type']
    list_filter = ['hostel', 'floor', 'room_type']
    search_fields = ['room_number']
    ordering = ['hostel', 'floor', 'room_number']
    
    def available_beds(self, obj):
        return obj.available_beds
    available_beds.short_description = 'Available Beds'


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'check_in_date', 'check_out_date', 'status', 'monthly_fee']
    list_filter = ['status', 'check_in_date', 'room__hostel']
    search_fields = ['student__name', 'room__room_number']
    date_hierarchy = 'check_in_date'
    ordering = ['-check_in_date']


# ==================== EVENTS ====================

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_date', 'end_date', 'venue', 'organizer', 'is_active']
    list_filter = ['event_type', 'is_active', 'start_date']
    search_fields = ['name', 'description', 'venue']
    date_hierarchy = 'start_date'
    list_editable = ['is_active']
    ordering = ['-start_date']


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'participation_type', 'registration_date', 'attended']
    list_filter = ['participation_type', 'attended', 'registration_date']
    search_fields = ['event__name', 'user__username']
    date_hierarchy = 'registration_date'
    list_editable = ['attended']


# ==================== DEMO REQUESTS ====================

@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'institution_name', 'status', 'created_at']
    list_filter = ['status', 'institution_type', 'created_at']
    search_fields = ['name', 'phone', 'email', 'institution_name']
    date_hierarchy = 'created_at'
    list_editable = ['status']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Institution Details', {
            'fields': ('institution_name', 'institution_type', 'message')
        }),
        ('Status & Notes', {
            'fields': ('status', 'contacted_at', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== EXAM & GRADING ====================

from .models import Exam, Grade, ResultCard, LibraryBook, BookIssue

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'grade_class', 'total_marks', 'passing_marks', 'exam_date', 'academic_year']
    list_filter = ['exam_type', 'academic_year', 'grade_class', 'exam_date']
    search_fields = ['name', 'subject__name', 'grade_class']
    date_hierarchy = 'exam_date'
    ordering = ['-exam_date']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'get_total_marks', 'percentage', 'status']
    list_filter = ['status', 'exam__exam_type', 'exam__academic_year']
    search_fields = ['student__name', 'exam__name']
    ordering = ['-exam__exam_date']
    
    def get_total_marks(self, obj):
        return obj.exam.total_marks
    get_total_marks.short_description = 'Total Marks'
    
    def percentage(self, obj):
        return f"{obj.percentage:.2f}%"


@admin.register(ResultCard)
class ResultCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'grade_class', 'semester_term', 'academic_year', 'percentage', 'gpa', 'result_status']
    list_filter = ['result_status', 'academic_year', 'grade_class']
    search_fields = ['student__name']
    ordering = ['-generated_at']


# ==================== LIBRARY ====================

@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ['isbn', 'title', 'author', 'category', 'total_copies', 'available_copies', 'is_available', 'price']
    list_filter = ['category', 'published_year']
    search_fields = ['isbn', 'title', 'author', 'publisher']
    ordering = ['title']
    list_per_page = 50
    
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Available'


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'student', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['book__title', 'student__name']
    date_hierarchy = 'issue_date'
    list_editable = ['status']
    ordering = ['-issue_date']
    
    fieldsets = (
        ('Issue Details', {
            'fields': ('book', 'student', 'due_date')
        }),
        ('Return Details', {
            'fields': ('return_date', 'status', 'fine_amount')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
