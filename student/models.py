from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
        name = models.CharField(max_length=20)
        age = models.PositiveBigIntegerField()
        gender = models.CharField(max_length=10)
        dob = models.DateField()
        grade = models.IntegerField()
        relation = models.CharField(max_length=50)
        user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
        parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
        
        def __str__(self):
            return self.name
        
        
class Attendence(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.name} - {self.date}"


class UserProfile(models.Model):
    """Extended user profile with role information"""
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        ('PARENT', 'Parent'),
        ('ADMIN', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Payment(models.Model):
    """Student fee payment tracking"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.student.name} - ₹{self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-update status based on due date
        if self.status != 'PAID' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)


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
    

# ==================== ACADEMIC MODULES ====================

class Subject(models.Model):
    """Subject/Course information"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
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


class ClassSchedule(models.Model):
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
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_schedules')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    section = models.CharField(max_length=50, help_text="Class 10-A, BSc-CS-I, etc.")
    academic_year = models.CharField(max_length=20, default='2024-25')
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['classroom', 'day_of_week', 'start_time', 'academic_year']
    
    def __str__(self):
        return f"{self.section} - {self.subject.name} - {self.get_day_of_week_display()} {self.start_time}"


# ==================== HOSTEL MANAGEMENT ====================

class Hostel(models.Model):
    """Hostel building information"""
    HOSTEL_TYPES = [
        ('BOYS', 'Boys Hostel'),
        ('GIRLS', 'Girls Hostel'),
        ('CO-ED', 'Co-Ed Hostel'),
    ]
    name = models.CharField(max_length=100)
    hostel_type = models.CharField(max_length=10, choices=HOSTEL_TYPES)
    total_rooms = models.IntegerField()
    warden = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_hostels')
    address = models.TextField()
    facilities = models.TextField(blank=True, help_text="WiFi, Gym, Mess, etc.")
    
    def __str__(self):
        return f"{self.name} ({self.get_hostel_type_display()})"


class Room(models.Model):
    """Hostel room information"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.IntegerField()
    capacity = models.IntegerField(default=2, help_text="Number of beds")
    current_occupancy = models.IntegerField(default=0)
    room_type = models.CharField(max_length=50, default='Standard', help_text="Standard, Deluxe, AC, Non-AC")
    
    class Meta:
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'floor', 'room_number']
    
    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"
    
    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity
    
    @property
    def available_beds(self):
        return self.capacity - self.current_occupancy


class HostelAllocation(models.Model):
    """Student hostel room allocation"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('VACATED', 'Vacated'),
        ('SUSPENDED', 'Suspended'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-check_in_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.room}"


# ==================== EVENTS MANAGEMENT ====================

class Event(models.Model):
    """College events and activities"""
    EVENT_TYPES = [
        ('ACADEMIC', 'Academic'),
        ('CULTURAL', 'Cultural'),
        ('SPORTS', 'Sports'),
        ('TECHNICAL', 'Technical'),
        ('SOCIAL', 'Social'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    max_participants = models.IntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    poster_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} - {self.get_event_type_display()}"


class EventParticipant(models.Model):
    """Event participation tracking"""
    PARTICIPATION_TYPES = [
        ('PARTICIPANT', 'Participant'),
        ('ORGANIZER', 'Organizer'),
        ('VOLUNTEER', 'Volunteer'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_participations')
    participation_type = models.CharField(max_length=20, choices=PARTICIPATION_TYPES, default='PARTICIPANT')
    registration_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name}"

