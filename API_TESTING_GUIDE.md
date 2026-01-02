# 🔧 Complete API Testing Guide - NextGen ERP

## 📋 Overview
This guide will help you test all APIs on the live server: **https://yashamishra.pythonanywhere.com/**

---

## 🔑 Step 1: Get Authentication Token

### Create Admin User (via Django Admin Panel)
1. Go to: https://yashamishra.pythonanywhere.com/admin/
2. Login with superuser credentials
3. Go to "Users" → "Add User"
4. Create user with:
   - Username: `testadmin`
   - Password: `testpass123`
5. Then go to "User profiles" → "Add User profile"
   - Select the user
   - Role: `ADMIN`
   - Phone: `+919999999999`

### Get JWT Token via API
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testadmin", "password": "testpass123"}'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Copy the `access` token - you'll need it for all authenticated requests!

---

## 📚 Step 2: Test Student APIs

### 1. Create Student ✅
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/students/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Rahul Kumar",
    "age": 18,
    "gender": "Male",
    "dob": "2007-05-15",
    "grade": 12,
    "relation": "None"
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "name": "Rahul Kumar",
  "age": 18,
  "gender": "Male",
  "dob": "2007-05-15",
  "grade": 12,
  "relation": "None",
  "user": null,
  "parent": null,
  "parent_name": null
}
```

### 2. List All Students ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/students/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Search Students ✅
```bash
curl -X GET "https://yashamishra.pythonanywhere.com/api/students/?search=Rahul" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Get Student Details ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/students/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Update Student ✅
```bash
curl -X PUT https://yashamishra.pythonanywhere.com/api/students/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Rahul Kumar Updated",
    "age": 19,
    "gender": "Male",
    "dob": "2007-05-15",
    "grade": 12,
    "relation": "None"
  }'
```

### 6. Delete Student ✅
```bash
curl -X DELETE https://yashamishra.pythonanywhere.com/api/students/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📅 Step 3: Test Attendance APIs

### 1. Mark Attendance ✅
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/attendence/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "student": 1,
    "date": "2026-01-01",
    "is_present": true
  }'
```

**Note**: `date` is optional - defaults to today if not provided

### 2. List All Attendance ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/attendence/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Get Attendance Details ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/attendence/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Update Attendance ✅
```bash
curl -X PUT https://yashamishra.pythonanywhere.com/api/attendence/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "student": 1,
    "date": "2026-01-01",
    "is_present": false
  }'
```

### 5. Delete Attendance ✅
```bash
curl -X DELETE https://yashamishra.pythonanywhere.com/api/attendence/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Get Today's Attendance Summary ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/students/today/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "date": "2026-01-01",
  "total_students": 10,
  "present_count": 8,
  "absent_count": 2,
  "present_students": [...],
  "absent_students": [...]
}
```

---

## 💰 Step 4: Test Payment APIs

### 1. Create Payment ✅
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/payments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "student": 1,
    "amount": 5000.00,
    "due_date": "2026-01-15",
    "description": "Tuition Fee - January 2026",
    "status": "PENDING"
  }'
```

### 2. List All Payments ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/payments/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Mark Payment as Paid ✅
```bash
curl -X PUT https://yashamishra.pythonanywhere.com/api/payments/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"mark_paid": true}'
```

---

## 🔔 Step 5: Test Notification APIs

### 1. List Notifications ✅
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/notifications/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Create Notification (Admin/Teacher Only) ✅
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/notifications/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "recipient_type": "ALL",
    "title": "Holiday Notice",
    "message": "School will remain closed tomorrow due to public holiday."
  }'
```

### 3. Mark Notification as Read ✅
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/notifications/1/read/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Step 6: Test Dashboard APIs

### 1. Student Dashboard ✅
(Need to be logged in as a student)
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/dashboard/student/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 2. Teacher Dashboard ✅
(Need to be logged in as a teacher)
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/dashboard/teacher/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Parent Dashboard ✅
(Need to be logged in as a parent)
```bash
curl -X GET https://yashamishra.pythonanywhere.com/api/dashboard/parent/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📝 Step 7: Test Demo Request (Public API - No Auth Required)

```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/demo-request/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+919876543210",
    "email": "john@example.com",
    "institution_name": "ABC School",
    "institution_type": "School",
    "message": "I want a personalized demo"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Thank you for your interest! We will contact you shortly.",
  "data": {...}
}
```

**This will trigger:**
- WhatsApp notification to admin (+918356926231)
- SMS backup to admin

---

## 🎯 Using Swagger UI (Easiest Way!)

### Option 1: Use Browser Swagger Interface
1. Go to: https://yashamishra.pythonanywhere.com/swagger/
2. Click "Authorize" button (top right)
3. Get token from Step 1
4. Enter: `Bearer YOUR_ACCESS_TOKEN`
5. Click "Authorize"
6. Now test all APIs directly from browser!

**Swagger will automatically:**
- Add authentication headers
- Show request/response examples
- Validate input data
- Display API documentation

---

## 🚨 Common Issues & Solutions

### Issue 1: "Authentication credentials were not provided"
**Solution**: Add Authorization header: `Authorization: Bearer YOUR_ACCESS_TOKEN`

### Issue 2: "Token has expired"
**Solution**: Get new token using refresh token:
```bash
curl -X POST https://yashamishra.pythonanywhere.com/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

### Issue 3: "Permission denied"
**Solution**: Make sure you're using correct role (Admin/Teacher for creating students)

### Issue 4: "Attendance already marked"
**Solution**: Student can only have one attendance record per date (unique constraint)

---

## ✅ Full Test Workflow

### Complete Test Sequence:
1. ✅ Get JWT token
2. ✅ Create 3 students
3. ✅ Mark attendance for all (2 present, 1 absent)
4. ✅ Check today's attendance summary
5. ✅ Create 2 payments
6. ✅ Update one student
7. ✅ Create notification
8. ✅ Mark payment as paid
9. ✅ List all data
10. ✅ Delete one student

---

## 🎨 Browser Testing (For Non-Technical Users)

### Use the Admin Dashboard:
1. Go to: https://yashamishra.pythonanywhere.com/dashboard/admin/
2. Login with credentials
3. Use the UI to:
   - Add students
   - Mark attendance
   - Manage payments
   - Send notifications

**All dashboard actions use these same APIs in the background!**

---

## 📲 Current Status

| Feature | Status | Notes |
|---------|--------|-------|
| Student CRUD | ✅ Working | Requires Auth |
| Attendance System | ✅ Working | Requires Auth |
| Payment Management | ✅ Working | Requires Auth |
| Notifications | ✅ Working | Requires Auth |
| Dashboards | ✅ Working | Role-based |
| Demo Request | ✅ Working | Public API |
| JWT Authentication | ✅ Working | Token-based |

---

## 🔧 Next Steps

1. **Create Admin User** (via Django admin panel)
2. **Test with Swagger UI** (easiest method)
3. **Test with curl** (for automation)
4. **Verify notifications** (add Twilio/MSG91 keys to enable)

---

**Live Server**: https://yashamishra.pythonanywhere.com/
**API Docs**: https://yashamishra.pythonanywhere.com/swagger/
**Admin Panel**: https://yashamishra.pythonanywhere.com/admin/
