# ⚠️ URGENT: Site Showing 500 Error

## Current Status
**URL:** https://yashamishra.pythonanywhere.com/
**Error:** HTTP 500 (Internal Server Error)

This means the code is uploaded but there's a configuration or runtime error.

---

## 🔍 TROUBLESHOOTING STEPS

### Step 1: Check Error Logs
1. Go to PythonAnywhere → Web tab
2. Scroll down to "Log files" section
3. Click on **Error log** (yashamishra.pythonanywhere.com.error.log)
4. Look for the latest errors (bottom of file)

**Common errors to look for:**
- `ImportError` - Missing Python package
- `DatabaseError` - Database not migrated
- `Template does not exist` - Missing template files
- `Static file not found` - collectstatic not run

---

### Step 2: Most Likely Issues & Fixes

#### Issue 1: Database Not Migrated ⚠️
**Fix:** Run in Bash Console:
```bash
cd ~/student-management-api
python manage.py migrate
```

#### Issue 2: Static Files Not Collected ⚠️
**Fix:** Run in Bash Console:
```bash
cd ~/student-management-api
python manage.py collectstatic --noinput
```

#### Issue 3: Missing Python Packages ⚠️
**Fix:** Run in Bash Console:
```bash
cd ~/student-management-api
pip install -r requirements.txt --user
```

#### Issue 4: Wrong Python Version ⚠️
**Check:** Web tab → Python version should be 3.9 or higher
**Fix:** Change to Python 3.10 in Web tab dropdown

#### Issue 5: WSGI Configuration ⚠️
**Check:** Web tab → WSGI configuration file
**Should contain:**
```python
import sys
import os

# Add project directory
project_home = '/home/yashamishra/student-management-api'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'manufatures.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

### Step 3: Quick Fix Script

Run this in PythonAnywhere Bash Console:

```bash
#!/bin/bash
cd ~/student-management-api

echo "Installing dependencies..."
pip install --user django djangorestframework django-cors-headers drf-spectacular PyJWT

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser (if needed)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin123!')
    print('Superuser created!')
else:
    print('Superuser already exists')
EOF

echo "✅ Setup complete! Now reload your web app."
```

---

### Step 4: Verify Settings

Check `manufatures/settings.py` has:

```python
# IMPORTANT for PythonAnywhere:
DEBUG = False  # Set to True temporarily to see detailed errors
ALLOWED_HOSTS = ['yashamishra.pythonanywhere.com', 'localhost', '127.0.0.1']

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Database (SQLite for now)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

### Step 5: Enable DEBUG Mode Temporarily

**To see detailed error:**
1. Go to Files tab
2. Open `manufatures/settings.py`
3. Change `DEBUG = False` to `DEBUG = True`
4. Save and reload web app
5. Visit site again - you'll see detailed error
6. **IMPORTANT:** Set DEBUG back to False after fixing!

---

## 📋 DEPLOYMENT CHECKLIST

After running fixes above, verify:

- [ ] `git pull origin main` completed successfully
- [ ] `python manage.py migrate` ran without errors
- [ ] `python manage.py collectstatic --noinput` collected files
- [ ] All packages installed (check requirements.txt)
- [ ] WSGI configuration is correct
- [ ] Reload button clicked
- [ ] Error logs checked (no recent errors)

---

## 🎯 MOST COMMON SOLUTION

**90% of 500 errors are fixed by:**

```bash
cd ~/student-management-api && \
python manage.py migrate && \
python manage.py collectstatic --noinput
```

Then **Reload** the web app.

---

## 📞 IF STILL NOT WORKING

1. **Enable DEBUG mode** (see Step 5)
2. **Check error log** and copy the full error
3. The error will tell you exactly what's wrong

**Common final errors:**
- Missing `requirements.txt` → Create one with all packages
- Wrong database path → Check DATABASES setting
- Import errors → Install missing packages

---

## ✅ SUCCESS INDICATORS

When site is working, you should see:

**Homepage (/):**
- 200 OK status
- Beautiful landing page
- Contact info visible
- Pricing section

**Admin (/admin/):**
- 200 OK status
- Django admin login page
- Can login with admin/Admin123!

**API Docs (/swagger/):**
- 200 OK status
- Swagger UI visible
- List of endpoints

---

## 🚨 EMERGENCY FIX

If nothing works, create a fresh WSGI file:

```python
# /var/www/yashamishra_pythonanywhere_com_wsgi.py

import os
import sys

# Add your project directory to the sys.path
path = '/home/yashamishra/student-management-api'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'manufatures.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Save and reload.
