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
