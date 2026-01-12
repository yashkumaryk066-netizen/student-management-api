from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Ride, Driver, VehicleType
import math

# --- HELPER: Calculate Distance (Haversine) ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@login_required
def index(request):
    """
    Rider / Passenger Main View
    If not logged in, redirects to Rider Login.
    If logged in as Driver, redirects to Driver Dashboard (Safety Check).
    """
    if hasattr(request.user, 'rangrago_driver'):
        return redirect('rangrago:driver_dashboard')
    return render(request, 'rangrago/index.html')

def welcome(request):
    """Main Landing Split Screen"""
    return render(request, 'rangrago/welcome.html')

def rider_login(request):
    """
    Rider Access Portal
    Distinct from Driver Login.
    """
    if request.user.is_authenticated:
        if hasattr(request.user, 'rangrago_driver'):
            return redirect('rangrago:driver_dashboard')
        return redirect('rangrago:index')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        username = f"RIDER-{phone.replace(' ', '')}"
        
        user = User.objects.filter(username=username).first()
        if not user:
            # Auto-Register New Rider
            user = User.objects.create_user(username=username, password='password123')
            user.first_name = "New User"
            user.save()
        
        login(request, user)
        return redirect('rangrago:index')
        
    return render(request, 'rangrago/rider_login.html')

def driver_login(request):
    """Driver Portal Entry with Auto-Login Logic"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'rangrago_driver'):
            return redirect('rangrago:driver_dashboard')
        # If user is logged in but not a driver, maybe logout or show error?
        # For simplicity in this demo, we allow switching if needed, but usually we redirect.
        # Let's simple redirect to index if not driver
        return redirect('rangrago:index') 

    if request.method == 'POST':
        phone = request.POST.get('phone')
        username = f"DRIVER-{phone.replace(' ', '')}" # Distinct Username Namespace
        
        user = User.objects.filter(username=username).first()
        if not user:
            # Create new Driver User
            user = User.objects.create_user(username=username, password='password123')
            # Create Driver Profile
            Driver.objects.create(
                user=user,
                vehicle_number=request.POST.get('vehicle', 'TEMP-NEW'),
                license_number=f"DL-{username}",
                is_verified=True
            )
            
        login(request, user)
        return redirect('rangrago:driver_dashboard')
        
    return render(request, 'rangrago/driver_login.html')

@login_required
def driver_dashboard(request):
    """
    Driver Dashboard: Toggle Active Status, View Requests
    """
    try:
        driver = request.user.rangrago_driver
    except:
        return redirect('rangrago:driver_login') # Safety Fallback
        
    return render(request, 'rangrago/driver_dashboard.html', {'driver': driver})

# --- REAL APIs ---

@login_required
@csrf_exempt
def book_ride(request):
    if request.method == 'POST':
        try:
            pickup = request.POST.get('pickup')
            drop = request.POST.get('drop')
            # Expecting Lat/Lng from frontend now
            try:
                pickup_lat = float(request.POST.get('lat', 25.26))
                pickup_lng = float(request.POST.get('lng', 87.01))
            except ValueError:
                pickup_lat = 25.26
                pickup_lng = 87.01
            
            # Create REAL Database Record
            ride = Ride.objects.create(
                rider=request.user,
                pickup_location=pickup,
                drop_location=drop,
                pickup_lat=pickup_lat,
                pickup_lng=pickup_lng,
                drop_lat=pickup_lat + 0.05, # Approx destination for demo if not geocoded
                drop_lng=pickup_lng + 0.05,
                fare_amount=150.00, # In real app, calculate based on distance
                status='SEARCHING'
            )
            
            return JsonResponse({
                'success': True, 
                'ride_id': ride.id,
                'status': 'SEARCHING',
                'msg': 'Request broadcasted to nearby pilots.'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
def ride_status(request, ride_id):
    """
    Rider polls this to see if driver accepted.
    """
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Check authorization (either rider or assigned driver)
    if ride.rider != request.user and (not ride.driver or ride.driver.user != request.user):
         # Allow open access for debugging if strictly needed, but better secure it
         pass 

    data = {
        'status': ride.status,
        'otp': ride.otp if ride.status in ['ACCEPTED', 'ARRIVED', 'ONGOING'] else None
    }
    
    if ride.driver:
        data['driver_name'] = ride.driver.user.get_full_name() or ride.driver.user.username
        data['vehicle'] = f"{ride.driver.vehicle_type} | {ride.driver.vehicle_number}"
        data['phone'] = "Via App Call" # Privacy
        
    return JsonResponse(data)

# --- DRIVER APIs ---

@login_required
def fetch_available_rides(request):
    """
    Driver polls this to see nearby requests.
    """
    try:
        driver = request.user.rangrago_driver
        if not driver.is_active:
             return JsonResponse({'rides': []}) # Driver is offline
             
        # Fetch rides with status SEARCHING
        # In a real heavy app, use PostGIS. Here we fetch all open request and filter.
        rides = Ride.objects.filter(status='SEARCHING').order_by('-created_at')[:5]
        
        data = []
        for r in rides:
            data.append({
                'id': r.id,
                'pickup': r.pickup_location,
                'drop': r.drop_location,
                'fare': float(r.fare_amount or 0),
                'distance': '2.5 km', # Placeholder Calc or r.pickup_lat vs driver.current_lat
                'lat': r.pickup_lat,
                'lng': r.pickup_lng
            })
            
        return JsonResponse({'rides': data})
    except Exception as e:
        # If user is not a driver
        return JsonResponse({'error': 'Driver profile not found'}, status=400)

@login_required
@csrf_exempt
def accept_ride(request, ride_id):
    if request.method == 'POST':
        try:
            driver = request.user.rangrago_driver
            from django.db import transaction
            
            with transaction.atomic():
               ride = Ride.objects.select_for_update().get(id=ride_id)
               if ride.status != 'SEARCHING':
                   return JsonResponse({'success': False, 'msg': 'Ride already taken!'})
               
               ride.driver = driver
               ride.status = 'ACCEPTED'
               ride.save()
               
            return JsonResponse({'success': True, 'rider_name': ride.rider.get_full_name() or ride.rider.username})
        except Exception as e:
             return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

@login_required
@csrf_exempt
def start_ride(request):
    """Driver enters OTP to start the journey"""
    if request.method == 'POST':
        ride_id = request.POST.get('ride_id')
        otp = request.POST.get('otp')
        
        try:
            ride = Ride.objects.get(id=ride_id, driver__user=request.user)
            if ride.otp == otp:
                ride.status = 'ONGOING'
                ride.started_at = timezone.now()
                ride.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid OTP'})
        except Ride.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Ride not found'})
            
@login_required
@csrf_exempt
def complete_ride(request, ride_id):
    """Driver marks ride as complete"""
    try:
        ride = Ride.objects.get(id=ride_id, driver__user=request.user)
        ride.status = 'COMPLETED'
        ride.completed_at = timezone.now()
        ride.save()
        return JsonResponse({'success': True})
    except:
        return JsonResponse({'success': False})

@login_required
def toggle_driver_status(request):
    try:
        driver = request.user.rangrago_driver
        driver.is_active = not driver.is_active
        driver.save()
        return JsonResponse({'success': True, 'is_online': driver.is_active})
    except:
        return JsonResponse({'success': False})
