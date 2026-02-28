from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from student.models import Exam
from student.serializers import ExamSerializer
from .base import filter_by_owner, get_owner_user

from student.permissions import IsStaffWithPermission

class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.select_related('subject', 'batch').prefetch_related('grades').all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated, IsStaffWithPermission]
    required_permission = 'exams.view'

    def get_queryset(self):
        return filter_by_owner(
            self.queryset, 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
