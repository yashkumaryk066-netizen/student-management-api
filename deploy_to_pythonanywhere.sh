#!/bin/bash
# ============================================
# PythonAnywhere Deployment Script
# Y.S.M Education System - Premium Sidebar Update
# ============================================

echo "🚀 Starting PythonAnywhere Deployment..."
echo "=========================================="
echo ""

# Step 1: Navigate to project directory
echo "📁 Step 1: Navigating to project directory..."
cd ~/student-management-api || { echo "❌ Error: Project directory not found!"; exit 1; }
echo "✅ Current directory: $(pwd)"
echo ""

# Step 2: Check current branch
echo "🔍 Step 2: Checking Git status..."
git branch
git status
echo ""

# Step 3: Pull latest changes from GitHub
echo "⬇️  Step 3: Pulling latest code from GitHub..."
git pull origin main
if [ $? -eq 0 ]; then
    echo "✅ Code pulled successfully!"
else
    echo "❌ Error pulling code. Please check your connection."
    exit 1
fi
echo ""

# Step 4: Install/Update dependencies (if needed)
echo "📦 Step 4: Checking dependencies..."
pip install --user djangorestframework-simplejwt --quiet
echo "✅ Dependencies checked"
echo ""

# Step 5: Collect static files
echo "📂 Step 5: Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully!"
else
    echo "⚠️  Warning: Static files collection had issues"
fi
echo ""

# Step 6: Run migrations (if any)
echo "🗄️  Step 6: Running database migrations..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✅ Migrations completed!"
else
    echo "⚠️  Warning: Migration issues detected"
fi
echo ""

# Step 7: Verify files
echo "🔍 Step 7: Verifying deployed files..."
echo "Checking CSS files:"
ls -lh static/css/dashboard.css static/css/upgrade-modal.css 2>/dev/null
echo ""
echo "Checking JS files:"
ls -lh static/js/sidebar-manager.js 2>/dev/null
echo ""

# Step 8: Instructions for web app reload
echo "=========================================="
echo "🎯 FINAL STEP: Reload Your Web App"
echo "=========================================="
echo ""
echo "1. Go to: https://www.pythonanywhere.com/user/YOUR_USERNAME/webapps/"
echo "2. Find your web app (e.g., yoursite.pythonanywhere.com)"
echo "3. Click the green 'Reload' button"
echo ""
echo "OR use this command (if you have API token):"
echo "curl -X POST https://www.pythonanywhere.com/api/v0/user/YOUR_USERNAME/webapps/YOUR_DOMAIN/reload/ \\"
echo "  -H 'Authorization: Token YOUR_API_TOKEN'"
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📋 What was deployed:"
echo "  ✓ Premium 3D Menu Toggle (Red theme)"
echo "  ✓ Premium Sidebar Navigation"
echo "  ✓ Plan-based Access Control"
echo "  ✓ Upgrade Modal System"
echo "  ✓ Category Organization"
echo "  ✓ Neon Animations & Effects"
echo ""
echo "🧪 Testing:"
echo "  1. Open your website"
echo "  2. Click the red three-dot menu button"
echo "  3. Sidebar should open with categories"
echo "  4. Open browser console (F12)"
echo "  5. Test plans: changePlan('coaching')"
echo ""
echo "📚 Documentation:"
echo "  - PREMIUM_SIDEBAR_GUIDE.md"
echo "  - DEPLOYMENT_TEST_REPORT.md"
echo "  - MENU_TOGGLE_IMPLEMENTATION.md"
echo ""
echo "🎉 Enjoy your premium dashboard!"
echo "=========================================="
