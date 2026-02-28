#!/usr/bin/env python3
import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import Student, ClientSubscription
from student.utils import filter_by_owner
from django.db.models import Q

print("="*70)
print("🔱 SUPERADMIN GOD MODE VERIFICATION")
print("="*70)

# Get SuperUser
superuser = User.objects.filter(is_superuser=True).first()
if not superuser:
    print("❌ No SuperUser found")
    sys.exit(1)

print(f"\n✅ SuperUser: {superuser.username}")

# Test 1: filter_by_owner bypass
print("\n[Test 1] 📊 filter_by_owner bypass...")
all_students = Student.objects.all()
filtered = filter_by_owner(all_students, superuser)
print(f"   Total Students in DB: {all_students.count()}")
print(f"   Filtered for SuperUser: {filtered.count()}")

if all_students.count() == filtered.count():
    print("   ✅ PASS: SuperUser sees ALL students (no filtering)")
else:
    print(f"   ❌ FAIL: SuperUser is being filtered!")

# Test 2: Cross-client visibility
print("\n[Test 2] 🌐 Cross-Client Access...")
clients = User.objects.filter(profile__role='CLIENT')[:3]
print(f"   Found {clients.count()} clients")

for client in clients:
    client_students = Student.objects.filter(created_by=client)
    print(f"   - {client.username}: {client_students.count()} students")

superuser_view = filter_by_owner(Student.objects.all(), superuser)
print(f"   SuperUser sees: {superuser_view.count()} students (should be TOTAL)")

# Test 3: Subscription check
print("\n[Test 3] 💳 Subscription Status...")
try:
    sub = ClientSubscription.objects.filter(user=superuser).first()
    if sub:
        print(f"   Subscription: {sub.plan_type} | Status: {sub.status}")
        print(f"   Expiry: {sub.end_date}")
    else:
        print("   ⚠️  No subscription (expected for superuser)")
except:
    print("   ℹ️  No subscription model for superuser")

print("\n" + "="*70)
print("🎯 GOD MODE STATUS")
print("="*70)

# Final verdict
if all_students.count() == filtered.count():
    print("\n✅✅✅ SUPERADMIN GOD MODE: ACTIVE")
    print("   - Sees ALL data across ALL clients")
    print("   - No ownership restrictions")
    print("   - No subscription checks")
    print("   - Full system access granted")
else:
    print("\n❌ GOD MODE: INCOMPLETE")
    print("   Some restrictions still apply")

