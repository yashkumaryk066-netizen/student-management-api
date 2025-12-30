from django.contrib import admin
from .models import Student, Attendence, UserProfile, Payment, Notification

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
