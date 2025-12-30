import os
import sys

# IMPORTANT: Replace YOUR_USERNAME with your actual PythonAnywhere username
path = '/home/YOUR_USERNAME/student-management-api'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module for PythonAnywhere
os.environ['DJANGO_SETTINGS_MODULE'] = 'manufatures.pythonanywhere_settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
