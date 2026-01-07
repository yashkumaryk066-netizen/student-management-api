# PythonAnywhere Deployment Commands
# Premium 3D Menu Toggle Update

## Step 1: Login to PythonAnywhere Console
# Go to: https://www.pythonanywhere.com/user/[your-username]/consoles/
# Open a Bash console

## Step 2: Navigate to your project directory
cd ~/student-management-api
# OR if your project is in a different location:
# cd ~/[your-project-folder-name]

## Step 3: Pull latest changes from GitHub
git pull origin main

## Step 4: Collect static files (IMPORTANT for CSS changes)
python manage.py collectstatic --noinput

## Step 5: Reload your web app
# Option A: Using the web interface
# Go to: https://www.pythonanywhere.com/user/[your-username]/webapps/
# Click the "Reload" button for your web app

# Option B: Using command line (if you have API token)
# Replace [your-username] with your actual username
# Replace [your-domain] with your actual domain
# curl -X POST https://www.pythonanywhere.com/api/v0/user/[your-username]/webapps/[your-domain]/reload/ \
#   -H "Authorization: Token YOUR_API_TOKEN"

## Step 6: Clear browser cache
# After reloading, clear your browser cache or use Ctrl+Shift+R (hard refresh)
# to see the new menu toggle design

## Verification Steps:
# 1. Open your website
# 2. Check if the red menu toggle button appears to the left of search bar
# 3. Click it to verify sidebar toggle works
# 4. Test on mobile/tablet view (resize browser or use DevTools)
# 5. Verify the 3D glow animation on hover

## Troubleshooting:
# If changes don't appear:
# 1. Check static files path in settings.py
# 2. Run collectstatic again with --clear flag:
#    python manage.py collectstatic --clear --noinput
# 3. Check file permissions: ls -la static/css/dashboard.css
# 4. Verify STATIC_ROOT and STATIC_URL in settings.py
# 5. Check error logs in PythonAnywhere dashboard

## Quick One-Liner (Copy-Paste All Commands):
cd ~/student-management-api && git pull origin main && python manage.py collectstatic --noinput && echo "✅ Deployment complete! Now reload your web app from PythonAnywhere dashboard."
