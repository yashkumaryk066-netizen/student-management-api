
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

User = get_user_model()
username = 'superadmin'
email = 'superadmin@example.com'
password = 'SuperPassword123!'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username, email, password)
    print("Superuser created.")
else:
    print(f"Superuser {username} already exists. Updating password...")
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print("Password updated.")
