from rest_framework import serializers
from django.utils import timezone
from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    LibraryBook, BookIssue, Hostel, Room, HostelAllocation,
    Vehicle, Route, TransportAllocation, Employee, Department, Designation,
    LeaveRequest, Payroll, Exam, Grade, Event,
    Course, Batch, Enrollment, LiveClass
)

# ==================== CORE ====================

class StudentSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"

    def get_parent_name(self, obj):
        return obj.parent.username if obj.parent else None


class AttendenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Attendence
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'role', 'phone', 'institution_type', 'created_at']
        read_only_fields = ['created_at']


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']

    def get_is_overdue(self, obj):
        return obj.status != 'PAID' and obj.due_date and obj.due_date < timezone.now().date()


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ['created_at']

    def get_recipient_name(self, obj):
        return obj.recipient.username if obj.recipient else "All"

# ==================== LIBRARY ====================

class LibraryBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryBook
        fields = "__all__"


class BookIssueSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = BookIssue
        fields = "__all__"

# ==================== HOSTEL ====================

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)

    class Meta:
        model = Room
        fields = "__all__"


class HostelAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    hostel_name = serializers.CharField(source='room.hostel.name', read_only=True)

    class Meta:
        model = HostelAllocation
        fields = "__all__"

# ==================== TRANSPORT ====================

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.registration_number', read_only=True)

    class Meta:
        model = Route
        fields = "__all__"


class TransportAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    route_name = serializers.CharField(source='route.route_name', read_only=True)

    class Meta:
        model = TransportAllocation
        fields = "__all__"

# ==================== HR ====================

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = "__all__"

    def get_fullname(self, obj):
        return obj.user.get_full_name()

# ==================== ACADEMIC ====================

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = "__all__"


class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = Exam
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"

# ==================== COACHING ====================

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='primary_teacher.get_full_name', read_only=True)
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Batch
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    course_name = serializers.CharField(source='batch.course.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = "__all__"


class LiveClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveClass
        fields = "__all__"
