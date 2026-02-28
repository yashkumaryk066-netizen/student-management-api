from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .base import AuditModel
from .academic import Student

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
