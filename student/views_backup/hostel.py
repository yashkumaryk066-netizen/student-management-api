from rest_framework import generics, permissions

from student.models import Hostel, Room, HostelAllocation
from student.serializers import HostelSerializer, RoomSerializer, HostelAllocationSerializer
from .base import filter_by_owner, get_owner_user

class HostelListCreateView(generics.ListCreateAPIView):
    queryset = Hostel.objects.all()
    serializer_class = HostelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class HostelAllocationListCreateView(generics.ListCreateAPIView):
    queryset = HostelAllocation.objects.all()
    serializer_class = HostelAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            self.queryset.select_related('student', 'room__hostel'),
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
