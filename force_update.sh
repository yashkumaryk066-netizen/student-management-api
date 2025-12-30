#!/bin/bash
echo "🔄 Force Updating Institute Management System..."

# 1. Reset any local changes to ensure clean pull
git reset --hard
git pull origin main

# 2. Activate or Create Environment
if [ ! -d "venv" ]; then
    echo "🔨 Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Install requirements
echo "📦 Installing modules..."
pip install --upgrade pip
pip install -r requirements.txt
pip install dj-database-url python-decouple django djangorestframework django-cors-headers whitenoise djangorestframework-simplejwt drf-spectacular

# 4. Force collect static files
python manage.py collectstatic --clear --noinput

# 5. Migrate
python manage.py migrate

echo "✅ Update successfully applied."
echo "👉 NOW: Go to PythonAnywhere 'Web' tab and click 'Reload'."
