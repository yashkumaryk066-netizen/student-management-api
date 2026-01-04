import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from rest_framework.test import APIClient
from django.db import connections
from django.db.utils import OperationalError
from django.contrib.auth.models import User

def check_db_connection():
    try:
        c = connections['default'].cursor()
        c.execute('SELECT 1')
        print("✅ Database Connection: SUCCESS")
        return True
    except OperationalError as e:
        print(f"❌ Database Connection: FAILED - {e}")
        return False

def check_api_endpoints():
    client = APIClient()
    
    # Create a temp superuser for testing if needed, or just check public endpoints
    # For now, let's check a protected endpoint that returns 401/403 to prove it's reachable
    
    endpoints = [
        '/api/students/',
        '/api/subscription/status/',
        '/api/admin/subscriptions/overview/'
    ]
    
    print("\n🔍 Checking API Endpoints:")
    for url in endpoints:
        try:
            response = client.get(url)
            # We expect 401 Unauthorized (since no token) or 200/403
            # If 404 or 500, that's a problem.
            
            status = response.status_code
            if status in [200, 401, 403]:
                print(f"✅ {url} - Reachable (Status: {status})")
            else:
                print(f"❌ {url} - Error (Status: {status})")
                print(f"   Response: {response.content}")
        except Exception as e:
            print(f"❌ {url} - Exception: {e}")

if __name__ == '__main__':
    if check_db_connection():
        check_api_endpoints()
