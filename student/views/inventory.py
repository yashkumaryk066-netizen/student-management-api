from .base import *
from student.models import InventoryItem
from student.serializers import InventoryItemSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InventoryItemSerializer

    def get_queryset(self):
        return filter_by_owner(InventoryItem.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))
