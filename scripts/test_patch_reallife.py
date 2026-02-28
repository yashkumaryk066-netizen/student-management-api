import requests
import json
import os
import django
from django.conf import settings

# Setup Django just to get credentials if needed, but we'll try to just hit the running server
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# 1. Get Token for Superuser
user = User.objects.filter(is_superuser=True).first()
if not user:
    print("FATAL: No superuser found")
    exit(1)

refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

print(f"🔑 Authenticated as: {user.username} (SuperUser)")

# 2. Patch Target
# We need a valid student ID. Let's find one.
from student.models import Student
student = Student.objects.first()
if not student:
    print("FATAL: No student found to edit")
    exit(1)

student_id = student.id
url = f"http://127.0.0.1:8000/api/students/{student_id}/"
print(f"🎯 Target URL: {url}")

# 3. Payload (Simulate Form Data)
# We will create a clean dict, requests will handle multipart if we want, or json.
# Admin.js uses FormData, so let's use multipart/form-data logic or just pure data if no file.
# The previous complexity was with space in URL, let's test a clean URL request.

data = {
    "name": f"{student.name} (Updated)",
    "grade": student.grade,
    "institution_type": student.institution_type,
    "gender": student.gender,
    "dob": str(student.dob),
    "age": student.age,
    "relation": student.relation,
    "parents_phone": student.parents_phone
    # Intentionally omitted 'photo' to test 'no file' scenario
}

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
    # requests adds Content-Type/boundary automatically for 'files' or 'data'
}

print(f"🚀 Sending PATCH request...")
try:
    # Using 'data' parameter sends 'application/x-www-form-urlencoded' generally, 
    # but to match JS FormData behavior without files, often 'json' is better or 'data'. 
    # JS  sends multipart/form-data.
    # Let's try sending as multipart (by providing an empty files dict or just standard data)
    
    # Actually, to strictly mimic JS:
    # const formData = new FormData(); ==> Multipart
    # fetch(url, { body: formData })
    
    # In python requests:
    response = requests.patch(url, data=data, headers=headers)
    
    print(f"📡 Response Status: {response.status_code}")
    print(f"📄 Response Body: {response.text[:200]}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS: PATCH request accepted and processed.")
        print("Backend logic is VALID.")
    else:
        print(f"\n❌ FAILURE: Server returned {response.status_code}")

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
    print("Is the server running on port 8000?")

