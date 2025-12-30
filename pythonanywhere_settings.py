"""
PythonAnywhere-specific Django settings
Import this in your WSGI file for PythonAnywhere deployment
"""
import os
import sys
from pathlib import Path

# Build paths
PROJECT_DIR = Path('/home/yashamishra/student-management-api/manufatures')
BASE_DIR = PROJECT_DIR.parent

# Add project directory to Python path
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import base settings
from manufatures.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-pa-zl*qy0_q$sj9&pmm=q^+82g@)1bg7-usxj-(_2vhc+bj-temp')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# PythonAnywhere domain
ALLOWED_HOSTS = ['yashamishra.pythonanywhere.com', 'localhost', '127.0.0.1']

# Database
# https://help.pythonanywhere.com/pages/UsingMySQL/
# IMPORTANT: Update YOUR_MYSQL_PASSWORD below
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yashamishra$mydb',
        'USER': 'yashamishra',
        'PASSWORD': 'ENTER_YOUR_DB_PASSWORD_HERE',  # Set this in PythonAnywhere MySQL console
        'HOST': 'yashamishra.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# CORS - adjust for your frontend
CORS_ALLOWED_ORIGINS = [
    'https://yashamishra.pythonanywhere.com',
    'https://your-frontend-domain.com',
]

# Security settings for production
SECURE_SSL_REDIRECT = False  # PythonAnywhere handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

