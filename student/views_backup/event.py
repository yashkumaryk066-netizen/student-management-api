from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from student.models import Event
from student.serializers import EventSerializer
from .base import filter_by_owner, get_owner_user

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.prefetch_related('participants').all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(self.queryset, self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
