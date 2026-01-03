#!/bin/bash
# Script to resolve "Table Already Exists" errors
echo "🔧 Fixing Database Sync Issues..."

# 1. Merge conflicting migrations (if any left)
python manage.py makemigrations --merge --noinput

# 2. Migrate with --fake-initial 
# This tells Django: "If the table already exists, assume this migration is done."
echo "🔄 Applying Database Migrations (Safe Mode)..."
python manage.py migrate --fake-initial

# 3. Reload Server
echo "🚀 Reloading Server..."
python manage.py collectstatic --noinput
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py

echo "✅ Database Synced! Try using the dashboard now."
