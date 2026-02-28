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
    
    # Geolocation for Attendance
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Institution Latitude")
    location_long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Institution Longitude")
    attendance_radius = models.PositiveIntegerField(default=200, help_text="Allowed radius in meters for attendance")
    
    # Plan Management
    subscription_expiry = models.DateField(null=True, blank=True)
    plan_purchased_at = models.DateTimeField(null=True, blank=True)  # First purchase timestamp
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Security & Access
    temp_password = models.CharField(max_length=128, blank=True, null=True, help_text="Temporary password for initial setup visibility")
    force_password_change = models.BooleanField(default=False, help_text="Force user to change password on next login")
    
    # Granular Permissions for Team Members
    # Structure: {'students': {'view': True, 'edit': False}, 'fees': {...}}
    permissions = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.institution_type})"
    
    def is_plan_expired(self):
        """Check if plan has expired"""
        if not self.subscription_expiry:
            return True
        return timezone.now().date() > self.subscription_expiry
    
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
