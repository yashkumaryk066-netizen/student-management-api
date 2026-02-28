from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from student.models import Employee, LeaveRequest
from student.serializers import EmployeeSerializer, LeaveRequestSerializer
from .base import filter_by_owner, get_owner_user

from student.permissions import IsStaffWithPermission

class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.select_related('user', 'user__profile', 'department', 'designation').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffWithPermission]
    required_permission = 'staff.view'

    def get_queryset(self):
         return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        serializer.save(created_by=owner)

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    queryset = LeaveRequest.objects.select_related('employee', 'employee__user', 'approved_by').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
