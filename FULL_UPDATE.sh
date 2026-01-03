#!/bin/bash
# FULL RELOAD SCRIPT (Run this when things are stuck)
echo "🛑 Hard Resetting Local Changes..."
git reset --hard HEAD
echo "🔄 Pulling Latest Code..."
git pull origin main
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --noinput --settings=manufatures.pythonanywhere_settings
echo "✨ Touching WSGI to Trigger Reload..."
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py 2>/dev/null
echo "✅ UPDATE COMPLETE! Please go to Web Tab -> RELOAD just to be sure."
