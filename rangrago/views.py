from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Ride, Driver, VehicleType
import random
import time

def index(request):
    """Main Booking Interface"""
    return render(request, 'rangrago/index.html')

@login_required
def book_ride(request):
    if request.method == 'POST':
        # Simulate booking logic
        pickup = request.POST.get('pickup')
        drop = request.POST.get('drop')
        
        # Create a dummy ride
        ride = Ride.objects.create(
            rider=request.user,
            pickup_location=pickup,
            drop_location=drop,
            pickup_lat=25.26, # Placeholder lat
            pickup_lng=87.01, # Placeholder lng
            drop_lat=25.30,
            drop_lng=87.05,
            fare_amount=random.randint(50, 500)
        )
        
        return JsonResponse({
            'success': True, 
            'ride_id': ride.id,
            'otp': ride.otp,
            'fare': ride.fare_amount,
            'status': 'SEARCHING'
        })
    return JsonResponse({'success': False})

def ride_status(request, ride_id):
    try:
        ride = Ride.objects.get(id=ride_id)
        # Simulate Driver Finding Logic
        if ride.status == 'SEARCHING':
            # Randomly assign a dummy driver after a few seconds
            ride.status = 'ACCEPTED'
            ride.save()
            
        return JsonResponse({
            'status': ride.status,
            'driver_name': "Rangra Pilot",
            'vehicle': "UP-14-BW-0000",
            'eta': "2 mins"
        })
    except Ride.DoesNotExist:
        return JsonResponse({'error': 'Ride not found'})
