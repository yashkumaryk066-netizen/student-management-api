import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from student.models import Student, UserProfile
from student.views import StudentDetailsView
import json

# 1. Setup Data
print("--- Setting up Test Data ---")
username = 'debug_admin_edit'
try:
    user = User.objects.get(username=username)
    print("User exists")
except User.DoesNotExist:
    user = User.objects.create_superuser(username, 'admin@test.com', 'password123')
    UserProfile.objects.create(user=user, role='ADMIN', institution_type='SCHOOL')
    print("User created")

try:
    student = Student.objects.create(
        name="Test Student",
        age=15,
        dob="2010-01-01",
        grade=10,
        gender="MALE",
        relation="Father",
        created_by=user,
        institution_type='SCHOOL'
    )
    print(f"Student created: ID {student.id}")
except Exception as e:
    student = Student.objects.last()
    print(f"Using existing student: ID {student.id}")

# 2. Simulate Request
print("\n--- Simulating PATCH Request ---")
factory = RequestFactory()
data = {
    'name': 'Updated Name',
    'parents_phone': '9998887776',
    'relation': 'Mother',
    'institution_type': 'SCHOOL',
    'gender': 'MALE',
    'dob': '2010-01-01',
    'grade': 10,
    'age': 15
}

# Use JSON content type for simplicity first, though frontend uses FormData
request = factory.patch(f'/api/students/{student.id}/', data=data, content_type='application/json')
request.user = user

view = StudentDetailsView.as_view()

try:
    response = view(request, id=student.id)
    print(f"Status Code: {response.status_code}")
    if hasattr(response, 'data'):
        print(f"Response Data: {response.data}")
    else:
        print(f"Response Content: {response.content.decode('utf-8')[:200]}...")
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()

