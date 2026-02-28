from rest_framework import serializers
from .models import DemoRequest, Notification
import logging

logger = logging.getLogger(__name__)
class DemoRequestSerializer(serializers.ModelSerializer):
    """Serializer for demo request submissions"""
    
    class Meta:
        model = DemoRequest
        fields = ['id', 'name', 'phone', 'email', 'institution_name', 
                 'institution_type', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
    
    def create(self, validated_data):
        """Create demo request and send notifications"""
        demo_request = DemoRequest.objects.create(**validated_data)
        
        # Send notifications to admin asynchronously (or synchronously for now)
        try:
            notifications_result = demo_request.send_notifications()
            logger.info(f"Notifications sent for demo request {demo_request.id}: {notifications_result}")
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
        
        return demo_request
