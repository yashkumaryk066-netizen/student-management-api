
# --- FROM base.py ---
from django.db import models, transaction
from django.contrib.auth.models import User
from student.soft_delete import SoftDeleteModel

class AuditModel(SoftDeleteModel):
    """
    Abstract base class that provides self-updating
    'created_at' and 'updated_at' fields.
    Also tracks who created the record.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='%(class)s_created', 
        null=True, 
        blank=True,
        help_text="User who created this record"
    )

    class Meta:
        abstract = True

# --- FROM users.py ---
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
            
            # Auto-set subscription plan based on purchase
            from student.plan_permissions import DEFAULT_PLAN_BY_INSTITUTION
            self.user.profile.subscription_plan = DEFAULT_PLAN_BY_INSTITUTION.get(self.plan_type, 'BASIC')
            
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

class UserProfile(models.Model):
    """Extended user profile with role information"""
    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        ('PARENT', 'Parent'),
        ('ADMIN', 'Admin'),   # System Admin (Superuser)
        ('CLIENT', 'Client'), # Subscription Owner (School/Coaching Owner)
        ('HR', 'HR/Manager'), # Staff with managed permissions
        ('AI_USER', 'AI User'), # Independent AI Platform User
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    
    INSTITUTION_TYPES = [
        ('SCHOOL', 'School'),
        ('COACHING', 'Coaching'),
        ('INSTITUTE', 'Institute/University'),
        ('EDUCATION SYSTEM', 'Education System'),
    ]
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, default='COACHING', db_index=True)
    
    SUBSCRIPTION_PLANS = [
        ('BASIC', 'Basic'),
        ('PRO', 'Pro'),
        ('ENTERPRISE', 'Enterprise'),
    ]
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='BASIC', db_index=True)
    institution_name = models.CharField(max_length=200, blank=True, null=True)
    institution_logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True, help_text="Upload your School/Institute Logo")
    digital_signature = models.ImageField(upload_to='signatures/', blank=True, null=True, help_text="Upload Administrator Digital Signature")
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True, help_text="Linked Telegram Chat ID")
    
    # Security Tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Geolocation for Attendance
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Institution Latitude")
    location_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Institution Longitude")
    attendance_radius = models.PositiveIntegerField(default=100, help_text="Allowed radius in meters for attendance")
    
    # Plan Management
    subscription_expiry = models.DateField(null=True, blank=True)
    plan_purchased_at = models.DateTimeField(null=True, blank=True)  # First purchase timestamp
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Security & Access
    # SECURITY FIX: Removed temp_password field (plaintext password storage vulnerability)
    # Use Django's built-in password reset tokens instead

    # --- GAMIFICATION (Magic Features) ---
    streak_count = models.IntegerField(default=0, help_text="Consecutive days of activity")
    last_activity_date = models.DateField(null=True, blank=True, help_text="Date of last significant activity")
    force_password_change = models.BooleanField(default=False, help_text="Force user to change password on next login")
    last_password_change = models.DateTimeField(null=True, blank=True, help_text="Track password changes for security")
    
    # Granular Permissions for Team Members
    # Structure: {'students': {'view': True, 'edit': False}, 'fees': {...}}
    permissions = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.institution_type})"
    
    def is_plan_expired(self):
        """Check if plan has expired, considering grace period"""
        # If no expiry is set, we assume it's a LIFETIME or DEV account (Active)
        if not self.subscription_expiry:
            return False
        
        # Check if today is past expiry + grace period (default 7 days hardcoded here or add field)
        grace_period = 7 
        expiry_threshold = self.subscription_expiry + timezone.timedelta(days=grace_period)
        
        return timezone.now().date() > expiry_threshold

    def is_in_grace_period(self):
        """Check if user is in grace period (Expired but within 7 days)"""
        if not self.subscription_expiry:
            return False
            
        today = timezone.now().date()
        if today <= self.subscription_expiry:
            return False # Not expired yet
            
        grace_period = 7
        expiry_threshold = self.subscription_expiry + timezone.timedelta(days=grace_period)
        return today <= expiry_threshold
    
    def extend_plan(self, days=30):
        """Extend plan by specified days"""
        if self.subscription_expiry and self.subscription_expiry > timezone.now().date():
            # Extend from current expiry
            self.subscription_expiry = self.subscription_expiry + timezone.timedelta(days=days)
        else:
            # Start from today
            self.subscription_expiry = timezone.now().date() + timezone.timedelta(days=days)
        self.save()

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

# --- FROM academic.py ---
from django.db import models
from django.contrib.auth.models import User

class Department(AuditModel):
    """For Institutes/Universities to manage departments (e.g., CSE, Mechanical)"""
    name = models.CharField(max_length=100)
    head_of_department = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Student(AuditModel):
    name = models.CharField(max_length=255)

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
    email = models.EmailField(max_length=255, help_text="Mandatory student or parent email for official communication")
    parent_email = models.EmailField(max_length=255, blank=True, null=True, help_text="Optional parent-specific email for separate notifications")
    
    class Meta:
        unique_together = ['roll_number', 'created_by']
        indexes = [
             models.Index(fields=['institution_type', 'grade']),
             models.Index(fields=['roll_number', 'institution_type']),
             models.Index(fields=['email']),
        ]
    is_approved = models.BooleanField(default=True)  # For Internal Admin Approval (Staff created students)
    is_active = models.BooleanField(default=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.roll_number or 'No Roll No'})"

    def save(self, *args, **kwargs):
        # AUTOMATIC ROLL NUMBER GENERATION (CONCURRENCY SAFE)
        if not self.roll_number:
            from django.utils import timezone
            import datetime
            
            # Identify the owner/institution scope
            owner = self.created_by
            year_short = timezone.now().strftime('%y')
            year_full = timezone.now().year
            
            # CRITICAL: Use select_for_update to lock rows and prevent race conditions
            # We filter by a dummy condition on the User model to acquire a lock for this Owner's scope
            # This ensures two admins cannot generate the same ID at the exact same millisecond.
            with transaction.atomic():
                # Lock the owner record to serialize ID generation for this specific institution
                if owner:
                     # This lock waits until other transactions affecting this owner finish
                     _lock = User.objects.select_for_update().filter(id=owner.id).first()
                
                # A. SCHOOL LOGIC: [OwnerID]-[Grade]-[Sequence]
                if self.institution_type == 'SCHOOL':
                    prefix = f"{owner.id}-{self.grade}-" if owner else f"S{self.grade}-"
                    # Find max sequence for this grade/owner
                    last_s = Student.objects.filter(
                        roll_number__startswith=prefix
                    ).order_by('-id').only('roll_number').first()
                    
                    next_num = 1
                    if last_s and last_s.roll_number:
                        try:
                            # Extract the last part of the roll number
                            next_num = int(last_s.roll_number.split('-')[-1]) + 1
                        except (ValueError, IndexError):
                            next_num = Student.objects.filter(roll_number__startswith=prefix).count() + 1
                    self.roll_number = f"{prefix}{next_num:03d}"
                    
                # B. COACHING LOGIC: ST[OwnerID]-[Year]-[Sequence]
                elif self.institution_type == 'COACHING':
                    prefix = f"ST{owner.id}-{year_short}-" if owner else f"CSH-{year_short}-"
                    # Optimized Count (Index friendly)
                    count = Student.objects.filter(institution_type='COACHING')
                    if owner:
                        count = count.filter(created_by=owner)
                    self.roll_number = f"{prefix}{count.count() + 1:04d}"
                    
                # C. INSTITUTE LOGIC: [Year][DeptCode][OwnerID][Sequence]
                elif self.institution_type == 'INSTITUTE':
                    dept_code = "GN"
                    if self.department and self.department.name:
                        dept_code = self.department.name[:2].upper()
                    
                    prefix = f"{year_full}{dept_code}{owner.id if owner else ''}"
                    q = Student.objects.filter(institution_type='INSTITUTE')
                    if owner:
                        q = q.filter(created_by=owner)
                    if self.department:
                        q = q.filter(department=self.department)
                    
                    self.roll_number = f"{prefix}{q.count() + 1:03d}"
                    
                # D. FALLBACK
                else:
                    self.roll_number = f"STU-{year_full}-{Student.objects.count() + 1:04d}"

        super().save(*args, **kwargs)

class Subject(AuditModel):
    """Subject/Course information"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['code', 'created_by']

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

# --- FROM attendance.py ---
from django.db import models
from django.contrib.auth.models import User

class Attendence(AuditModel):
    """
    Enterprise-Grade Attendance Tracking
    Supports both Students and Staff (Employees)
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True, related_name='attendance_records')
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True, related_name='attendance_records')
    date = models.DateField(db_index=True)
    is_present = models.BooleanField(default=True)
    
    # ADVANCED METADATA (Security & Auditing)
    # Store distance, lat/long used, device info, etc.
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        # Atomic uniqueness for both roles
        unique_together = [
            ("student", "date"),
            ("employee", "date"),
        ]
        indexes = [
            models.Index(fields=['date', 'is_present']),
        ]

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            # We use .filter().values() to avoid full model instantiation during status check
            old_record = Attendence.objects.filter(pk=self.pk).values('is_present').first()
            if old_record:
                old_status = old_record['is_present']
            
        super().save(*args, **kwargs)
        
        # Trigger Absence Notification
        if self.student and not self.is_present:
            # Only notify if it was newly marked absent (is_new) or changed from present to absent (old_status was True)
            if is_new or old_status:
                from student.notifications import send_erp_notification
                user_to_notify = self.student.parent if self.student.parent else self.student.user
                if user_to_notify:
                    # Async task would be better here, but for now we do direct send (buffered by engine)
                    send_erp_notification(
                        user_to_notify,
                        f"Student Absence Alert: {self.student.name}",
                        f"This is to inform you that <strong>{self.student.name}</strong> has been marked <strong>ABSENT</strong> for today ({self.date.strftime('%Y-%m-%d')}). Please contact the institutional desk for any clarifications."
                    )

    def __str__(self):
        target = self.student.name if self.student else (self.employee.user.username if self.employee else "Unknown")
        return f"{target} - {self.date} ({'Present' if self.is_present else 'Absent'})"

# --- FROM finance.py ---
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from student.conf import CURRENCY_SYMBOL
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

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
    
    PAYMENT_MODES = [
        ('ONLINE', 'Online (Razorpay/Stripe)'),
        ('CASH', 'Cash'),
        ('BANK_TRANSFER', 'Bank Transfer (NEFT/IMPS)'),
        ('UPI', 'UPI (GPay/PhonePe)'),
        ('CHEQUE', 'Cheque/DD'),
    ]

    FEE_CATEGORIES = [
        ('TUITION', 'Tuition/Monthly Fee'),
        ('ADMISSION', 'Admission/Registration Fee'),
        ('ANNUAL', 'Annual/Development Fee'),
        ('EXAM', 'Exam/Assessment Fee'),
        ('TRANSPORT', 'Transport/Bus Fee'),
        ('HOSTEL', 'Hostel/Lodging Fee'),
        ('MESS', 'Mess/Food Fee'),
        ('LIBRARY', 'Library Fee/Fine'),
        ('LAB', 'Laboratory/Practical Fee'),
        ('COMPUTER', 'Computer/IT Fee'),
        ('MATERIAL', 'Books/Study Material'),
        ('UNIFORM', 'Uniform/Accessories'),
        ('EVENT', 'Event/Picnic/Function'),
        ('SECURITY', 'Security Deposit (Refundable)'),
        ('PROSPECTUS', 'Prospectus/Form Fee'),
        ('LATE_FINE', 'Late Payment Fine'),
        ('OTHER', 'Other/Miscellaneous'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', null=True, blank=True) # For Clients
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='FEE', db_index=True)
    # Granular Category for Fees
    payment_category = models.CharField(max_length=20, choices=FEE_CATEGORIES, default='TUITION', blank=True, null=True)


    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='ONLINE')
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    description = models.CharField(max_length=200)
    metadata = models.JSONField(null=True, blank=True, default=dict)  # Store additional payment data
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        student_name = self.student.name if self.student else "No Student"
        return f"{student_name} - {CURRENCY_SYMBOL}{self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Auto-update overdue only for pending states.
        if self.status in {'PENDING', 'PENDING_VERIFICATION'} and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)

# --- FROM hostel.py ---
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Hostel(AuditModel):
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

class Room(AuditModel):
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

class HostelAllocation(AuditModel):
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

# --- FROM transport.py ---
from django.db import models
from django.contrib.auth.models import User

class Vehicle(AuditModel):
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

class Route(AuditModel):
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

class TransportAllocation(AuditModel):
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

# --- FROM library.py ---
from django.db import models
from datetime import timedelta
from django.utils import timezone
from student.conf import CURRENCY_SYMBOL

class LibraryBook(AuditModel):
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
    cover_image = models.ImageField(upload_to='library/covers/', null=True, blank=True)
    location_rack = models.CharField(max_length=50, blank=True, help_text="Shelf/Rack Location")
    shelf_location = models.CharField(max_length=50, blank=True)
    
    # Premium Fields
    description = models.TextField(blank=True, help_text="Synopsis or details")
    added_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.available_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)
    
    @property
    def is_available(self):
        return self.available_copies > 0

class BookIssue(AuditModel):
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
        """Calculate fine for overdue books"""
        if self.status == 'OVERDUE' and self.due_date < timezone.now().date():
            days_late = (timezone.now().date() - self.due_date).days
            self.fine_amount = days_late * 5  # Cost per day
        return self.fine_amount
    
    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        is_new = self.pk is None
        
        if is_new:
            # Check availability
            if self.book.available_copies <= 0:
                raise ValidationError(f"Sorry, no copies of '{self.book.title}' are available right now.")
            
            # Reduce inventory
            self.book.available_copies -= 1
            self.book.save()
            
            if not self.due_date:
                # Default 14 days
                self.due_date = timezone.now().date() + timezone.timedelta(days=14)
        else:
            # Check for Status Change (Return)
            old_instance = BookIssue.objects.get(pk=self.pk)
            if old_instance.status != 'RETURNED' and self.status == 'RETURNED':
                self.book.available_copies += 1
                self.book.save()
                self.return_date = timezone.now().date()
        
        # Check if overdue
        if self.status == 'ISSUED' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
            self.calculate_fine()
            
        super().save(*args, **kwargs)

# --- FROM hr.py ---
from django.db import models
from django.contrib.auth.models import User

class HRDepartment(AuditModel):
    """Organization departments"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    
    def __str__(self):
        return self.name

class Designation(AuditModel):
    """Job roles/titles"""
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.title

class Employee(AuditModel):
    """Staff and faculty records"""
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

class LeaveRequest(AuditModel):
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

class Payroll(AuditModel):
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

# --- FROM exam.py ---
from django.db import models
from django.contrib.auth.models import User

class Exam(AuditModel):
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
    
    class Meta:
        ordering = ['-exam_date']
    
    def __str__(self):
        batch_info = f" ({self.batch.name})" if self.batch else f" ({self.grade_class})"
        return f"{self.name} - {self.subject.name if self.subject else 'General'}{batch_info}"

class Grade(AuditModel):
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
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-exam__exam_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.marks_obtained}/{self.exam.total_marks}"
    
    @property
    def percentage(self) -> float:
        if not self.exam.total_marks or self.exam.total_marks <= 0:
            return 0
        return float((self.marks_obtained / self.exam.total_marks) * 100)
    
    def save(self, *args, **kwargs):
        # Auto-determine status
        if self.marks_obtained >= self.exam.passing_marks:
            self.status = 'PASS'
        else:
            self.status = 'FAIL'
        super().save(*args, **kwargs)

class ResultCard(AuditModel):
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

# --- FROM event.py ---
from django.db import models
from django.contrib.auth.models import User

class Event(AuditModel):
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

# --- FROM communication.py ---
from django.db import models
from django.contrib.auth.models import User

class Notification(AuditModel):
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
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient_type}"

class ResumeDownload(models.Model):
    """Tracking resume downloads for analytics"""
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Download from {self.ip_address} at {self.timestamp}"


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
        """Send notification to admin"""
        try:
             from django.contrib.auth.models import User
             from student.models import Notification
             
             admins = User.objects.filter(is_superuser=True)
             for admin in admins:
                 Notification.objects.create(
                     recipient=admin,
                     title=f"New Demo Request: {self.institution_name}",
                     message=f"{self.name} ({self.phone}) requested a demo for their institution."
                 )
             return {"status": "success"}
        except Exception as e:
            import logging
            logging.error(f"Demo notification failed: {e}")
            return {"status": "error", "message": str(e)}
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
        ('ANALYTICS_SUMMARY', 'Analytics Summary'),
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

# --- FROM coaching.py ---
from django.db import models
from django.contrib.auth.models import User

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
        if hasattr(self, 'enrolled_count'):
            return self.enrolled_count
        return self.enrollments.count()

class Enrollment(AuditModel):
    """Student Enrollment in a Batch"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DROPPED', 'Dropped'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='enrollments')
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
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='live_classes', null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_classes')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='ZOOM')
    meeting_url = models.URLField(max_length=500)
    meeting_id = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    
    # New Fields for Multi-Institution Support
    grade = models.CharField(max_length=50, blank=True, null=True, help_text="For Schools (e.g. 10)")
    section = models.CharField(max_length=50, blank=True, null=True, help_text="For Schools (e.g. A)")
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.get_platform_display()})"

# --- FROM ai.py ---
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AISubscription(models.Model):
    """
    Dedicated Subscription for Y.S.M AI (Antigravity).
    Independent of the main platform subscription.
    """
    STATUS_CHOICES = [
        ('TRIAL', 'Free Trial (7 Days)'),
        ('EXPIRED', 'Trial Expired'),
        ('PENDING', 'Payment Pending'),
        ('ACTIVE', 'Premium Active'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_subscription')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TRIAL')
    
    # Trial Tracking
    trial_start_date = models.DateTimeField(auto_now_add=True)
    
    # Premium Tracking
    premium_expiry_date = models.DateField(null=True, blank=True)
    last_payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AI-SUB: {self.user.username} - {self.status}"

    @property
    def is_access_granted(self):
        """
        Check if user has access (Trial or Premium).
        """
        if self.status == 'ACTIVE':
            # Check expiry
            if self.premium_expiry_date and self.premium_expiry_date >= timezone.now().date():
                return True
            else:
                return False
        
        elif self.status == 'TRIAL':
            # Check 7-day window
            trial_end = self.trial_start_date + timezone.timedelta(days=7)
            if timezone.now() <= trial_end:
                return True
            else:
                return False
                
        return False
    
    @property
    def check_and_update_status(self):
        """
        Auto-update status if trial expired.
        """
        if self.status == 'TRIAL':
            trial_end = self.trial_start_date + timezone.timedelta(days=7)
            if timezone.now() > trial_end:
                self.status = 'EXPIRED'
                self.save()
                return 'EXPIRED'
        
        if self.status == 'ACTIVE':
            if self.premium_expiry_date and self.premium_expiry_date < timezone.now().date():
                self.status = 'EXPIRED'
                self.save()
                return 'EXPIRED'
                
        return self.status
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
        ('system', 'System'),
        ('assistant', 'Assistant') # Compatibility with ChatMessage API
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

# =====================================================
# --- NEW: ERP 2.0 ADVANCED MODULES ---
# =====================================================

class StudentDiary(AuditModel):
    """Daily Homework/Diary module for Student-Teacher sync"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='diaries')
    grade_class = models.CharField(max_length=50)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    task_title = models.CharField(max_length=255)
    description = models.TextField(help_text="Detailed homework or task instructions")
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False) # For tracking general completion status

    class Meta:
        verbose_name_plural = "Student Diaries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task_title} ({self.grade_class})"


class LMSMaterial(AuditModel):
    """Learning Management System - Study Materials (Video/PDF)"""
    MATERIAL_TYPES = [
        ('VIDEO', 'Video Lecture URL'),
        ('DOCUMENT', 'PDF/Document'),
        ('LINK', 'External Resource Link'),
    ]
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='materials')
    grade_class = models.CharField(max_length=50, blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES)
    file_upload = models.FileField(upload_to='lms_materials/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class LMSAssignment(AuditModel):
    """Teacher assigned task with student submission capability"""
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    description = models.TextField()
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=10)
    grade_class = models.CharField(max_length=50, blank=True, help_text="Target Class/Grade")
    file_attachment = models.FileField(upload_to='assignments/', blank=True, null=True)

    def __str__(self):
        return self.title

class AssignmentSubmission(AuditModel):
    """Student uploaded response to an assignment"""
    assignment = models.ForeignKey(LMSAssignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submitted_file = models.FileField(upload_to='submissions/')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_remarks = models.TextField(blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['assignment', 'student']

class InventoryItem(AuditModel):
    """Asset & Stock management for Institutional ROI"""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, help_text="Stationary, Lab, Furniture, IT")
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, default='pcs')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_stock_level = models.IntegerField(default=5, help_text="Alert when stock falls below this")
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

class InstitutionExpense(AuditModel):
    """Financial tracking of institution costs (Bills, Salaries, etc.)"""
    EXPENSE_TYPES = [
        ('SALARY', 'Staff Salary'),
        ('UTILITY', 'Utility Bills (Electricity/Water)'),
        ('MAINTENANCE', 'Maintenance & Repairs'),
        ('STATIONARY', 'Rent & Stationery'),
        ('MARKETING', 'Marketing & Ads'),
        ('OTHER', 'Miscellaneous'),
    ]
    title = models.CharField(max_length=200)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True)
    invoice_copy = models.FileField(upload_to='expense_invoices/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"

# ==========================================
# SOVEREIGN AI INTELLIGENCE MODELS
# ==========================================

class StudentLead(AuditModel):
    """
    AI-Powered Lead Tracking for Coaching Centers.
    predict_score() calculates the probability of conversion.
    """
    STATUS_CHOICES = [
        ('NEW', 'New Enquiry'),
        ('CONTACTED', 'Contacted'),
        ('DEMO_SCHEDULED', 'Demo Scheduled'),
        ('DEMO_DONE', 'Demo Attended'),
        ('INTERESTED', 'Interested'),
        ('NEGOTIATION', 'Negotiation/Discount'),
        ('CONVERTED', 'Admitted'),
        ('LOST', 'Lost'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    source = models.CharField(max_length=50, choices=[
        ('WALK_IN', 'Walk-in'),
        ('REFERRAL', 'Referral'),
        ('SOCIAL_MEDIA', 'Facebook/Insta'),
        ('WEBSITE', 'Website'),
        ('OTHER', 'Other')
    ], default='WALK_IN')
    
    course_interest = models.ForeignKey('Course', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    
    # AI Metrics
    probability_score = models.IntegerField(default=0, help_text="AI Predicted Conversion Chance (0-100)")
    follow_up_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    next_follow_up = models.DateField(null=True, blank=True)

    def calculate_ai_score(self):
        """
        Sovereign AI Algorithm for Lead Scoring.
        """
        score = 10  # Base score
        
        # Source Weightage
        if self.source == 'REFERRAL': score += 20
        elif self.source == 'WALK_IN': score += 15
        
        # Status Progress
        if self.status == 'CONTACTED': score += 10
        elif self.status == 'DEMO_SCHEDULED': score += 20
        elif self.status == 'DEMO_DONE': score += 40
        elif self.status == 'INTERESTED': score += 60
        elif self.status == 'NEGOTIATION': score += 70
        elif self.status == 'CONVERTED': score = 100
        elif self.status == 'LOST': score = 0
            
        # Engagement
        score += (self.follow_up_count * 5)
        
        return min(score, 100)

    def save(self, *args, **kwargs):
        self.probability_score = self.calculate_ai_score()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.probability_score}%)"


class SubstituteAllocation(AuditModel):
    """
    Smart Substitute System for Schools.
    Auto-allocates free teachers when someone is on leave.
    """
    absent_teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='absences')
    date = models.DateField()
    period_slot = models.CharField(max_length=50, help_text="e.g., 2nd Period (10:00-11:00)")
    grade_class = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    
    # The substitute found by AI
    substitute_teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='substitutions')
    is_notified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Sub: {self.substitute_teacher} for {self.absent_teacher} on {self.date}"

class StudentLeaveRequest(AuditModel):
    """Universal Student Leave Management (Applied by Parent or Student)"""
    LEAVE_TYPES = [
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual / Personal'),
        ('EMERGENCY', 'Family Emergency'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests')
    applied_by = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who submitted (Parent/Student)")
    
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='CASUAL')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    
    # Optional Document Attachment (e.g. Medical Certificate)
    attachment = models.FileField(upload_to='student_leaves/', blank=True, null=True)
    
    admin_remarks = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_student_leaves')

    def __str__(self):
        return f"Leave: {self.student.name} ({self.start_date} to {self.end_date})"

    class Meta:
        ordering = ['-created_at']

# ==========================================
# ONLINE EXAM & PROCTORING SYSTEM
# ==========================================

class OnlineExam(AuditModel):
    """
    Advanced Online Examination System with Proctoring & AI
    """
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='online_exams')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='online_exams')
    grade_class = models.CharField(max_length=50, blank=True, help_text="For School/Institute classes")
    
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    
    # Timing & Duration
    start_window = models.DateTimeField(help_text="When students can start the exam")
    end_window = models.DateTimeField(help_text="Deadline to complete the exam")
    duration_minutes = models.IntegerField(default=60)
    
    # AI Generation Preferences
    num_mcq = models.IntegerField(default=5)
    num_short = models.IntegerField(default=3)
    num_long = models.IntegerField(default=2)
    knowledge_base_file = models.FileField(upload_to='exam_kb/', blank=True, null=True, help_text="Upload a book or reference for AI to generate questions")
    
    # Proctoring & Lockdown Settings
    lockdown_mode = models.BooleanField(default=True, help_text="Enforce fullscreen and tab-lock")
    require_geofencing = models.BooleanField(default=False, help_text="Exam can only start within premises")
    allow_navigation = models.BooleanField(default=False, help_text="If False, auto-submits on tab switch")
    max_violations = models.IntegerField(default=3, help_text="Number of tab-switches allowed before auto-submit")
    roll_code = models.CharField(max_length=20, default='YSM-2026', help_text="Unique Center/Exam Code for Admit Card Verification")
    assigned_batches = models.ManyToManyField('Batch', blank=True, help_text="Assign this exam to specific batches")
    admit_cards_sent = models.BooleanField(default=False)
    
    # Grading
    total_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    passing_percentage = models.IntegerField(default=33)
    
    is_published = models.BooleanField(default=False)
    results_published = models.BooleanField(default=False, help_text="Set to True after 5 hours or manually")
    auto_release_results = models.BooleanField(default=True, help_text="Automatically release results 5 hours after exam ends")

    def __str__(self):
        return f"{self.title} - {self.subject.name}"

class OnlineQuestion(AuditModel):
    """Individual questions for an Online Exam"""
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice Question'),
        ('TF', 'True / False'),
        ('SA', 'Short Answer'),
        ('LA', 'Long Answer'),
    ]
    
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='MCQ')
    
    # JSON structure for options: {"A": "Option 1", "B": "Option 2"...}
    options = models.JSONField(default=dict, blank=True, null=True)
    correct_answer = models.CharField(max_length=255, help_text="For MCQ: Key (A/B/C), For TF: True/False")
    
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    explanation = models.TextField(blank=True, help_text="AI or Teacher explanation for the correct answer")

    def __str__(self):
        return f"Q: {self.question_text[:50]}"

class ExamAttempt(AuditModel):
    """Tracking a student's attempt at an online exam"""
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    
    start_time = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Proctoring Logs
    violation_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.TextField(blank=True)
    
    # Results
    score_obtained = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_submitted = models.BooleanField(default=False)
    is_ai_graded = models.BooleanField(default=False)
    plagiarism_score = models.IntegerField(default=0, help_text="AI detected probability of external content (0-100)")
    status = models.CharField(max_length=20, default='IN_PROGRESS', choices=[
        ('IN_PROGRESS', 'Taking Exam'),
        ('SUBMITTED', 'Submitted'),
        ('TERMINATED', 'Terminated (Proctoring Violation)'),
        ('GRADED', 'Graded')
    ])
    result_notified = models.BooleanField(default=False, help_text="Email notification sent to student")

    class Meta:
        unique_together = ['exam', 'student']

    def __str__(self):
        return f"{self.student.name} - {self.exam.title}"

class ExamResponse(AuditModel):
    """Individual question responses in an attempt"""
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(OnlineQuestion, on_delete=models.CASCADE)
    marked_answer = models.TextField() # Changed from CharField to support long answers
    is_correct = models.BooleanField(default=False)
    points_awarded = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # AI Evaluation Data
    ai_feedback = models.TextField(blank=True, help_text="Constructive feedback from Sovereign AI")
    ai_accuracy_score = models.IntegerField(default=0, help_text="AI calculated accuracy (0-100)")

    class Meta:
        unique_together = ['attempt', 'question']

class StudentPerformanceInsight(AuditModel):
    """AI Generated insights based on multiple exam attempts"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='ai_insights')
    
    # JSON Data: {"Mathematics": 85, "Science": 42...}
    subject_mastery = models.JSONField(default=dict)
    weak_topics = models.JSONField(default=list)
    strong_topics = models.JSONField(default=list)
    
    # AI Recommendations
    ai_recommendation = models.TextField(blank=True)
    learning_path = models.JSONField(default=list, help_text="Multi-step roadmap generated by AI")
    
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Insights: {self.student.name}"


class LoginAttempt(models.Model):
    """
    SECURITY: Track all login attempts for Brute Force Protection & Auditing
    """
    username = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'), 
        ('FAILURE', 'Failure'), 
        ('LOCKED', 'Locked')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} - {self.status} (created_at)"
