# NextGen ERP - Client Onboarding Guide

## Welcome to NextGen ERP! 🎉

This guide will help you get started with your new Education Management System.

---

## 📋 Pre-Deployment Checklist

Before going live, ensure you have:

- [ ] Domain name (if using custom domain)
- [ ] Institution logo (PNG format, 500x500px recommended)
- [ ] Color scheme preferences
- [ ] List of initial admin users
- [ ] Student data in CSV format (if migrating)
- [ ] Fee structure details
- [ ] Academic year dates
- [ ] Holiday calendar

---

## 🚀 Quick Start Steps

### Step 1: Access Your System

**Live URL:** `https://[your-domain].pythonanywhere.com`  
**Admin Panel:** `https://[your-domain].pythonanywhere.com/admin/`

### Step 2: Initial Login

**Default Admin Credentials:**
- Username: `admin`
- Password: `[provided separately]`

**⚠️ IMPORTANT:** Change this password immediately after first login!

### Step 3: System Configuration

1. **Go to Admin Panel** → Settings
2. **Update Institution Details:**
   - Name
   - Address
   - Contact information
   - Logo upload
   - Color theme

3. **Set Academic Year:**
   - Start date
   - End date
   - Terms/semesters

4. **Configure Fee Structure:**
   - Fee categories
   - Amounts
   - Due dates
   - Late fee rules

---

## 👥 User Management

### Creating Admin Users

1. Admin Panel → Users → Add User
2. Fill details and set role as "ADMIN"
3. Create User Profile with Admin role
4. Send credentials securely

### Creating Teachers

1. Admin Panel → Users → Add User
2. Set role as "TEACHER"
3. Assign subjects and classes
4. Provide login credentials

### Adding Students

**Method 1: Individual Entry**
1. Dashboard → Students → Add Student
2. Fill all required fields
3. Assign parent/guardian
4. Set class and section

**Method 2: Bulk Upload (CSV)**
1. Dashboard → Students → Import
2. Download sample CSV template
3. Fill with student data
4. Upload and verify

---

## 📚 Module Setup

### 1. Academic Setup
- [ ] Create subjects
- [ ] Define classes/sections
- [ ] Set up classrooms
- [ ] Create timetable
- [ ] Add exam schedule

### 2. Library Setup
- [ ] Add book categories
- [ ] Import book catalog
- [ ] Set borrowing rules
- [ ] Configure fine rates
- [ ] Assign librarian

### 3. Finance Setup
- [ ] Define fee categories
- [ ] Set payment methods
- [ ] Configure SMS for reminders
- [ ] Set up payment gateway (optional)
- [ ] Create fee structure templates

### 4. Transport Setup (if applicable)
- [ ] Add vehicles
- [ ] Define routes
- [ ] Set pickup points
- [ ] Allocate students
- [ ] Assign drivers

### 5. Hostel Setup (if applicable)
- [ ] Create hostel buildings
- [ ] Add rooms
- [ ] Set capacity
- [ ] Assign wardens
- [ ] Configure hostel fees

---

## 🔔 Notification Setup

### SMS Configuration

1. Choose provider (MSG91 / Twilio / TextLocal)
2. Get API credentials
3. Add to Admin Panel → Settings → SMS
4. Test with sample message

### WhatsApp Setup

1. Register for Twilio WhatsApp API
2. Get credentials
3. Add to Settings → WhatsApp
4. Verify sandbox (for testing)
5. Apply for production access

---

## 📊 Using Dashboards

### Admin Dashboard

**Key Metrics displayed:**
- Total students
- Today's attendance
- Pending fees
- Recent activities

**Quick Actions:**
- Add student
- Mark attendance
- Send notification
- View reports

### Teacher Dashboard

**Features:**
- Class attendance
- Grade entry
- Assignment creation
- Student list
- Timetable view

### Parent Dashboard

**What parents see:**
- Children's attendance
- Grades and report cards
- Fee dues
- Notifications
- Upcoming events

### Student Dashboard

**Student access:**
- Attendance record
- Grades and marks
- Fee status  
- Timetable
- Assignments

---

## 📱 Mobile Access

**Responsive Design:** Works on all devices  
**Recommended Browsers:**
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Mobile App:** Coming soon (iOS/Android)

---

## 🔐 Security Best Practices

1. **Change default passwords immediately**
2. **Use strong passwords** (min 12 characters)
3. **Enable two-factor authentication** (when available)
4. **Review user permissions regularly**
5. **Don't share admin credentials**
6. **Log out after each session**
7. **Keep software updated**

---

## 📞 Support & Training

### Getting Help

**Priority Support:**
- Email: support@nextgenerp.com
- Phone: +91 835-692-6231
- Hours: Mon-Sat, 9 AM - 6 PM IST

**Resources:**
- User Manual: `/USER_MANUAL.md`
- API Documentation: `/swagger/`
- Video Tutorials: [Coming soon]
- Knowledge Base: [Coming soon]

### Training Schedule

**Week 1: Admin Training** (4 hours)
- System overview
- Basic configuration
- User management
- Report generation

**Week 2: Staff Training** (2 hours per group)
- Dashboard navigation
- Attendance marking
- Grade entry
- Communication tools

**Week 3: Parent Orientation** (1 hour)
- Portal access
- Viewing reports
- Fee payment
- Communication

---

## 🔧 Troubleshooting

### Common Issues

**Q: Can't login?**
A: Verify username/password, check caps lock, try password reset

**Q: Attendance not showing?**
A: Ensure correct date selected, check if marked for that class

**Q: Payment not reflecting?**
A: Wait 5 minutes for sync, check transaction ID, contact support

**Q: SMS not sending?**
A: Verify API credentials, check SMS balance, test configuration

---

## 📈 Best Practices

### Daily Operations
- ✅ Mark attendance by 10 AM
- ✅ Review pending tasks
- ✅ Check notifications
- ✅ Update student records

### Weekly Tasks
- ✅ Generate attendance reports
- ✅ Follow up on fee dues
- ✅ Back up important data
- ✅ Review system logs

### Monthly Activities
- ✅ Generate financial reports
- ✅ Send parent updates
- ✅ Review user access
- ✅ Plan upcoming events

---

## 🎓 Advanced Features

### API Integration
- Access via `/api/` endpoints
- Documentation at `/swagger/`
- JWT authentication required
- Rate limits apply

### Custom Reports
- Export to Excel/PDF
- Schedule automatic reports
- Email reports to stakeholders
- Custom filters available

### Third-Party Integrations
- Payment gateways
- Biometric devices
- SMS providers
- Accounting software

---

## ✅ Go-Live Checklist

Before announcing to users:

- [ ] All admin users created
- [ ] Sample data tested
- [ ] Notifications working
- [ ] Reports generating correctly
- [ ] Backups configured
- [ ] Support contacts shared
- [ ] Staff trained
- [ ] Parent communication sent
- [ ] Login credentials distributed
- [ ] Monitoring enabled

---

## 🔄 Data Migration

### From Excel/CSV

1. Export existing data to CSV
2. Use our import templates
3. Map fields correctly
4. Import in test environment
5. Verify data integrity
6. Import to production

### From Another System

Contact support for:
- Database migration assistance
- API integration
- Custom data import scripts

---

## 📊 Reporting & Analytics

### Available Reports

**Academic:**
- Student list
- Attendance summary
- Grade reports
- Result analysis

**Financial:**
- Fee collection
- Pending dues
- Payment history
- Revenue analysis

**Administrative:**
- User activity logs
- System usage stats
- Performance metrics

---

## 🎯 Success Metrics

Track these KPIs:

- **Adoption Rate:** % of staff using system daily
- **Data Accuracy:** % of records complete
- **Parent Engagement:** Login frequency
- **Fee Collection:** On-time payment %
- **Support Tickets:** Response time

---

## 📅 Maintenance Schedule

**Daily:** Automatic backups  
**Weekly:** System health checks  
**Monthly:** Security updates  
**Quarterly:** Feature updates  
**Yearly:** Major version upgrades

---

## 🆘 Emergency Contacts

**Critical Issues (24/7):**  
Phone: +91 835-692-6231  
Email: emergency@nextgenerp.com

**Technical Support:**  
Email: tech@nextgenerp.com  
Portal: support.nextgenerp.com

---

**Welcome aboard! We're excited to support your institution's digital transformation!** 🚀

---

*NextGen ERP Client Onboarding Guide v1.0*  
*Last Updated: January 2026*
