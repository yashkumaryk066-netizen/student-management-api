import requests
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# 1. Auth as SuperUser
user = User.objects.filter(is_superuser=True).first()
if not user:
    print("No SuperUser")
    exit(1)
refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

# 2. Hit Payments API
url = "http://127.0.0.1:8000/api/payments/"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

print(f"Testing {url}...")
try:
    resp = requests.get(url, headers=headers)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Payments API is FIXED")
    else:
        print(f"❌ Failed: {resp.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")
