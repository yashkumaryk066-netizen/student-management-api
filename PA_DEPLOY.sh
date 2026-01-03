#!/bin/bash
# PA_DEPLOY.sh - Robust PythonAnywhere Deployment Script
# Usage: bash PA_DEPLOY.sh

echo "🚀 Starting PythonAnywhere Deployment..."

# 0. Ensure we are in the project root
if [ -f "manage.py" ]; then
    PROJECT_ROOT=$(pwd)
else
    # Try to find manage.py one level down
    if [ -d "student-management-api" ]; then
        cd student-management-api
        PROJECT_ROOT=$(pwd)
    else
        echo "❌ Error: Could not find manage.py. Please run this script from the project folder."
        exit 1
    fi
fi

echo "📂 Project Root: $PROJECT_ROOT"

# 1. Pull Latest Code
echo "📥 Git Pull..."
git pull origin main

# 2. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "🔨 Creating venv..."
    python3 -m venv venv
fi
source venv/bin/activate
echo "✅ Virtualenv Activated: $(which python)"

# 3. Install Requirements
echo "📦 Installing Requirements..."
# Force reinstall pycryptodome to avoid binary issues
pip install --upgrade pip
pip install -r requirements.txt
pip install --force-reinstall pycryptodome

# 4. Migrate DB
echo "🗄️ Migrating Database..."
# Attempt to merge conflicting migrations automatically
python manage.py makemigrations --merge --noinput
python manage.py makemigrations
python manage.py migrate

# 5. Collect Static
echo "🎨 Collecting Static Files..."
python manage.py collectstatic --noinput

# 6. Verify Import (Sanity Check)
export DJANGO_SETTINGS_MODULE=manufatures.settings
python -c "import django; django.setup(); from student import urls; print('✅ Syntax Check Passed')"

echo "---------------------------------------------------"
echo "✅ DEPLOYMENT FINISHED SUCCESSFULLY!"
echo "👉 Now go to the PythonAnywhere 'Web' tab and click 'Reload'."
echo "---------------------------------------------------"
