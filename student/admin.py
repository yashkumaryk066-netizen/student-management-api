from django.contrib import admin
from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Subject, Classroom, ClassSchedule,
    Hostel, Room, HostelAllocation,
    Event, EventParticipant
)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "gender", "age", "grade", "parent")
    search_fields = ("name", "gender")
    list_filter = ("gender", "grade")

@admin.register(Attendence)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "is_present")
    list_filter = ("date", "is_present")
    search_fields = ("student__name",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "phone")

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "due_date", "status", "paid_date")
    list_filter = ("status", "due_date")
    search_fields = ("student__name", "description")
    date_hierarchy = "due_date"

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient_type", "recipient", "is_read", "created_at")
    list_filter = ("recipient_type", "is_read", "created_at")
    search_fields = ("title", "message")
    date_hierarchy = "created_at"

# Academic Modules
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits']
    search_fields = ['name', 'code']

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'capacity', 'floor', 'building']
    list_filter = ['room_type', 'floor']
    search_fields = ['room_number', 'building']

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['section', 'subject', 'teacher', 'day_of_week', 'start_time', 'classroom']
    list_filter = ['day_of_week', 'section', 'academic_year']
    search_fields = ['section']

# Hostel Modules
@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostel_type', 'total_rooms', 'warden']
    list_filter = ['hostel_type']
    search_fields = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'room_number', 'floor', 'capacity', 'current_occupancy', 'available_beds']
    list_filter = ['hostel', 'floor']
    search_fields = ['room_number']
    
    def available_beds(self, obj):
        return obj.available_beds
    available_beds.short_description = 'Available Beds'

@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'check_in_date', 'status', 'monthly_fee']
    list_filter = ['status', 'room__hostel']
    search_fields = ['student__name']

# Events  
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_date', 'venue', 'organizer', 'is_active']
    list_filter = ['event_type', 'is_active']
    search_fields = ['name', 'venue']

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'participation_type', 'registration_date', 'attended']
    list_filter = ['participation_type', 'attended']
    search_fields = ['user__username', 'event__name']
