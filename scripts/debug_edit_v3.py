import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth.models import User
from student.models import Student, UserProfile
from datetime import date

print("--- Setting up Test Data (V3) ---")
username = 'debug_admin_v3'
password = 'password123'

try:
    user = User.objects.get(username=username)
except User.DoesNotExist:
    user = User.objects.create_superuser(username, 'admin@test.com', password)
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user, role='ADMIN', institution_type='SCHOOL')

# Just ensure profile exists
if not hasattr(user, 'profile'):
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'ADMIN', 'institution_type': 'SCHOOL'})

client = APIClient()
client.force_authenticate(user=user)

# Create Student (excluding 'age' from defaults as it's a property)
student, created = Student.objects.get_or_create(
    name="Test Student V3",
    created_by=user,
    defaults={
        'dob': date(2008, 1, 1),
        'grade': 11,
        'gender': "MALE",
        'relation': "Mother",
        'institution_type': 'SCHOOL',
        'roll_number': 'TEST-101'
    }
)
print(f"Student ID: {student.id}, Roll: {student.roll_number}")

# Simulate PATCH Request
# Note: 'age' should NOT be sent to the backend as it's read-only. The serializer might ignore it, or error if not read_only.
data = {
    'name': 'Updated Name V3',
    'parents_phone': '9998887776',
    'relation': 'Father',
    # 'age': 16,  <-- REMOVED because it's a property
    'roll_number': 'TEST-101'  # Keeping same roll number to check uniqueness validation
}

print("\n--- Sending PATCH Request ---")
try:
    response = client.patch(f'/api/students/{student.id}/', data, format='multipart')
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")
except Exception as e:
    print(f"Client Crash: {e}")

# Test Case 2: Empty Roll Number Update (Checking the NULL fix)
print("\n--- Sending PATCH Request (Empty Roll Number) ---")
data_empty_roll = {
    'roll_number': '' 
}
try:
    response = client.patch(f'/api/students/{student.id}/', data_empty_roll, format='multipart')
    print(f"Status Code: {response.status_code}")
    print(f"Response Data: {response.data}")
except Exception as e:
    print(f"Client Crash: {e}")
