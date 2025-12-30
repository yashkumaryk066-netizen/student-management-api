from django.contrib import admin
from .models import Student, Attendence

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "gender", "age")
    search_fields = ("name", "gender")
    list_filter = ("gender",)

@admin.register(Attendence)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "is_present")
    list_filter = ("date", "is_present")
    search_fields = ("student__name",)
