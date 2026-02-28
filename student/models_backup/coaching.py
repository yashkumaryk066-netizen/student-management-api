from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel
from .academic import Student, Department

class Course(AuditModel):
    """Institute Course Catalog (e.g. JEE Mains, Python Masterclass)"""
    LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='BEGINNER')
    duration_weeks = models.IntegerField(help_text="Duration in weeks")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Batch(AuditModel):
    """Specific Batch/Section of a Course"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=100, help_text="e.g. Morning Batch A, Weekend Batch")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    primary_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_batches')
    max_capacity = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.course.name}"
        
    @property
    def student_count(self):
        return self.enrollments.count()

class Enrollment(AuditModel):
    """Student Enrollment in a Batch"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    class Meta:
        unique_together = ['student', 'batch']
        
    def __str__(self):
        return f"{self.student.name} -> {self.batch.name}"

class LiveClass(AuditModel):
    """Live Class / Zoom Meeting integration"""
    PLATFORM_CHOICES = [
        ('ZOOM', 'Zoom Meeting'),
        ('GOOGLE_MEET', 'Google Meet'),
        ('TEAMS', 'Microsoft Teams'),
    ]
    
    title = models.CharField(max_length=200)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='live_classes', null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_classes')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='ZOOM')
    meeting_url = models.URLField(max_length=500)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"
