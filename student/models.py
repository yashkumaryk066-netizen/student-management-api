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


# ==================== DEMO REQUEST ====================

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

# ==================== EXAM & GRADING SYSTEM ====================

class Exam(models.Model):
    """Examination/Test configuration"""
    EXAM_TYPES = [
        ('UNIT', 'Unit Test'),
        ('MIDTERM', 'Mid-Term'),
        ('FINAL', 'Final Exam'),
        ('PRACTICAL', 'Practical'),
        ('ASSIGNMENT', 'Assignment'),
    ]
    
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    grade_class = models.CharField(max_length=50, help_text="Class 10, BSc-I, etc.")
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    exam_date = models.DateField()
    duration_minutes = models.IntegerField(default=180)
    academic_year = models.CharField(max_length=20, default='2024-25')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"{self.name} - {self.subject.name} ({self.grade_class})"


class Grade(models.Model):
    """Student exam grades/marks"""
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('ABSENT', 'Absent'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-exam__exam_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.marks_obtained}/{self.exam.total_marks}"
    
    @property
    def percentage(self):
        return (self.marks_obtained / self.exam.total_marks) * 100
    
    def save(self, *args, **kwargs):
        # Auto-determine status
        if self.marks_obtained >= self.exam.passing_marks:
            self.status = 'PASS'
        else:
            self.status = 'FAIL'
        super().save(*args, **kwargs)


class ResultCard(models.Model):
    """Consolidated result card for a student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='result_cards')
    academic_year = models.CharField(max_length=20)
    semester_term = models.CharField(max_length=50, help_text="Semester 1, Term 2, etc.")
    grade_class = models.CharField(max_length=50)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2)
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    result_status = models.CharField(max_length=20, choices=[('PASS', 'Pass'), ('FAIL', 'Fail'), ('PROMOTED', 'Promoted')])
    remarks = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'semester_term']
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.semester_term} ({self.academic_year})"


# ==================== LIBRARY MANAGEMENT ====================

class LibraryBook(models.Model):
    """Library book catalog"""
    CATEGORIES = [
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('TEXTBOOK', 'Textbook'),
        ('REFERENCE', 'Reference'),
        ('MAGAZINE', 'Magazine'),
        ('JOURNAL', 'Journal'),
    ]
    
    isbn = models.CharField(max_length=13, unique=True, help_text="ISBN-10 or ISBN-13")
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    published_year = models.IntegerField()
    edition = models.CharField(max_length=50, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shelf_location = models.CharField(max_length=50, blank=True)
    added_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.available_copies > 0


class BookIssue(models.Model):
    """Book issue/return tracking"""
    STATUS_CHOICES = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('LOST', 'Lost'),
    ]
    
    book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ISSUED')
    fine_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.student.name} ({self.status})"
    
    def calculate_fine(self):
        """Calculate fine for overdue books (₹5/day)"""
        if self.status == 'OVERDUE' and self.due_date < timezone.now().date():
            from datetime import timedelta
            days_late = (timezone.now().date() - self.due_date).days
            self.fine_amount = days_late * 5  # ₹5 per day
        return self.fine_amount
    
    def save(self, *args, **kwargs):
        # Update book availability
        if self.pk is None:  # New issue
            self.book.available_copies -= 1
            self.book.save()
        
        # Check if overdue
        if self.status == 'ISSUED' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
            self.calculate_fine()
        
        # Mark as returned and restore availability
        if self.return_date and self.status != 'RETURNED':
            self.status = 'RETURNED'
            self.book.available_copies += 1
            self.book.save()
        
        super().save(*args, **kwargs)
