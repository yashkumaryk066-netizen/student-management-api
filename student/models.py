from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

# --- NEW SUBSCRIPTION MODEL ---
class ClientSubscription(models.Model):
    PLAN_CHOICES = [
        ('SCHOOL', 'School Management'),
        ('COACHING', 'Coaching Management'),
        ('INSTITUTE', 'Institute Management'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('SUSPENDED', 'Suspended')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True) # Last payment Ref
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan_type} ({self.status})"

    def activate(self, days=30):
        """
        Activates or Renews the subscription.
        Data Preservation: This method ONLY updates the status and dates.
        It does NOT touch any student/attendance data, ensuring strictly 'Access-Only' logic.
        """
        today = timezone.now().date()
        
        if self.status == 'ACTIVE' and self.end_date and self.end_date >= today:
             # If already active, extend from the current end date
             self.end_date = self.end_date + timezone.timedelta(days=days)
        else:
             # If expired or new, start from today
             self.status = 'ACTIVE'
             self.start_date = today
             self.end_date = today + timezone.timedelta(days=days)
             
        self.save()
        
        # Sync with UserProfile to control login/API access
        if hasattr(self.user, 'profile'):
            self.user.profile.institution_type = self.plan_type
            
            # CRITICAL: Clients are NOT Admins. They are CLIENTS.
            # Only preserve role if they are already superuser/staff, otherwise force CLIENT.
            if not self.user.is_superuser:
                 self.user.profile.role = 'CLIENT'
            
            self.user.profile.subscription_expiry = self.end_date
            self.user.profile.save()

    @property
    def days_remaining(self):
        if not self.end_date:
            return 0
        delta = self.end_date - timezone.now().date()
        return max(0, delta.days)

    def request_renewal(self):
        """Creates a pending payment/request for renewal"""
        # Logic can be handled in view, but helper is good
        pass

class Student(models.Model):
        created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_students', null=True, blank=True)
        name = models.CharField(max_length=20)
        age = models.PositiveBigIntegerField()
        gender = models.CharField(max_length=10)
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
        ('ADMIN', 'Admin'),   # System Admin (Superuser)
        ('CLIENT', 'Client'), # Subscription Owner (School/Coaching Owner)
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    
    INSTITUTION_TYPES = [
        ('SCHOOL', 'School'),
        ('COACHING', 'Coaching'),
        ('INSTITUTE', 'Institute/University'),
    ]
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, default='SCHOOL', db_index=True)
    phone = models.CharField(max_length=15, blank=True)
    subscription_expiry = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.institution_type})"


class Department(models.Model):
    """For Institutes/Universities to manage departments (e.g., CSE, Mechanical)"""
    name = models.CharField(max_length=100)
    head_of_department = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    """Student fee payment tracking"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('PENDING_VERIFICATION', 'Pending Verification'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    PAYMENT_TYPES = [
        ('FEE', 'Student Fee'),
        ('SUBSCRIPTION', 'Client Subscription Renewal'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', null=True, blank=True) # For Clients
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='FEE')
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')
    description = models.CharField(max_length=200)
    metadata = models.JSONField(null=True, blank=True, default=dict)  # Store additional payment data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        student_name = self.student.name if self.student else "No Student"
        return f"{student_name} - ₹{self.amount} - {self.status}"
    
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
        return self.allocations.filter(status='ACTIVE').count() >= self.capacity
    
    @property
    def available_beds(self):
        return self.capacity - self.allocations.filter(status='ACTIVE').count()


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

    def clean(self):
        if self.pk is None and self.room.is_full:
            raise ValidationError(f"Room {self.room.room_number} is already full!")


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
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    grade_class = models.CharField(max_length=50, help_text="Class 10, BSc-I, etc.", blank=True)
    batch = models.ForeignKey('Batch', on_delete=models.SET_NULL, null=True, blank=True, related_name='exams')
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    exam_date = models.DateField()
    duration_minutes = models.IntegerField(default=180)
    academic_year = models.CharField(max_length=20, default='2024-25')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-exam_date']
    
    def __str__(self):
        batch_info = f" ({self.batch.name})" if self.batch else f" ({self.grade_class})"
        return f"{self.name} - {self.subject.name if self.subject else 'General'}{batch_info}"


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
        ('EQUIPMENT', 'Lab Equipment'),
        ('ASSET', 'Other Asset'),
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

# ==================== TRANSPORT MANAGEMENT ====================

class Vehicle(models.Model):
    """Transport vehicle information"""
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=[('BUS', 'Bus'), ('VAN', 'Van'), ('CAR', 'Car')])
    capacity = models.IntegerField()
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)
    helper_name = models.CharField(max_length=100, blank=True)
    helper_phone = models.CharField(max_length=15, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.registration_number} ({self.vehicle_type})"


class Route(models.Model):
    """Transport route details"""
    route_name = models.CharField(max_length=100)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')
    stops = models.TextField(help_text="Comma separated stops")
    pickup_time = models.TimeField()
    drop_time = models.TimeField()
    monthly_fare = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.route_name}: {self.start_point} - {self.end_point}"


class TransportAllocation(models.Model):
    """Student transport allocation"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport_allocation')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='passengers')
    pickup_stop = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'is_active']
        
    def __str__(self):
        return f"{self.student.name} - {self.route.route_name}"


# ==================== HR & PAYROLL MANAGEMENT ====================

class HRDepartment(models.Model):
    """Organization departments"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    
    def __str__(self):
        return self.name


class Designation(models.Model):
    """Job roles/titles"""
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title


class Employee(models.Model):
    """Staff and faculty records"""
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_employees', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.ForeignKey(HRDepartment, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    joining_date = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    contract_type = models.CharField(max_length=20, choices=[('PERMANENT', 'Permanent'), ('CONTRACT', 'Contract'), ('VISITING', 'Visiting')])
    bank_account_no = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.designation})"


class LeaveRequest(models.Model):
    """Employee leave management"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=[('SICK', 'Sick Leave'), ('CASUAL', 'Casual Leave'), ('EARNED', 'Earned Leave')])
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"


class Payroll(models.Model):
    """Staff salary processing"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.CharField(max_length=20) # e.g. "January 2025"
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('PAID', 'Paid'), ('PENDING', 'Pending')], default='PENDING')
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}"
    
    def save(self, *args, **kwargs):
        self.net_salary = self.basic_salary + self.allowances - self.deductions
        super().save(*args, **kwargs)
from django.db import models
from django.contrib.auth.models import User
from .models import Student

# ==================== COACHING/INSTITUTE MANAGEMENT ====================

class Course(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Batch(models.Model):
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

class Enrollment(models.Model):
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
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_otps')
    otp_code = models.CharField(max_length=6)
    identifier = models.CharField(max_length=255) # Email or Phone
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"OTP for {self.user.username} ({self.otp_code})"


class GeneratedReport(models.Model):
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

# ==================== LIVE CLASSES (ZOOM) ====================

class LiveClass(models.Model):
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"
