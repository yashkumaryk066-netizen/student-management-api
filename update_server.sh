#!/bin/bash
echo "🚀 Updating Student Management System..."

# Pull latest changes
git pull origin main

# Activate virtualenv
source venv/bin/activate

# Install dependencies just in case
pip install -r requirements.txt

# Collect static files (this will now correctly hash files from static/ to staticfiles/)
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Migrate database
echo "🗄️ Running migrations..."
python manage.py migrate

echo "✅ Update complete! Please reload the web app from the 'Web' tab."
