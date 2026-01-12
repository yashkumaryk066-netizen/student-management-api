from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Ride, Driver, VehicleType
import random

def index(request):
    """
    Rider / Passenger View (Main App)
    """
    return render(request, 'rangrago/index.html')

def driver_login(request):
    """
    Driver Portal Entry
    """
    return render(request, 'rangrago/driver_login.html')

@login_required
def driver_dashboard(request):
    """
    Driver Dashboard: Toggle Active Status, View Requests
    """
    # Simply render the template, logic effectively simulated via frontend/API for now
    # Check if user is driver (in real app)
    return render(request, 'rangrago/driver_dashboard.html')

# --- API ENDPOINTS ---

@login_required
def book_ride(request):
    if request.method == 'POST':
        pickup = request.POST.get('pickup')
        drop = request.POST.get('drop')
        vehicle_type = request.POST.get('vehicle', 'auto')
        
        ride = Ride.objects.create(
            rider=request.user,
            pickup_location=pickup,
            drop_location=drop,
            pickup_lat=25.26, 
            pickup_lng=87.01,
            drop_lat=25.30,
            drop_lng=87.05,
            fare_amount=random.randint(50, 500),
            status='SEARCHING'
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
        # Simulate Driver Found Logic
        if ride.status == 'SEARCHING':
            # 80% chance to find driver quickly
            if random.random() > 0.2:
                ride.status = 'ACCEPTED'
                ride.save()
            
        return JsonResponse({
            'status': ride.status,
            'driver_name': "Rangra Pilot",
            'vehicle': "BIKE - BR-10-XY-9999",
            'eta': "2 mins",
            'otp': ride.otp
        })
    except Ride.DoesNotExist:
        return JsonResponse({'error': 'Ride not found'})
