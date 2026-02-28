"""
SECURITY SETTINGS FOR Y.S.M EDUCATION MANAGEMENT SYSTEM
Add these settings to your main settings.py file
"""

# ===========================
# SESSION SECURITY
# ===========================
# SECURITY FIX #15: Secure session management

SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True  # HTTPS only (set to False for local development)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session on activity

# ===========================
# HTTPS/SSL ENFORCEMENT
# ===========================
# SECURITY FIX #19: HTTPS enforcement (enable in production)

# Uncomment these for production:
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ===========================
# SECURITY HEADERS
# ===========================
# SECURITY FIX #20: Security headers

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# ===========================
# PASSWORD VALIDATION
# ===========================
# SECURITY FIX #22: Password complexity requirements

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased from default 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===========================
# FILE UPLOAD SECURITY
# ===========================
# SECURITY FIX #5: File upload restrictions

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
MAX_IMAGE_SIZE_MB = 5

# ===========================
# RATE LIMITING
# ===========================
# SECURITY FIX #14: Rate limiting configuration

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users
        'user': '1000/hour',  # Authenticated users
        'login': '10/hour',  # Login attempts
        'password_reset': '5/hour',  # Password reset requests
        'payment': '20/hour',  # Payment submissions
    },
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'EXCEPTION_HANDLER': 'student.exception_handlers.custom_exception_handler',
}

# ===========================
# JWT SETTINGS
# ===========================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Use your SECRET_KEY
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# ===========================
# LOGGING CONFIGURATION
# ===========================
# SECURITY FIX #23: Comprehensive audit logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security_audit.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'student.security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ===========================
# PAYMENT SECURITY
# ===========================
# SECURITY FIX #4: Payment webhook security

# Set these in environment variables, NEVER in code:
# RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET')
# STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
# EAZYPAY_WEBHOOK_SECRET = os.environ.get('EAZYPAY_WEBHOOK_SECRET')

# ===========================
# CORS SETTINGS (if using frontend)
# ===========================
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    # Add your production domains here
]

CORS_ALLOW_CREDENTIALS = True

# For development only:
# CORS_ALLOW_ALL_ORIGINS = True  # NEVER use in production!

# ===========================
# CSRF SETTINGS
# ===========================
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
CSRF_COOKIE_AGE = 31449600  # 1 year

# ===========================
# DATABASE SECURITY
# ===========================
# Use environment variables for database credentials
# NEVER commit database passwords to version control

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#         'CONN_MAX_AGE': 600,
#         'OPTIONS': {
#             'sslmode': 'require',  # Enforce SSL for database connections
#         },
#     }
# }

# ===========================
# ADMIN SECURITY
# ===========================
# Change the default admin URL
# ADMIN_URL = os.environ.get('ADMIN_URL', 'secret-admin-panel/')

# ===========================
# ALLOWED HOSTS
# ===========================
# Set properly in production
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# ===========================
# DEBUG SETTINGS
# ===========================
# NEVER set DEBUG=True in production
# DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ===========================
# SECRET KEY
# ===========================
# Generate a new secret key and store in environment variable
# SECRET_KEY = os.environ.get('SECRET_KEY')
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY environment variable must be set")
