#!/bin/bash
echo "🔄 Force Updating Institute Management System..."

# 1. Reset any local changes to ensure clean pull
git reset --hard
git pull origin main

# 2. Activate Environment
source venv/bin/activate

# 3. Re-install requirements to be safe
pip install -r requirements.txt

# 4. Force collect static files
python manage.py collectstatic --clear --noinput

# 5. Migrate
python manage.py migrate

echo "✅ Update successfully applied."
echo "👉 NOW: Go to PythonAnywhere 'Web' tab and click 'Reload'."
