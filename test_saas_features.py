
import os
import django
from django.conf import settings
from datetime import date, timedelta
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from student.models import UserProfile, ClientSubscription
from student.middleware import SubscriptionMiddleware
from student.views import LiveClassListView
from student.super_admin_views import SuperAdminAdvancedDashboardView
import random
import string

def get_random_string(length=5):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def verify_saas_features():
    print("\n=== Verifying Advanced SaaS Features ===\n")
    factory = RequestFactory()
    
    # 1. Test Middleware - Expired User
    print("--- 1. Testing SubscriptionMiddleware Expiry ---")
    user_expired = User.objects.create_user(username=f'test_expired_{get_random_string()}', password='password')
    UserProfile.objects.create(
        user=user_expired, 
        role='CLIENT', 
        institution_type='SCHOOL',
        subscription_expiry=date.today() - timedelta(days=10) # Expired
    )
    
    # Mocking Subscription Middleware call
    # Create request to an UNSAFE method (POST)
    request = factory.post('/api/some-endpoint/')
    request.user = user_expired
    
    middleware = SubscriptionMiddleware(lambda r: None) # Mock get_response
    response = middleware(request)
    
    if hasattr(response, 'status_code') and response.status_code == 403:
        content = json.loads(response.content)
        if content.get('code') == 'SUBSCRIPTION_EXPIRED':
            print("✅ Middleware blocked expired POST request correctly.")
        else:
            print(f"❌ Middleware returned 403 but unexpected code: {content}")
    else:
        print(f"❌ Middleware failed to block. Status: {getattr(response, 'status_code', 'None')}")

    # Cleanup
    user_expired.delete()

    # 2. Test Live Class Error Handling
    print("\n--- 2. Testing Live Class Error Handling ---")
    # Using a fresh user (Active)
    user_active = User.objects.create_user(username=f'test_active_{get_random_string()}', password='password')
    UserProfile.objects.create(user=user_active, role='STUDENT', institution_type='COACHING')
    
    request_live = factory.get('/api/live-classes/')
    request_live.user = user_active
    
    view = LiveClassListView.as_view()
    response_live = view(request_live)
    
    # Data is rendered response, access via .data usually if DRF, but here we might get Response object
    if hasattr(response_live, 'data'):
        data = response_live.data
        if isinstance(data, dict) and data.get('code') == 'NO_LIVE_CLASSES':
             print("✅ Live Class returned professional error for empty list.")
        else:
             print(f"❌ Unexpected Live Class response: {data}")
    else:
         print(f"❌ Live Class view failed to return response data.")
         
    user_active.delete()

    # 3. Test Super Admin Advanced Dashboard
    print("\n--- 3. Testing Super Admin Dashboard ---")
    admin_user = User.objects.create_superuser(username=f'test_super_admin_{get_random_string()}', email='a@a.com', password='password')
    
    request_admin = factory.get('/api/admin/advanced/dashboard/')
    request_admin.user = admin_user
    
    view_admin = SuperAdminAdvancedDashboardView.as_view()
    response_admin = view_admin(request_admin)
    
    if response_admin.status_code == 200:
        data = response_admin.data
        if 'stats' in data and 'health' in data:
            print("✅ Super Admin Dashboard returned expected metrics (Advanced Architecture).")
        else:
             print(f"❌ Dashboard missing keys: {data.keys()}")
    else:
        print(f"❌ Dashboard failed status: {response_admin.status_code}")
        
    admin_user.delete()

if __name__ == "__main__":
    verify_saas_features()
