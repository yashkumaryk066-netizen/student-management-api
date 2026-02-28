from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from student.conf import CURRENCY_SYMBOL
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from .academic import Student

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
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', null=True, blank=True) # For Clients
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, default='FEE', db_index=True)
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
        # Auto-update status based on due date
        if self.status != 'PAID' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
        super().save(*args, **kwargs)
