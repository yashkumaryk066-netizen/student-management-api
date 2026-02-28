#!/bin/bash

# ============================================
# PYTHONANYWHERE DEPLOYMENT GUIDE
# Y.S.M ADVANCE EDUCATION SYSTEM
# ============================================

echo "🚀 Starting PythonAnywhere Deployment..."
echo "========================================="

# 1. Navigate to project directory
cd ~/student-management-api || { echo "❌ Directory not found!"; exit 1; }

echo "✅ Step 1: In project directory"

# 2. Pull latest code from GitHub
echo "📥 Step 2: Pulling latest code from GitHub..."
git pull origin main

# 3. Activate virtual environment
echo "🔧 Step 3: Activating virtual environment..."
source venv/bin/activate

# 4. Install/Update dependencies (if needed)
echo "📦 Step 4: Installing dependencies..."
pip install -r requirements.txt --quiet

# 5. Run database migrations
echo "🗄️  Step 5: Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# 6. Collect static files
echo "📁 Step 6: Collecting static files..."
python manage.py collectstatic --noinput

# 7. Reload web app instructions
echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "🔄 FINAL STEP (MANUAL):"
echo "Go to PythonAnywhere Dashboard → Web Tab"
echo "Click the green 'Reload yashamishra.pythonanywhere.com' button"
echo ""
echo "📌 Updated Features:"
echo "  ✅ Premium Sidebar with Auto-Close"
echo "  ✅ Smooth Scrolling + Custom Scrollbars"
echo "  ✅ Profile Update API (PUT/PATCH)"
echo "  ✅ Desktop Toggle Support"
echo "  ✅ Unified Plan Access Control"
echo "  ✅ Team & Permissions Module"
echo "  ✅ System Audit Logs"
echo ""
echo "🌐 Test URL: https://yashamishra.pythonanywhere.com/dashboard"
echo "========================================="
