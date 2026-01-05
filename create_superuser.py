
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manufatures.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    if User.objects.filter(username="admin").exists():
        user = User.objects.get(username="admin")
        user.set_password("admin123")
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print("Updated existing 'admin' user password to 'admin123'")
    else:
        User.objects.create_superuser("admin", "admin@example.com", "admin123")
        print("Created new superuser: admin / admin123")
except Exception as e:
    print(f"Error: {e}")
