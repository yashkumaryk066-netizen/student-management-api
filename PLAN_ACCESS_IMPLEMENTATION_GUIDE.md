# 🎯 ADVANCE LEVEL PLAN ACCESS SYSTEM - IMPLEMENTATION GUIDE

## ✅ What Has Been Implemented

### 1. **Enhanced UserProfile Model** (`student/models.py`)
New fields added for better plan tracking:
- `institution_name` - Client's institution name
- `address` - Institution address  
- `plan_purchased_at` - Timestamp of first purchase (for renewal detection)
- `is_active` - Account active status
- `is_plan_expired()` - Method to check if plan expired
- `extend_plan(days=30)` - Method to extend subscription

### 2. **Plan-Based Feature Access** (`student/permissions.py`)
```python
PLAN_FEATURES = {
    'SCHOOL': ['dashboard', 'students', 'exams', 'attendance', 'transport', 
               'hostel', 'parents', 'teachers', 'reports', 'payments', 
               'events', 'settings', 'subscription', 'hr'],
    
    'COACHING': ['dashboard', 'students', 'courses', 'live_classes',
                 'attendance', 'reports', 'payments', 'events', 
                 'settings', 'subscription'],
    
    'INSTITUTE': ['dashboard', 'students', 'exams', 'courses', 'attendance',
                  'transport', 'hostel', 'parents', 'teachers', 'reports',
                  'payments', 'lab', 'library', 'hr', 'events', 'settings',
                  'subscription', 'logs', 'users', 'live_classes']
}
```

### 3. **Frontend Plan Access** (`static/js/sidebar-manager.js`)
- Synced with backend `PLAN_FEATURES`
- Dynamic sidebar hiding/showing based on plan
- Lock icon for inaccessible modules
- Upgrade modal for locked features

### 4. **Payment Approval System** (See `PAYMENT_APPROVAL_IMPROVEMENT.py`)
#### Super Admin Workflow:
1. Client makes payment (recorded in `Payment` model)
2. Super Admin goes to Django Admin → Payments
3. Selects payment → Actions → "Approve Payment & Activate Plan"

#### System Actions:
**First Purchase:**
- ✅ Activates 30-day subscription
- ✅ Sets `plan_purchased_at` timestamp
- ✅ Sends email with **login credentials**
- ✅ Grants access to plan-specific features only

**Renewal:**
- ✅ Extends subscription by 30 days
- ✅ NO new credentials sent
- ✅ Sends **renewal confirmation** email
- ✅ Maintains same username/password

---

## 📋 DEPLOYMENT STEPS

### Step 1: Run Database Migrations
```bash
cd ~/student-management-api
source venv/bin/activate
python manage.py migrate
```

### Step 2: Update Admin Payment Approval Function
Replace the `approve_payment_and_renew` function in `student/admin.py` (lines 107-138) with the improved version from `PAYMENT_APPROVAL_IMPROVEMENT.py`

### Step 3: Configure Email Settings
In `.env` or `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Y.S.M Education <your-email@gmail.com>'
```

### Step 4: Collect Static Files & Reload
```bash
python manage.py collectstatic --noinput
# Then reload web app from PythonAnywhere dashboard
```

---

## 🎬 TESTING WORKFLOW

### Test 1: New Client Approval
1. Create a test user (or use DemoRequest conversion)
2. Create a Payment for that user with:
   - `payment_type` = 'SUBSCRIPTION'
   - `user` = test_user
   - `amount` = 5000
3. Go to Admin → Payments → Select payment → Approve
4. **Expected:**
   - User receives email with credentials
   - Subscription active for 30 days
   - Can login and see ONLY their plan features

### Test 2: Renewal Approval
1. Same user makes another payment after 15 days
2. Approve that payment
3. **Expected:**
   - Email says "Subscription Renewed"
   - NO credentials in email
   - Subscription extended by 30 days from current expiry

### Test 3: Plan Expiry Check
```python
# In Django shell
from django.contrib.auth.models import User
user = User.objects.get(username='test_client')
user.profile.is_plan_expired()  # Should return True/False
```

---

## 🔐 SECURITY & ACCESS CONTROL

### How It Works:
1. **Backend Check** (`HasPlanAccess` permission):
   - Every API view checks user's plan
   - Returns 403 if feature not in plan

2. **Frontend Check** (`sidebar-manager.js`):
   - Fetches plan from `/api/plan/features/`
   - Hides/locks unavailable modules
   - Shows upgrade modal on click

3. **Super Admin Bypass**:
   - `is_superuser=True` users have ALL access
   - No plan restrictions

---

## 📧 EMAIL TEMPLATES

### First Purchase Email:
- Subject: "🎉 Welcome! Your {PLAN} Plan is Active"
- Contains: Username, Password, Login URL
- Mentions: Plan-specific features only

### Renewal Email:
- Subject: "✅ Subscription Renewed - {PLAN} Plan"
- Contains: New expiry date, amount paid
- NO credentials

---

## 🚀 NEXT STEPS (Optional Enhancements)

1. **Auto-Expiry Checker** (Cron job):
   - Daily check for expired subscriptions
   - Auto-suspend access

2. **Grace Period**:
   - 7 days grace after expiry
   - Read-only access

3. **Plan Upgrade**:
   - Allow clients to upgrade mid-subscription
   - Prorated billing

4. **WhatsApp Notifications**:
   - Send renewal reminders via WhatsApp
   - Payment confirmations

---

## 📝 MANUAL OVERRIDE (Admin)

Super Admin can manually:
- Extend/Reduce subscription days
- Change user's plan type
- Force activate/suspend

Django Admin → User Profiles → Edit

---

## ⚠️ IMPORTANT NOTES

1. **Migration Required**: Run `python manage.py migrate` before testing
2. **Email Setup**: Configure SMTP in settings for emails to work
3. **Plan Sync**: Backend PLAN_FEATURES must match frontend PLAN_ACCESS
4. **First Login**: Users MUST change password after first login (security)
5. **Data Preservation**: Renewal does NOT delete user's data (students, exams, etc.)

---

## 🎯 CURRENT STATUS

✅ Database schema updated (new migration created)
✅ UserProfile model enhanced  
✅ Plan-wise access rules defined
✅ Frontend sidebar synchronization
✅ Payment approval logic ready
✅ Email templates created

⏳ PENDING:
- Apply improved payment approval function to admin.py
- Configure email SMTP settings
- Test on live server
- PythonAnywhere deployment

---

**Created**: 2026-01-07
**Version**: 1.0 - Advance Level Implementation
**System**: Y.S.M ADVANCE EDUCATION SYSTEM
