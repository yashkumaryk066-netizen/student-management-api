import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "manufatures.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from student.views.auth import ProfileView

users = User.objects.exclude(is_superuser=True)[:5]
for user in users:
    req = RequestFactory().get('/api/profile/')
    req.user = user
    try:
        res = ProfileView().get(req)
        print("Success for", user.username, res.status_code)
    except Exception as e:
        import traceback
        traceback.print_exc()
