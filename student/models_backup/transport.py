from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel
from .academic import Student

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
