#!/bin/bash
# Complete Deployment Script for PythonAnywhere
# This script handles the entire deployment process

echo "=============================================="
echo "🚀 NextGen ERP - Complete Deployment"
echo "=============================================="

# Navigate to project directory
cd ~/student-management-api

echo "📦 Step 1: Pulling latest code..."
git pull origin main

echo "🔧 Step 2: Activating virtual environment..."
source venv/bin/activate

echo "📥 Step 3: Installing/updating dependencies..."
pip install -r requirements.txt --upgrade

echo "🗄️  Step 4: Running database migrations..."
python manage.py migrate

echo "📁 Step 5: Collecting static files..."
python manage.py collectstatic --noinput

echo "👑 Step 6: Creating Super Admin..."
python create_super_admin_auto.py

echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo "Next Steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' button"
echo "3. Visit: https://yashamishra.pythonanywhere.com"
echo "=============================================="
