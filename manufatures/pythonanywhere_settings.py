"""
PythonAnywhere-specific Django settings
Use: DJANGO_SETTINGS_MODULE=manufatures.pythonanywhere_settings
"""

from .settings import *

# Production mode
DEBUG = True

# Update with YOUR PythonAnywhere username
ALLOWED_HOSTS = ['yashamishra.pythonanywhere.com']

# MySQL Database (PythonAnywhere provides MySQL for free)
# Note: User must manually configure this in secret settings if using MySQL, 
# otherwise it might break if password not set. 
# For now, let's stick to SQLite if not configured, OR use the correct username pattern.
# SAFEST OPTION: Use SQLite by default unless env var set, or minimal config.
# But since this file is explicitly for PA, let's fix the HOSTS at least.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files
STATIC_ROOT = '/home/yashamishra/student-management-api/staticfiles'
STATIC_URL = '/static/'

# CORS - Update with your frontend URL
CORS_ALLOWED_ORIGINS = [
    'https://yashamishra.pythonanywhere.com',
]
CORS_ALLOW_CREDENTIALS = True

# Security settings for production
SECURE_SSL_REDIRECT = False  # PythonAnywhere handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Disable strict Whitenoise manifest storage to prevent 500 errors if collectstatic failed
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
