from rest_framework import generics, permissions

from student.models import Vehicle, Route, TransportAllocation
from student.serializers import VehicleSerializer, RouteSerializer, TransportAllocationSerializer
from .base import filter_by_owner, get_owner_user

class VehicleListCreateView(generics.ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class RouteListCreateView(generics.ListCreateAPIView):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('vehicle'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class TransportAllocationListCreateView(generics.ListCreateAPIView):
    queryset = TransportAllocation.objects.select_related('student', 'route', 'vehicle').all()
    serializer_class = TransportAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('student', 'route'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
