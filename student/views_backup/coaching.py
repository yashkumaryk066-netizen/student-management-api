from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from student.models import Course, Batch, Enrollment, LiveClass
from student.serializers import CourseSerializer, BatchSerializer, EnrollmentSerializer, LiveClassSerializer
from .base import filter_by_owner, get_owner_user

class CourseListCreateView(generics.ListCreateAPIView):
    queryset = Course.objects.prefetch_related('batches').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.prefetch_related('batches').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.select_related('course').prefetch_related('enrollments', 'enrollments__student').all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class EnrollmentListCreateView(generics.ListCreateAPIView):
    queryset = Enrollment.objects.select_related('student', 'student__user', 'batch', 'batch__course').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LiveClassListCreateView(generics.ListCreateAPIView):
    queryset = LiveClass.objects.select_related('course', 'teacher', 'teacher__user').all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LiveClassListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    # Optional logic for active live classes specifically
    # Reusing the list create view logic implicitly or separate if needed
    # The original was APIView with filtering. Let's adapt.
    
    def get(self, request):
        from django.utils import timezone
        today = timezone.now().date()
        qs = LiveClass.objects.filter(start_time__date=today, is_active=True)
        qs = filter_by_owner(qs, request.user) 

        if request.user.profile.role == 'TEACHER':
            qs = qs.filter(teacher=request.user)

        data = LiveClassSerializer(qs, many=True).data
        if not data:
            from rest_framework.response import Response
            return Response({"code": "NO_LIVE_CLASSES", "message": "No active classes found"}, status=200)

        from rest_framework.response import Response
        return Response(data)
