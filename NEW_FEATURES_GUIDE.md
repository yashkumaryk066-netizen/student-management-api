# 🚀 Y.S.M Advance Education System - New Premium Features Guide

## 1. 💸 Smart Invoice & Payment System
The system now automatically generates professional Tax Invoices for every payment.

### How to Use:
1.  Go to **Admin Panel > Payments**.
2.  Select a specific payment or bulk select payments.
3.  Choose Action: **"Approve Payment & Renew Subscription"**.
4.  **Result**:
    *   Client receives an email with:
        *   **New Purchase**: Login Credentials + Invoice PDF.
        *   **Renewal**: Plan Extension Notice + Invoice PDF.
    *   Features are automatically unlocked based on the plan (School/Coaching/Institute).

---

## 2. 🪪 Smart Student ID Cards
Generate physical ID cards with QR codes for identity verification.

### How to Use:
1.  Go to **Admin Panel > Students**.
2.  Select one or multiple students.
3.  Choose Action: **"Download Smart ID Card"**.
4.  **Result**:
    *   A high-quality PDF is downloaded (ZIP file if multiple).
    *   Includes: Photo, Name, Roll No, Blood Group, and **Unique QR Code**.

> **Note**: Ensure student has a photo uploaded for best results.

---

## 3. 📄 Automated Admission Letters
Issue official welcome letters to parents upon admission.

### How to Use:
1.  Go to **Admin Panel > Students**.
2.  Select the student.
3.  Choose Action: **"Download Admission Letter"**.
4.  **Result**:
    *   A4 PDF Letterhead with Principal's signature area.
    *   Standardized text confirming admission details (Class, Roll No).

---

## 4. 🔒 Premium Feature Locking
A visual upgrade to the user interface to encourage plan upgrades.

*   **Behavior**: When a user clicks on a module NOT in their plan (e.g., a 'Coaching' user clicking 'Hostel').
*   **Visual**: A "Glassmorphism" styled modal appears with a glowing lock icon.
*   **Action**: Prompts user to "Upgrade Plan" instead of just showing an error.

## 5. 📈 Smart Progress Reports (Report Cards)
Generate comprehensive Academic Report Cards with performance analysis.

### How to Use:
1.  Go to **Admin Panel > Students**.
2.  Select student(s).
3.  Choose Action: **"Download Progress Report"**.
4.  **Result**:
    *   Professional PDF Report Card.
    *   Lists all exams, marks, grades, and Fail/Pass status.
    *   Includes **Performance Summary** and Teacher Signature area.

---

## 🛠️ Required Setup for Deployment
Run these commands on PythonAnywhere to activate all features:

```bash
cd ~/student-management-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # instals reportlab, qrcode
python manage.py migrate         # adds photo, payment_mode fields
python manage.py collectstatic --noinput
```

**System Version**: 2.0 (Advance)
**Last Updated**: Jan 2026
