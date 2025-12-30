import os
import sys

# Add your project directory to the sys.path
path = '/home/yashamishra/student-management-api'
if path not in sys.path:
    sys.path.insert(0, path)

# Set Django settings module for PythonAnywhere
os.environ['DJANGO_SETTINGS_MODULE'] = 'manufatures.pythonanywhere_settings'

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

