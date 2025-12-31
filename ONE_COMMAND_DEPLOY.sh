#!/bin/bash
# ========================================================
# 🎯 ONE-COMMAND DEPLOYMENT FOR PYTHONANYWHERE
# ========================================================
# Copy this entire block and paste in PythonAnywhere Bash Console
# ========================================================

echo "=============================================="
echo "🚀 NextGen ERP - Complete Deployment"
echo "   Live Server: yashamishra.pythonanywhere.com"
echo "=============================================="
echo ""

# Navigate to project
cd ~/student-management-api || { echo "❌ Failed to find project directory"; exit 1; }

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main || { echo "⚠️  Git pull failed - continuing anyway"; }
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ~/student-management-api/venv/bin/activate || { echo "❌ Failed to activate venv"; exit 1; }
echo ""

# Install dependencies
echo "📦 Installing/Updating dependencies..."
pip install -r requirements.txt --upgrade --quiet
echo "✅ Dependencies updated"
echo ""

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate
echo ""

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput
echo ""

# Create super admin
echo "👑 Creating Super Admin Account..."
python create_super_admin_auto.py
echo ""

echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to PythonAnywhere 'Web' tab"
echo "2. Click 'Reload' for yashamishra.pythonanywhere.com"
echo "3. Visit: https://yashamishra.pythonanywhere.com"
echo ""
echo "🔐 LOGIN CREDENTIALS:"
echo "   URL: https://yashamishra.pythonanywhere.com/admin/"
echo "   Username: client_admin"
echo "   Password: NextGen2025!Secure"
echo ""
echo "=============================================="
