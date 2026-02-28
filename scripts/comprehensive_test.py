#!/usr/bin/env python3
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from student.models import Student
import requests

print("="*60)
print("🔬 COMPREHENSIVE STUDENT EDIT TEST")
print("="*60)

# 1. Auth Check
print("\n[1/6] 🔑 Authentication Test...")
user = User.objects.filter(username='yash.kumar').first()
if not user:
    print("❌ FAILED: User 'yash.kumar' not found")
    print("Available users:", [u.username for u in User.objects.all()[:5]])
    sys.exit(1)

refresh = RefreshToken.for_user(user)
token = str(refresh.access_token)
print(f"✅ Token Generated for: {user.username} (SuperUser: {user.is_superuser})")

# 2. Student Exists Check
print("\n[2/6] 👨‍🎓 Student Data Check...")
student = Student.objects.first()
if not student:
    print("❌ FAILED: No students in database")
    sys.exit(1)
print(f"✅ Test Student Found: ID={student.id}, Name={student.name}")

# 3. GET Request Test (Modal Data Fetch)
print("\n[3/6] 📡 GET Request Test (Fetch Student for Edit)...")
url_get = f"http://127.0.0.1:8000/api/students/{student.id}/"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}
try:
    resp = requests.get(url_get, headers=headers, timeout=5)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ GET Success: Retrieved data for '{data.get('name')}'")
    else:
        print(f"❌ GET Failed: {resp.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"❌ GET Error: {e}")
    sys.exit(1)

# 4. PATCH Request Test (Update Student)
print("\n[4/6] 🔄 PATCH Request Test (Update Student)...")
url_patch = f"http://127.0.0.1:8000/api/students/{student.id}/"
print(f"   Target URL: {url_patch}")

# Simulate FormData from frontend
payload = {
    "name": f"{student.name} VERIFIED",
    "grade": student.grade,
    "institution_type": student.institution_type,
    "gender": "MALE",  # Ensure valid choice
    "dob": str(student.dob),
    "relation": student.relation,
    "parents_phone": student.parents_phone or ""
}

try:
    resp = requests.patch(url_patch, data=payload, headers=headers, timeout=5)
    print(f"   Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print(f"✅ PATCH Success: Update Accepted")
        updated = resp.json()
        print(f"   New Name: {updated.get('name')}")
    else:
        print(f"❌ PATCH Failed: {resp.status_code}")
        print(f"   Response: {resp.text[:300]}")
        sys.exit(1)
except Exception as e:
    print(f"❌ PATCH Error: {e}")
    sys.exit(1)

# 5. Verify Update in DB
print("\n[5/6] 💾 Database Verification...")
student.refresh_from_db()
if "VERIFIED" in student.name:
    print(f"✅ DB Updated: {student.name}")
else:
    print(f"⚠️  DB Name: {student.name} (Update may not have persisted)")

# 6. JS File Check
print("\n[6/6] 📄 JavaScript File Check...")
js_path = "/home/tele/manufatures/static/js/dashboard/admin.js"
with open(js_path, 'r') as f:
    content = f.read()
    
# Check for the space bug
if '${this.apiBaseUrl} /students/' in content:
    print("❌ CRITICAL BUG FOUND: Space in URL construction")
    print("   Line contains: '${this.apiBaseUrl} /students/'")
    print("   This causes: '/api /students/' -> '/api%20/students/' (404)")
elif '${this.apiBaseUrl}/students/' in content:
    print("✅ URL Construction: Correct (no space)")
else:
    print("⚠️  Could not verify URL pattern")

print("\n" + "="*60)
print("🎯 TEST COMPLETE")
print("="*60)
print("\n📊 SUMMARY:")
print("   - Authentication: ✅")
print("   - Student Fetch (GET): ✅")
print("   - Student Update (PATCH): ✅" if resp.status_code == 200 else "   - Student Update (PATCH): ❌")
print("   - JavaScript Syntax: ✅" if '${this.apiBaseUrl}/students/' in content else "   - JavaScript Syntax: ❌")
print("\n💡 NEXT STEP: Hard refresh browser (Ctrl+Shift+R) and test")

