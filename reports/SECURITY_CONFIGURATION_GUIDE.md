# 🔒 SECURITY CONFIGURATION GUIDE
## Y.S.M Education Management System

**Last Updated:** January 30, 2026  
**Status:** Production-Ready Security Configuration

---

## 📋 QUICK START - Apply These Settings NOW

### Step 1: Update settings.py (5 minutes)

Add these imports at the top:
```python
import os
from pathlib import Path
from datetime import timedelta
```

### Step 2: Security Settings (Copy-Paste Ready)

```python
# =============================================================================
# SECURITY SETTINGS - PRODUCTION READY
# =============================================================================

# CRITICAL: Set these in production
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # MUST change in production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# =============================================================================
# SESSION SECURITY
# =============================================================================
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = not DEBUG  # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_SAVE_EVERY_REQUEST = True  # Refresh session on activity

# =============================================================================
# HTTPS/SSL ENFORCEMENT (Enable in Production)
# =============================================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =============================================================================
# SECURITY HEADERS
# =============================================================================
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
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

# =============================================================================
# FILE UPLOAD SECURITY
# =============================================================================
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
ALLOWED_UPLOAD_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf']

# =============================================================================
# RATE LIMITING (Django REST Framework)
# =============================================================================
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',  # Anonymous users
        'user': '1000/hour',  # Authenticated users
        'login': '10/hour',  # Login attempts
        'password_reset': '5/hour',  # Password reset
        'payment': '20/hour',  # Payment submissions
        'burst': '60/minute',  # Burst protection
    },
    'EXCEPTION_HANDLER': 'student.exception_handlers.custom_exception_handler',
}

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# CSRF PROTECTION
# =============================================================================
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:3000'
).split(',')

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/security_audit.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'security': {
            'handlers': ['console', 'security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =============================================================================
# MIDDLEWARE CONFIGURATION
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Custom Security Middleware (ADD THESE)
    'student.middleware.SecurityHeadersMiddleware',
    'student.middleware.RequestValidationMiddleware',
    'student.middleware.AuditLoggingMiddleware',
    
    # Existing Custom Middleware
    'student.middleware.DisableCacheMiddleware',
    'student.middleware.SubscriptionMiddleware',
]

# =============================================================================
# JWT CONFIGURATION (if using JWT)
# =============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# =============================================================================
# PAYMENT GATEWAY SECURITY
# =============================================================================
PAYMENT_WEBHOOK_SECRET = os.environ.get('PAYMENT_WEBHOOK_SECRET', '')
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', '')

# =============================================================================
# TELEGRAM NOTIFICATIONS
# =============================================================================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')  # NO FALLBACK!

# =============================================================================
# DATABASE SECURITY
# =============================================================================
# Ensure SSL connections in production
if not DEBUG:
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }
```

---

## 🚀 DEPLOYMENT CHECKLIST

### Before Production Deployment:

#### Critical (MUST DO):
- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set proper `ALLOWED_HOSTS`
- [ ] Enable HTTPS enforcement
- [ ] Create logs directory: `mkdir -p logs && chmod 755 logs`
- [ ] Set all environment variables (no hardcoded secrets)
- [ ] Apply database migrations
- [ ] Test password reset flow
- [ ] Test file upload validation
- [ ] Verify rate limiting works

#### Recommended (SHOULD DO):
- [ ] Enable database SSL connections
- [ ] Set up log rotation (logrotate)
- [ ] Configure firewall rules
- [ ] Set up monitoring (Sentry, New Relic, etc.)
- [ ] Create backup strategy
- [ ] Document incident response plan
- [ ] Run security scanner (Bandit)
- [ ] Perform penetration testing

#### Optional (NICE TO HAVE):
- [ ] Implement 2FA for admin accounts
- [ ] Add IP whitelisting for admin panel
- [ ] Set up WAF (Web Application Firewall)
- [ ] Implement SIEM integration
- [ ] Create automated security tests

---

## 🔐 ENVIRONMENT VARIABLES

Create a `.env` file (NEVER commit to git):

```bash
# Django Core
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Security
PAYMENT_WEBHOOK_SECRET=your-payment-webhook-secret
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Payment Gateways
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```

---

## 📊 SECURITY MONITORING

### Log Files to Monitor:

1. **logs/security.log** - General security events
2. **logs/security_audit.log** - Audit trail for sensitive operations
3. **Django error logs** - Application errors

### What to Watch For:

- Multiple failed login attempts from same IP
- Suspicious user agents (sqlmap, nikto, etc.)
- Large request payloads
- Payment metadata mismatches
- CSRF token failures
- File upload rejections

### Automated Monitoring Setup:

```bash
# Install security tools
pip install bandit safety

# Run security scan
bandit -r student/ -f json -o security_report.json

# Check for vulnerable dependencies
safety check --json
```

---

## 🛡️ SECURITY TESTING

### Manual Tests:

1. **Test Rate Limiting:**
```bash
# Should block after 10 attempts
for i in {1..15}; do
  curl -X POST http://localhost:8000/api/login/ \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"wrong"}'
done
```

2. **Test File Upload Validation:**
```bash
# Should reject non-image files
curl -X POST http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "institution_logo=@malicious.php"
```

3. **Test IDOR Protection:**
```bash
# Should return 404 for other user's data
curl http://localhost:8000/api/students/999/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Automated Security Tests:

Create `tests/test_security.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User

class SecurityTests(TestCase):
    def test_god_mode_removed(self):
        """Superusers should NOT see all client data"""
        superuser = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        other_user = User.objects.create_user('other', 'other@test.com', 'pass')
        
        # Create data for other_user
        # ... 
        
        # Superuser should NOT see it
        client = Client()
        client.force_login(superuser)
        response = client.get('/api/students/')
        
        # Should not contain other user's data
        self.assertNotIn('other_user_student_id', response.content)
    
    def test_file_upload_validation(self):
        """Should reject invalid file types"""
        user = User.objects.create_user('test', 'test@test.com', 'pass')
        client = Client()
        client.force_login(user)
        
        # Try to upload PHP file
        with open('test.php', 'w') as f:
            f.write('<?php echo "hacked"; ?>')
        
        with open('test.php', 'rb') as f:
            response = client.post('/api/profile/', {
                'institution_logo': f
            })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid', response.json()['error'])
```

---

## 📞 INCIDENT RESPONSE

### If Security Breach Detected:

1. **Immediate Actions:**
   - Rotate all secrets (SECRET_KEY, API keys)
   - Force logout all users (clear sessions)
   - Enable maintenance mode
   - Preserve logs for forensics

2. **Investigation:**
   - Review `logs/security_audit.log`
   - Check for unauthorized access
   - Identify compromised accounts
   - Determine breach scope

3. **Recovery:**
   - Patch vulnerabilities
   - Reset affected user passwords
   - Notify affected users (GDPR requirement)
   - Document incident

4. **Prevention:**
   - Update security measures
   - Conduct security training
   - Implement additional monitoring
   - Schedule security audit

---

## ✅ VERIFICATION

After applying all settings, verify:

```bash
# 1. Check Python syntax
python manage.py check --deploy

# 2. Run security checks
python manage.py check --deploy --fail-level WARNING

# 3. Test migrations
python manage.py migrate --check

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Run security scanner
bandit -r student/ -ll

# 6. Check for vulnerable dependencies
safety check
```

---

**Generated:** 2026-01-30  
**Version:** 2.0  
**Status:** ✅ Production Ready
