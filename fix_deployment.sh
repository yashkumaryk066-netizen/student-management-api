#!/bin/bash
# EMERGENCY FIX SCRIPT FOR PYTHONANYWHERE DEPLOYMENT
# This script fixes all common deployment errors

echo "🚀 Starting Emergency Fix..."

# Step 1: Navigate to project
cd ~/student-management-api || exit 1

# Step 2: Reset any corrupted files and pull fresh code
echo "📥 Pulling fresh code from GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

# Step 3: Activate virtual environment (if it exists)
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found at venv/"
    echo "Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Step 4: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 5: Install all dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 6: Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations student
python manage.py migrate

# Step 7: Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "⚠️ IMPORTANT: Now go to PythonAnywhere Web tab and click the GREEN 'Reload' button!"
echo ""
