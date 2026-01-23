# Education System Access Control & Permission Guide

This document provides a comprehensive breakdown of the Role-Based Access Control (RBAC) system implemented in the application. It details the capabilities and restrictions for each user role across different product types.

## 1. Product Overview

The system supports three distinct product types, each with tailored feature sets:

### **A. Coaching Product**
*   **Focus:** Specialized tuition centers and coaching institutes.
*   **Key Features:**
    *   Student & Batch Management
    *   Fees & Installation Tracking
    *   Attendance
    *   Basic Reports
    *   *Excluded:* Library, Transport, Hostel, Advanced HR.

### **B. School Product**
*   **Focus:** Formal K-12 education.
*   **Key Features:**
    *   Full Student Lifecycle (Admission to Alumni)
    *   Comprehensive Exam & Grading System (CBSE/ICSE support)
    *   Transport Management (Bus tracking)
    *   Library Management
    *   Hostel Management
    *   Timetable & Syllabus

### **C. Institute Product (Premium/ERP)**
*   **Focus:** Large colleges, universities, or multi-branch institutions.
*   **Key Features:**
    *   **All School Features** +
    *   Advanced HR & Payroll (Salary, Leave, Biometric Integration)
    *   Asset Management
    *   Alumni Network
    *   Multi-branch Support
    *   Public Website CMS

---

## 2. User Roles & Capabilities

### **1. CLIENT (Super Admin / Owner)**
*   **Description:** The primary account holder who purchased the subscription.
*   **Access Level:** **Unlimited**.
*   **Capabilities:**
    *   **Manage Staff:** Create/Delete HR, Teachers, Accountants.
    *   **Financials:** Full view of revenue, expenses, profit/loss, and subscription renewals.
    *   **Settings:** Configure institution details, branding, geolocation, and payment gateways.
    *   **Approvals:** Approve/Reject new student registrations.
    *   **Data Control:** Edit or delete any record in the system.

### **2. HR / MANAGER**
*   **Description:** Operational head responsible for day-to-day management.
*   **Access Level:** **High (Restricted)**.
*   **Capabilities:**
    *   **Staff Management:** Add new teachers and operational staff.
    *   **Attendance:** specific oversight of staff attendance.
    *   **Student Management:** Full access to admits and details.
    *   **Reports:** View operational reports.
*   **Restrictions:**
    *   **CANNOT** delete the Client (Owner) account.
    *   **CANNOT** access the "Subscription & Billing" section (SaaS payments).
    *   **CANNOT** modify global system settings (e.g., Institution Name, Logo).

### **3. TEACHER**
*   **Description:** Academic staff responsible for students and classrooms.
*   **Access Level:** **Medium (Academic Only)**.
*   **Capabilities:**
    *   **Classes:** View assigned batches/classes.
    *   **Attendance:** Mark student attendance (Geo-fenced or Manual).
    *   **Exams:** Upload marks and view results.
    *   **Library:** Search books and view catalog.
    *   **Homework:** Upload assignments.
*   **Restrictions:**
    *   No access to Fees or Financial data.
    *   No access to Staff management.
    *   Cannot delete students.

### **4. ACCOUNTANT**
*   **Description:** Staff managing finances.
*   **Access Level:** **Medium (Financial Only)**.
*   **Capabilities:**
    *   **Fees:** Collect fees, generate receipts, view dues.
    *   **Expenses:** Record daily expenses.
*   **Restrictions:**
    *   No access to Academic records (Marks, Exams).
    *   No access to HR/Staffing.

### **5. STUDENT**
*   **Description:** The end-user learner.
*   **Access Level:** **Personal View Only**.
*   **Capabilities:**
    *   **Profile:** View personal details.
    *   **Academics:** View Class Routine, Syllabus, Homework.
    *   **Exams:** View Report Card / Marks.
    *   **Attendance:** View personal attendance history.
    *   **Fees:** Pay fees online (if enabled) and view payment history.
    *   **Library:** View issued books and due dates.
*   **Restrictions:**
    *   Read-only access. Cannot modify any data.

### **6. PARENT**
*   **Description:** Guardian of the student.
*   **Access Level:** **Personal View Only (Child-focused)**.
*   **Capabilities:**
    *   Same visibility as the Student but can switch between multiple children (siblings).
    *   Direct communication channel with Teachers/Admin (if enabled).

---

## 3. Permission Matrix (Quick Reference)

| Module | Client | HR | Teacher | Student | Parent |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Settings** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Add Staff** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **See Revenue**| ✅ | ⚠️ (Ltd) | ❌ | ❌ | ❌ |
| **Take Attendance** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Mark History** | ✅ | ✅ | ✅ | 👁️ View | 👁️ View |
| **Pay Fees** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Library** | ✅ | ✅ | 👁️ View | 👁️ View | 👁️ View |
