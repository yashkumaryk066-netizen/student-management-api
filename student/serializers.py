from rest_framework import serializers
from django.utils import timezone
from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    LibraryBook, BookIssue, Hostel, Room, HostelAllocation,
    Vehicle, Route, TransportAllocation, Employee, Department, Designation,
    LeaveRequest, Payroll, Exam, Grade, Event,
    Course, Batch, Enrollment, LiveClass, AuditLog,
    StudentDiary, StudentLeaveRequest, LMSMaterial, LMSAssignment, AssignmentSubmission,
    InventoryItem, InstitutionExpense, StudentLead, SubstituteAllocation, ResultCard,
    Holiday, ClassRoutine, Subject, Classroom, ClassSchedule, SupportTicket, GlobalAnnouncement,
    OnlineExam, OnlineQuestion, ExamAttempt, ExamResponse, StudentPerformanceInsight,
    LoginAttempt, ClientSubscription, ChatConversation, ChatMessage
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# ==================== ONLINE EXAM ====================

class OnlineQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineQuestion
        fields = "__all__"

class OnlineExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    question_count = serializers.SerializerMethodField()
    estimated_result_release = serializers.SerializerMethodField()
    
    class Meta:
        model = OnlineExam
        fields = "__all__"
        
    def get_question_count(self, obj) -> int:
        return obj.questions.count()

    def get_estimated_result_release(self, obj) -> str:
        if obj.results_published:
            return "Released"
        if obj.auto_release_results:
            return (obj.end_window + timezone.timedelta(hours=5)).isoformat()
        return "Manual Release Only"

class ExamResponseSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    
    class Meta:
        model = ExamResponse
        fields = "__all__"

class ExamAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    responses = ExamResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = ExamAttempt
        fields = "__all__"

class SupportTicketSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = SupportTicket
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at', 'resolved_at']

class GlobalAnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    class Meta:
        model = GlobalAnnouncement
        fields = "__all__"
        read_only_fields = ['created_at']

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = "__all__"

class ClassScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.room_number', read_only=True)
    
    class Meta:
        model = ClassSchedule
        fields = "__all__"

class StudentPerformanceInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPerformanceInsight
        fields = "__all__"

# ==================== AI INTELLIGENCE ====================

class StudentLeadSerializer(serializers.ModelSerializer):
    ai_score_color = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentLead
        fields = "__all__"
        read_only_fields = ['probability_score', 'created_at']

    def get_ai_score_color(self, obj) -> str:
        if obj.probability_score >= 80: return '#10b981' # Green
        if obj.probability_score >= 50: return '#f59e0b' # Yellow
        return '#ef4444' # Red

class SubstituteAllocationSerializer(serializers.ModelSerializer):
    absent_teacher_name = serializers.CharField(source='absent_teacher.user.get_full_name', read_only=True)
    substitute_teacher_name = serializers.CharField(source='substitute_teacher.user.get_full_name', read_only=True)

    class Meta:
        model = SubstituteAllocation
        fields = "__all__"

# ==================== CORE ====================

from django.db import IntegrityError

class StudentSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    roll_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=True)
    parent_email = serializers.EmailField(required=False, allow_null=True)

    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"
        extra_kwargs = {
            'roll_number': {'required': False, 'allow_null': True}
        }
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'is_approved', 'user', 'parent']

    def get_photo_url(self, obj) -> str | None:
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None

    def validate_roll_number(self, value):
        if value == "":
            return None
        return value

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"detail": "Database Integrity Error: Updates would cause duplicates (Roll Number/Institution Type collision) or other constraint failure."})

    def validate(self, data):
        # Manual Uniqueness Check to prevent IntegrityError
        roll_number = data.get('roll_number', getattr(self.instance, 'roll_number', None))
        institution_type = data.get('institution_type', getattr(self.instance, 'institution_type', None))
        
        if roll_number and institution_type:
            # Check if exists
            exists = Student.objects.filter(roll_number=roll_number, institution_type=institution_type)
            if self.instance:
                exists = exists.exclude(pk=self.instance.pk)
            
            if exists.exists():
                 raise serializers.ValidationError({"roll_number": "Student with this ID already exists in this institution type."})
        
        return data

    def get_parent_name(self, obj) -> str | None:
        return obj.parent.username if obj.parent else None



class AttendenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = Attendence
        fields = "__all__"
        read_only_fields = ['created_by', 'created_at', 'updated_at', 'student_name', 'employee']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    is_superuser = serializers.BooleanField(source='user.is_superuser', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'role', 'phone', 'institution_type', 'institution_name', 'institution_logo', 'digital_signature', 'created_at', 'is_superuser', 'full_name']
        read_only_fields = ['created_at']

    def get_full_name(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ['created_at', 'updated_at']

    def get_is_overdue(self, obj) -> bool:
        return obj.status != 'PAID' and obj.due_date and obj.due_date < timezone.now().date()


class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ['created_at']

    def get_recipient_name(self, obj) -> str:
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
    
    def validate(self, data):
        # Only check availability on creation
        if not self.instance:
            book = data.get('book')
            if book and book.available_copies <= 0:
                raise serializers.ValidationError(f"The book '{book.title}' is currently unavailable (0 copies left).")
        return data

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

    def get_fullname(self, obj) -> str:
        return obj.user.get_full_name()

# ==================== ACADEMIC ====================

class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = "__all__"

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = Payroll
        fields = "__all__"

class ExamSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    batch_name = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = "__all__"

    def get_subject_name(self, obj) -> str | None:
        return obj.subject.name if obj.subject else None

    def get_batch_name(self, obj) -> str | None:
        return obj.batch.name if obj.batch else None


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    exam_name = serializers.CharField(source='exam.name', read_only=True)
    percentage = serializers.ReadOnlyField()

    class Meta:
        model = Grade
        fields = "__all__"

class ResultCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = ResultCard
        fields = "__all__"

# ==================== COACHING ====================

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    student_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Batch
        fields = "__all__"

    def get_teacher_name(self, obj) -> str:
        return obj.primary_teacher.get_full_name() if obj.primary_teacher else "N/A"


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

class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'username', 'action', 'description', 'ip_address', 'created_at']

# =====================================================
# --- NEW: ERP 2.0 ADVANCED SERIALIZERS ---
# =====================================================

class StudentDiarySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = StudentDiary
        fields = "__all__"

class StudentLeaveRequestSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = StudentLeaveRequest
        fields = "__all__"

class LMSMaterialSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = LMSMaterial
        fields = "__all__"

class LMSAssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LMSAssignment
        fields = "__all__"
        
    def get_submission_count(self, obj) -> int:
        return obj.submissions.count()

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = "__all__"

class InventoryItemSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = "__all__"
        
    def get_status(self, obj) -> str:
        if obj.quantity <= 0: return "OUT_OF_STOCK"
        if obj.quantity <= obj.min_stock_level: return "LOW_STOCK"
        return "IN_STOCK"

class InstitutionExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionExpense
        fields = "__all__"

class HolidaySerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name', read_only=True)
    start = serializers.DateField(source='date', read_only=True)
    className = serializers.SerializerMethodField()

    class Meta:
        model = Holiday
        fields = "__all__"
    
    def get_className(self, obj) -> str:
        return f"holiday-{obj.type.lower()}"

class ClassRoutineSerializer(serializers.ModelSerializer):
    batch_name = serializers.SerializerMethodField()
    start = serializers.TimeField(source='start_time', format='%H:%M', read_only=True)
    end = serializers.TimeField(source='end_time', format='%H:%M', read_only=True)

    class Meta:
        model = ClassRoutine
        fields = "__all__"
    
    def get_batch_name(self, obj) -> str:
        if obj.batch: return obj.batch.name
        if obj.grade: return f"Class {obj.grade}"
        return "General"

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Enhanced Token Serializer with:
    1. Custom Claims (Role, Avatar, ID)
    2. Last Login IP Tracking
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        
        if hasattr(user, 'profile'):
            token['role'] = user.profile.role
            token['institution_type'] = user.profile.institution_type
            if user.profile.institution_logo:
                token['institution_logo'] = user.profile.institution_logo.url
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra response data (optional, for frontend convenience)
        data['username'] = self.user.username
        data['role'] = getattr(self.user.profile, 'role', 'STUDENT') if hasattr(self.user, 'profile') else 'ADMIN'
        
        # Update Last Login IP and Log Attempt
        request = self.context.get('request')
        ip = "Unknown"
        agent = "Unknown"
        
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            agent = request.META.get('HTTP_USER_AGENT', '')[:400]

            # Update last login IP (with error handling)
            try:
                if hasattr(self.user, 'profile'):
                    self.user.profile.last_login_ip = ip
                    self.user.profile.save()  # FIX: Save profile, not user!
            except Exception as e:
                # Don't block login if profile update fails
                import logging
                logging.warning(f"Failed to update login IP for {self.user.username}: {e}")
        
        # Log SUCCESS
        try:
             LoginAttempt.objects.create(
                 username=self.user.username,
                 status='SUCCESS',
                 ip_address=ip,
                 user_agent=agent
             )
        except Exception:
             pass # Don't block login if logging fails
            
        return data
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"

class ChatConversationSerializer(serializers.ModelSerializer):
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    
    class Meta:
        model = ChatConversation
        fields = "__all__"

class ClientSubscriptionSerializer(serializers.ModelSerializer):
    days_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = ClientSubscription
        fields = "__all__"
