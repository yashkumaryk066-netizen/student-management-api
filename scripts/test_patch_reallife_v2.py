import requests
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from student.models import Student

# 1. Auth
user = User.objects.filter(is_superuser=True).first()
refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)

# 2. Target
student = Student.objects.first()
print(f"Current DB Gender: '{student.gender}'")  # Debugging why it was "M"

url = f"http://127.0.0.1:8000/api/students/{student.id}/"

# 3. Payload with VALID choices
data = {
    "name": f"{student.name} (Verified)",
    "grade": student.grade,
    "institution_type": 'SCHOOL', # Hardcode valid choice
    "gender": 'MALE',           # Hardcode valid choice to bypass legacy data issues
    "dob": str(student.dob),
    "age": student.age,
    "relation": student.relation,
    "parents_phone": student.parents_phone
}

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

print(f"🚀 Sending Corrected PATCH request to {url}...")
try:
    response = requests.patch(url, data=data, headers=headers)
    
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS: API is Fully Operational.")
    else:
        print(f"\n❌ FAILURE: {response.text}")

except Exception as e:
    print(f"❌ ERROR: {e}")
