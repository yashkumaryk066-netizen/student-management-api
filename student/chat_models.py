from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatConversation(models.Model):
    """
    Stores AI chat conversations with auto-generated titles
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_conversations')
    title = models.CharField(max_length=200, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False, db_index=True)
    is_pinned = models.BooleanField(default=False)
    
    # Metadata
    total_messages = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    ai_model = models.CharField(max_length=50, default='gemini-2.0-flash')
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_archived']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title or f'Chat {self.id}'}"
    
    def auto_generate_title(self):
        """Generate title from first user message"""
        first_message = self.messages.filter(role='user').first()
        if first_message and not self.title:
            # Take first 50 chars of first message
            self.title = first_message.content[:50]
            if len(first_message.content) > 50:
                self.title += '...'
            self.save()


class ChatMessage(models.Model):
    """
    Individual messages in a conversation
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Assistant'),
        ('system', 'System')
    ]
    
    conversation = models.ForeignKey(
        ChatConversation, 
        related_name='messages', 
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # AI Metadata
    tokens_used = models.IntegerField(default=0)
    model = models.CharField(max_length=50, default='gemini-2.0-flash')
    response_time_ms = models.IntegerField(default=0, help_text="Response time in milliseconds")
    
    # Features
    is_edited = models.BooleanField(default=False)
    is_regenerated = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]
    
    def __str__(self):
        preview = self.content[:50]
        return f"{self.role}: {preview}..."


class UserNotification(models.Model):
    """
    Real notification system
    """
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('ai_update', 'AI Update'),
        ('system', 'System')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info', db_index=True)
    
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Optional action
    action_link = models.CharField(max_length=500, blank=True)
    action_text = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @classmethod
    def create_for_user(cls, user, title, message, notification_type='info', action_link=''):
        """Helper method to create notifications"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_link=action_link
        )
