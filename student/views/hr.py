from .base import *
from student.models import Department, Designation, Payroll
from student.serializers import DepartmentSerializer, DesignationSerializer, PayrollSerializer

class DepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Department.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class DesignationListCreateView(generics.ListCreateAPIView):
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Designation.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LeaveRequestViewSet(viewsets.ModelViewSet):
    from student.models import LeaveRequest
    from student.serializers import LeaveRequestSerializer
    
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            LeaveRequest.objects.select_related('employee', 'employee__user'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class PayrollViewSet(viewsets.ModelViewSet):
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            Payroll.objects.select_related('employee', 'employee__user'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
