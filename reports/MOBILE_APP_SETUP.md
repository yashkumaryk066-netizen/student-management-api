# 📱 Sovereign ERP: Real Mobile App (APK) Setup Guide

This guide explains how to generate your **Real Android APK** for free using the advanced infrastructure I have set up.

## 🚀 The Infrastructure
I have created a **Professional Native Shell** using Apache Cordova and an **Automated Build Pipeline** using GitHub Actions.

### 1. Configure your URL
Before building, open `real_app/sovereign-app/www/index_mobile.html` and change:
```javascript
const PRODUCTION_URL = "https://your-production-url.com";
```
Replace it with the live domain where your ERP is hosted.

### 2. Get your APK (The Free Cloud Build way)
Since building an APK requires 20GB of Android SDKs and specialized software, I have set up a **GitHub Action** that does this for you on GitHub's powerful servers for FREE.

**Steps:**
1.  **Push this code** to a GitHub repository (Public or Private).
2.  Go to the **"Actions"** tab on your GitHub repository page.
3.  You will see a workflow named **"Build Sovereign ERP APK"** running.
4.  Once it finishes (takes ~5 mins), click on the successful run.
5.  Under **"Artifacts"**, you will find the `Sovereign-ERP-Mobile-Release` download link.
6.  This is your **Real APK** file!

### 3. Native Features Included
*   **Branded Splash Screen:** Institutional logo on a deep blue background.
*   **High Performance:** Assets are cached locally for faster loading.
*   **Native Feel:** No browser address bar, no zoom glitches, and custom icons.
*   **Security:** Whitelisted navigation to prevent users from leaving the ERP shell.

---
*Developed with Advanced Research & Sovereign Enterprise Standards.*
