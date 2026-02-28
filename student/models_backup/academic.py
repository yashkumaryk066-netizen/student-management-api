from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel
from .users import UserProfile

class Department(AuditModel):
    """For Institutes/Universities to manage departments (e.g., CSE, Mechanical)"""
    name = models.CharField(max_length=100)
    head_of_department = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Student(AuditModel):
    name = models.CharField(max_length=20)

    @property
    def age(self):
        from datetime import date
        today = date.today()
        if self.dob:
             return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return 0

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()
    grade = models.IntegerField()
    relation = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    INSTITUTION_TYPES = [
        ('SCHOOL', 'School'),
        ('COACHING', 'Coaching'),
        ('INSTITUTE', 'Institute/College'),
    ]
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, default='SCHOOL')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Extended Bio-Data for ID Cards
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)
    admission_number = models.CharField(max_length=50, blank=True, null=True, help_text="Unique admission ID")
    student_class = models.CharField(max_length=50, blank=True, null=True, help_text="Class/Grade/Section")
    parents_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Parent contact number")
    
    class Meta:
        unique_together = ['roll_number', 'institution_type']
    is_approved = models.BooleanField(default=True)  # For Internal Admin Approval (Staff created students)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.roll_number or 'No Roll No'})"

class Subject(AuditModel):
    """Subject/Course information"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Classroom(models.Model):
    """Classroom/Lab/Venue information"""
    ROOM_TYPES = [
        ('CLASSROOM', 'Classroom'),
        ('LAB', 'Laboratory'),
        ('AUDITORIUM', 'Auditorium'),
        ('LIBRARY', 'Library'),
        ('SPORTS', 'Sports'),
    ]
    room_number = models.CharField(max_length=50, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='CLASSROOM')
    capacity = models.IntegerField()
    floor = models.IntegerField(default=1)
    building = models.CharField(max_length=50, blank=True)
    facilities = models.TextField(blank=True, help_text="Projector, AC, Smart Board, etc.")
    
    def __str__(self):
        return f"{self.room_number} ({self.get_room_type_display()})"

class ClassSchedule(AuditModel):
    """Timetable/Schedule for classes"""
    DAYS = [
        ('MONDAY', 'Monday'),
        ('TUESDAY', 'Tuesday'),
        ('WEDNESDAY', 'Wednesday'),
        ('THURSDAY', 'Thursday'),
        ('FRIDAY', 'Friday'),
        ('SATURDAY', 'Saturday'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    teacher = models.ForeignKey(
        UserProfile, 
        on_delete=models.CASCADE, 
        related_name='teaching_schedules',
        limit_choices_to={'role': 'TEACHER'}
    )
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    section = models.CharField(max_length=50, help_text="Class 10-A, BSc-CS-I, etc.")
    academic_year = models.CharField(max_length=20, default='2024-25')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")
        super().clean()
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['classroom', 'day_of_week', 'start_time', 'academic_year']
    
    def __str__(self):
        return f"{self.section} - {self.subject.name} - {self.get_day_of_week_display()} {self.start_time}"

class Holiday(models.Model):
    HOLIDAY_TYPES = [
        ('NATIONAL', 'National Holiday'),
        ('ACADEMIC', 'Academic Holiday'),
        ('REGIONAL', 'Regional Festival'),
        ('EMERGENCY', 'Emergency/Other')
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='holidays')
    name = models.CharField(max_length=100)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Leave blank if single day")
    type = models.CharField(max_length=20, choices=HOLIDAY_TYPES, default='ACADEMIC')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        indexes = [
            models.Index(fields=['owner', 'date']),
        ]

    def __str__(self):
        return f"{self.name} ({self.date})"

class ClassRoutine(models.Model):
    """
    Routine for Coaching/Batches
    Schools/Institutes should use ClassSchedule
    """
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    
    # Link to Batch (Coaching) using string reference to avoid circular import if Batch is in coaching.py
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True, help_text="For Schools (1-12)")
    
    subject = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100, help_text="Or link to User/Staff model if needed")
    
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.day_of_week} | {self.subject} ({self.start_time})"
