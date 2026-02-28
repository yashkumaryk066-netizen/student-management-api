import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from student.models import UserProfile

user = User.objects.filter(is_superuser=True).first()
if not user:
    print("No superuser found")
    exit(1)

# Ensure profile
if not hasattr(user, 'profile'):
    UserProfile.objects.create(user=user, role='ADMIN', institution_type='SCHOOL')

client = APIClient()
client.force_authenticate(user=user)

print(f"Fetching Student 1 as {user.username}...")
resp = client.get('/api/students/1/')
print(f"Status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Error: {resp.data}")
else:
    print("Success. Data keys:", resp.data.keys())
    # Check for fields needed by frontend
    needed = ['name', 'relation', 'parents_phone', 'grade', 'roll_number', 'institution_type', 'gender', 'dob', 'age', 'photo', 'id']
    for n in needed:
        val = resp.data.get(n)
        print(f"Field '{n}': {val} (Type: {type(val)})")
