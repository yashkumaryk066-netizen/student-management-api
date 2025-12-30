"""
PythonAnywhere-specific Django settings
Use: DJANGO_SETTINGS_MODULE=manufatures.pythonanywhere_settings
"""

from .settings import *

# Production mode
DEBUG = False

# Update with YOUR PythonAnywhere username
ALLOWED_HOSTS = ['YOUR_USERNAME.pythonanywhere.com']

# MySQL Database (PythonAnywhere provides MySQL for free)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'YOUR_USERNAME$mydb',  # Replace YOUR_USERNAME
        'USER': 'YOUR_USERNAME',  # Replace YOUR_USERNAME
        'PASSWORD': 'GET_FROM_DATABASES_TAB',  # Get from PythonAnywhere Databases tab
        'HOST': 'YOUR_USERNAME.mysql.pythonanywhere-services.com',  # Replace YOUR_USERNAME
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files
STATIC_ROOT = '/home/YOUR_USERNAME/student-management-api/staticfiles'
STATIC_URL = '/static/'

# CORS - Update with your frontend URL
CORS_ALLOWED_ORIGINS = [
    'https://YOUR_USERNAME.pythonanywhere.com',
]
CORS_ALLOW_CREDENTIALS = True

# Security settings for production
SECURE_SSL_REDIRECT = False  # PythonAnywhere handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
