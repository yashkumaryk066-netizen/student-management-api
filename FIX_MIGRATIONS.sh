#!/bin/bash
# Script to resolve migration conflicts and deploy
echo "🩹 Fixing Migration Conflicts..."

# 1. Merge conflicting migrations
python manage.py makemigrations --merge --noinput

# 2. Apply migrations
echo "🔄 Applying Database Migrations..."
python manage.py migrate

# 3. Collect Static Files
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --noinput

# 4. Reload Server
echo "🚀 Reloading Server..."
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py

echo "✅ Fix Complete! Please reload the page."
