#!/bin/bash
# One-click deployment script for user to copy-paste
echo "🚀 Updating your live site..."
cd ~/student-management-api
git pull origin main
echo "✅ Code updated!"
echo "🔄 Reloading application..."
# Note: We can't hit the reload button via script without API token, 
# but we can touch the wsgi file which often triggers a reload in some setups,
# or just tell the user to click the button.
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py 2>/dev/null || echo "⚠️  Please go to Web Tab and click RELOAD button manually."
echo "🎉 Update Complete! Visit https://yashamishra.pythonanywhere.com/developer/"
