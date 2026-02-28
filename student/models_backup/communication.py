from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel

class Notification(models.Model):
    """Notification system for different user roles"""
    RECIPIENT_TYPES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        ('PARENT', 'Parent'),
        ('ADMIN', 'Admin'),
        ('ALL', 'All'),
    ]
    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_TYPES)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient_type}"

class DemoRequest(models.Model):
    """Demo request submissions from potential customers"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONTACTED', 'Contacted'),
        ('DEMO_GIVEN', 'Demo Given'),
        ('CONVERTED', 'Converted'),
        ('DECLINED', 'Declined'),
    ]
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    institution_name = models.CharField(max_length=200, blank=True)
    institution_type = models.CharField(max_length=50, blank=True, 
                                       help_text="School, College, University, Coaching")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Admin notes")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.phone} ({self.status})"
    
    def send_notifications(self):
        """Send WhatsApp and SMS notifications to admin"""
        # Note: Imports are inside method to manage circular dependency if notifications app uses student models
        # Assuming notifications module is separate app or utility
        try:
             from notifications import whatsapp_service, sms_service
             
             # Send WhatsApp to admin
             whatsapp_result = whatsapp_service.send_demo_request_notification(
                 requester_name=self.name,
                 requester_phone=self.phone,
                 requester_email=self.email,
                 institution_name=self.institution_name
             )
             
             # Send SMS as backup
             sms_message = f"New Demo Request: {self.name} ({self.phone}) from {self.institution_name or 'Unknown'}. Check WhatsApp for details."
             sms_result = sms_service.send_message('+918356926231', sms_message)
             
             return {
                 'whatsapp': whatsapp_result,
                 'sms': sms_result
             }
        except ImportError:
            return {'error': 'Notification service not found'}

class SupportTicket(models.Model):
    """Support Ticket System for SuperAdmin"""
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SLA Tracking
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.subject} ({self.status})"

class GlobalAnnouncement(models.Model):
    """System-wide Announcements"""
    RECIPIENT_CHOICES = [
        ('ALL', 'All Users'),
        ('ADMINS', 'School Admins Only'),
        ('TEACHERS', 'Teachers Only'),
        ('NOBODY', 'Draft'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    recipient_group = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='ALL')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class GeneratedReport(AuditModel):
    REPORT_TYPES = [
        ('FINANCE', 'Financial Statement'),
        ('ACADEMIC', 'Academic Performance'),
        ('ATTENDANCE', 'Attendance Log'),
        ('HR', 'HR & Payroll'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_url = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20, default='READY')

    def __str__(self):
        return f"{self.name} ({self.status})"

class AuditLog(models.Model):
    """System-wide activity logging for monitoring"""
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs', null=True, blank=True)
    action = models.CharField(max_length=100) # e.g., 'STUDENT_CREATED', 'PAYMENT_RECEIVED'
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} by {self.created_by.username if self.created_by else 'System'} at {self.created_at}"
