#!/bin/bash
# Script to create a Super Admin user
echo "Creating Super Admin User..."
echo "Use the following credentials to login:"
echo "Username: admin"
echo "Password: adminpassword123"

# Create superuser non-interactively
# Since we are in a script, we use a python script to do this safely
python manage.py shell <<EOF
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
        print("✅ Superuser 'admin' created successfully.")
    else:
        u = User.objects.get(username='admin')
        u.set_password('adminpassword123')
        u.save()
        print("✅ Superuser 'admin' password updated to 'adminpassword123'.")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
