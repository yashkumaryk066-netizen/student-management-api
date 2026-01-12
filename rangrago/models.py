from django.db import models
from django.conf import settings
from django.utils import timezone

class VehicleType(models.TextChoices):
    BIKE = 'BIKE', 'Rangra Bike 🏍️'
    AUTO = 'AUTO', 'Rangra Auto 🛺'
    MINI = 'MINI', 'Rangra Mini 🚗'
    SEDAN = 'SEDAN', 'Rangra Prime 🚘'
    SUV = 'SUV', 'Rangra SUV 🚙'

class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rangrago_driver')
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    current_lat = models.FloatField(default=0.0)
    current_lng = models.FloatField(default=0.0)
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices, default=VehicleType.BIKE)
    vehicle_number = models.CharField(max_length=20, unique=True)
    license_number = models.CharField(max_length=50)
    rating = models.FloatField(default=5.0)
    total_rides = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.vehicle_number}"

class Ride(models.Model):
    STATUS_CHOICES = [
        ('SEARCHING', 'Searching Driver'),
        ('ACCEPTED', 'Driver Accepted'),
        ('ARRIVED', 'Driver Arrived'),
        ('ONGOING', 'Ride in Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rides_as_rider')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='rides_as_driver')
    
    pickup_location = models.CharField(max_length=255)
    drop_location = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lng = models.FloatField()
    drop_lat = models.FloatField()
    drop_lng = models.FloatField()
    
    fare_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SEARCHING')
    otp = models.CharField(max_length=4, null=True, blank=True) # Secure Ride Start
    
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.otp:
            import random
            self.otp = str(random.randint(1000, 9999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ride #{self.id} - {self.status}"
