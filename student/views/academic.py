from .base import *
from student.models import (
    Course, Batch, Enrollment, LiveClass, 
    LMSMaterial, LMSAssignment, AssignmentSubmission,
    StudentDiary, StudentLeaveRequest, Subject,
    Event, Exam, Grade, Holiday, ClassRoutine, Classroom, ClassSchedule
)
from student.serializers import (
    CourseSerializer, BatchSerializer, EnrollmentSerializer, LiveClassSerializer,
    LMSMaterialSerializer, LMSAssignmentSerializer, AssignmentSubmissionSerializer,
    StudentDiarySerializer, StudentLeaveRequestSerializer, SubjectSerializer,
    EventSerializer, ExamSerializer, GradeSerializer, HolidaySerializer, ClassRoutineSerializer,
    ClassroomSerializer, ClassScheduleSerializer
)

# --- COURSE MANAGEMENT ---

class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(Course.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(Course.objects.all(), self.request.user)

# --- BATCH MANAGEMENT ---

class BatchListCreateView(generics.ListCreateAPIView):
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = filter_by_owner(Batch.objects.select_related('course', 'primary_teacher'), self.request.user)
        course_id = self.request.query_params.get('course_id')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- ENROLLMENT ---

class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Enrollment.objects.select_related('student', 'batch', 'batch__course').all()
        
        # If student, only show own enrollments
        if hasattr(self.request.user, 'student_profile'):
             return qs.filter(student=self.request.user.student_profile)
             
        return filter_by_owner(qs, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- LIVE CLASSES ---

class LiveClassListCreateView(generics.ListCreateAPIView):
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = LiveClass.objects.select_related('teacher', 'batch').all()
        # Filter by today or future
        # qs = qs.filter(start_time__gte=timezone.now()) 
        return filter_by_owner(qs, self.request.user).order_by('start_time')

    def perform_create(self, serializer):
        serializer.save(
            created_by=get_owner_user(self.request.user),
            teacher=self.request.user
        )

class LiveClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(LiveClass.objects.all(), self.request.user)

# --- LMS & MATERIALS (ViewSets) ---

class LMSMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = LMSMaterialSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = LMSMaterial.objects.all()
        return filter_by_owner(qs, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LMSAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = LMSAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Students see assignments for their batch/grade
        user = self.request.user
        qs = LMSAssignment.objects.all()
        
        if hasattr(user, 'student_profile'):
             # Complex filter: Assignments for my batch OR my subject
             student = user.student_profile
             # For now, return all created by my institute owner
             # In future: Filter by Student's Grade/Batch
             return filter_by_owner(qs, user)
             
        return filter_by_owner(qs, user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = AssignmentSubmission.objects.all()
        if hasattr(user, 'student_profile'):
             return qs.filter(student=user.student_profile)
        return filter_by_owner(qs, user)

    def perform_create(self, serializer):
         # Auto-set student
         if hasattr(self.request.user, 'student_profile'):
             serializer.save(
                 created_by=get_owner_user(self.request.user),
                 student=self.request.user.student_profile
             )
         else:
             serializer.save(created_by=get_owner_user(self.request.user))

class StudentDiaryViewSet(viewsets.ModelViewSet):
    serializer_class = StudentDiarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = StudentDiary.objects.all()
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        return filter_by_owner(qs, user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class StudentLeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = StudentLeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        qs = StudentLeaveRequest.objects.all()
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        return filter_by_owner(qs, user)

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        if hasattr(self.request.user, 'student_profile'):
             serializer.save(
                 created_by=owner,
                 student=self.request.user.student_profile
             )
        else:
             serializer.save(created_by=owner)

class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Subject.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- CLASSROOM & SCHEDULE ---

class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Classroom.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))


class ClassScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ClassScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ClassSchedule.objects.all()
        # Additional filtering could go here (e.g., student filters by grade)
        return filter_by_owner(qs, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- EXAMS & GRADES ---

class ExamListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(Exam.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class GradeListCreateView(generics.ListCreateAPIView):
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(Grade.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- EVENTS & ROUTINES ---

class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Event.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class HolidayListCreateView(generics.ListCreateAPIView):
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Holiday model uses 'owner' field (not AuditModel created_by)
        owner = get_owner_user(self.request.user)
        return Holiday.objects.filter(owner=owner) if owner else Holiday.objects.none()

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        serializer.save(owner=owner)

class RoutineListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassRoutineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # ClassRoutine model uses 'owner' field (not AuditModel created_by)
        owner = get_owner_user(self.request.user)
        qs = ClassRoutine.objects.filter(owner=owner) if owner else ClassRoutine.objects.none()
        # Optional: filter by batch or grade
        batch_id = self.request.query_params.get('batch')
        grade = self.request.query_params.get('grade')
        if batch_id:
            qs = qs.filter(batch_id=batch_id)
        if grade:
            qs = qs.filter(grade=grade)
        return qs

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        serializer.save(owner=owner)
