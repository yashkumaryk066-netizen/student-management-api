import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from student.models import Student, UserProfile

print("--- Setting up Test Data (V2) ---")
username = 'debug_admin_v2'
password = 'password123'

try:
    user = User.objects.get(username=username)
    print("User found")
except User.DoesNotExist:
    user = User.objects.create_superuser(username, 'admin@test.com', password)
    # Check if profile exists before creating
    if not UserProfile.objects.filter(user=user).exists():
        UserProfile.objects.create(user=user, role='ADMIN', institution_type='SCHOOL')
    print("User created")

# Ensure profile exists for existing users too
if not hasattr(user, 'profile'):
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'ADMIN', 'institution_type': 'SCHOOL'})

client = APIClient()
client.force_authenticate(user=user)

# Get or Create Student
student, created = Student.objects.get_or_create(
    name="Test Student V2",
    created_by=user,
    defaults={
        'age': 16,
        'dob': "2008-01-01",
        'grade': 11,
        'gender': "MALE",
        'relation': "Mother",
        'institution_type': 'SCHOOL'
    }
)
print(f"Student ID: {student.id}")

# Simulate PATCH Request (Multipart/FormData styles)
data = {
    'name': 'Updated Name V2',
    'parents_phone': '9998887776',
    'relation': 'Father',
    'institution_type': 'SCHOOL',
    'gender': 'MALE',
    'dob': '2010-01-01',
    'grade': 12,
    'age': 15,
    # Simulate empty photo being sent or not sent
}

print("\n--- Sending PATCH Request ---")
response = client.patch(f'/api/students/{student.id}/', data, format='multipart')

print(f"Status Code: {response.status_code}")
print(f"Response Data: {response.data}")
