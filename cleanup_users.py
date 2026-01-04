import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.contrib.auth.models import User

# Keep only the superuser 'admin'
users_deleted = User.objects.exclude(username='admin').delete()
print(f"Deleted {users_deleted[0]} users. Only 'admin' remains.")
