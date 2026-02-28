#!/bin/bash
# Script to FORCE synchronization of database
echo "🔧 Forcing Database Sync..."

# 1. Merge any lingering conflicts
python manage.py makemigrations --merge --noinput

# 2. Fake Apply 'student' app migrations
# This assumes the database tables already exist (which the error confirms)
# and tells Django to just mark the migrations as "done" without running SQL.
echo "🔄 Syncing Migration History..."
python manage.py migrate student --fake

# 3. Apply any other pending migrations normally
echo "🔄 Applying other migrations..."
python manage.py migrate

# 4. Collect Static Files (ensure JS updates are live)
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --noinput

# 5. Reload Server
echo "🚀 Reloading Server..."
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py

echo "✅ Database & Server Synced! You can now use the dashboard."
