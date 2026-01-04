# Final Deployment Command List

Execute these commands in your **PythonAnywhere Bash Console** to verify and deploy the "Advance Level" Fixed System.

## 1. Update Code & Deploy Admin Controls 👑
```bash
cd student-management-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Verify Database (REQUIRED: Performance Updates)
```bash
python manage.py makemigrations
python manage.py migrate
```

## 3. Collect Static Files (REQUIRED for Dashboard JS)
```bash
python manage.py collectstatic --noinput
```

## 4. Automation Setup (Daily Reminders)
*(Ensure you have set the Task in PythonAnywhere Dashboard)*

## 5. Reload Application
*   Go to the **Web** tab in PythonAnywhere dashboard.
*   Click the big green **Reload** button.

---
**Features Live in Dashboard:** 
✅ **Super Admin Controls:** "Block", "Unblock", "-7 Days" buttons (Frontend).
✅ **Mobile Security:** Fixed CSRF/CORS.
✅ **UI:** Premium 3D Modals (Now on Dashboard + Login).
✅ **Automation:** Daily Reminders active.
