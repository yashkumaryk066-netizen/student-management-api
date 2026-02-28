#!/bin/bash
# Script to create a Super Admin user AND Profile
echo "Creating Super Admin User & Profile..."
echo "Use the following credentials to login:"
echo "Username: admin"
echo "Password: adminpassword123"

python manage.py shell <<EOF
from django.contrib.auth.models import User
from student.models import UserProfile

try:
    # 1. Create/Get User
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
        print("✅ Superuser 'admin' created successfully.")
    else:
        user = User.objects.get(username='admin')
        user.set_password('adminpassword123')
        user.save()
        print("✅ Superuser 'admin' password updated.")

    # 2. Create/Update Profile
    # Check if profile exists
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user, role='ADMIN', phone='+919999999999')
        print("✅ Admin 'UserProfile' created successfully.")
    else:
        user.profile.role = 'ADMIN'
        user.profile.save()
        print("✅ Admin 'UserProfile' updated to role ADMIN.")

except Exception as e:
    print(f"❌ Error: {e}")
EOF
