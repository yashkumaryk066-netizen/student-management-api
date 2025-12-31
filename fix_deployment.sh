#!/bin/bash
# Complete Deployment Fix Script for PythonAnywhere
# This script pulls latest code, updates static files, and restarts the app

set -e  # Exit on any error

echo "=========================================="
echo "🚀 NextGen ERP Deployment Fix Script"
echo "=========================================="
echo ""

# Navigate to project directory
cd ~/student-management-api || { echo "❌ Error: Project directory not found!"; exit 1; }

echo "📂 Current directory: $(pwd)"
echo ""

# Check git status before pulling
echo "🔍 Checking Git status..."
git status
echo ""

# Pull latest code from GitHub
echo "📥 Pulling latest code from GitHub..."
git pull origin main
echo "✅ Code updated successfully!"
echo ""

# Show last 5 commits
echo "📝 Recent commits:"
git log --oneline -5
echo ""

# Install/Update dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed!"
echo ""

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected!"
echo ""

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate
echo "✅ Migrations complete!"
echo ""

# Verify author.jpg exists
if [ -f "static/images/author.jpg" ]; then
    echo "✅ Author photo found: static/images/author.jpg"
else
    echo "⚠️  WARNING: Author photo not found!"
fi
echo ""

if [ -f "staticfiles/images/author.jpg" ]; then
    echo "✅ Author photo collected: staticfiles/images/author.jpg"
else
    echo "⚠️  WARNING: Author photo not in staticfiles!"
fi
echo ""

# Check index.html for branding
echo "🔍 Checking for branding in templates..."
if grep -q "by Yash A Mishra" templates/index.html; then
    echo "✅ Branding found in index.html"
else
    echo "⚠️  WARNING: Branding NOT found in index.html!"
fi
echo ""

echo "=========================================="
echo "✅ Deployment fixes completed!"
echo "=========================================="
echo ""
echo "📋 NEXT STEPS:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click the green 'Reload' button"
echo "3. Wait 10-15 seconds"
echo "4. Visit: https://yashamishra.pythonanywhere.com/"
echo "5. Check for 'by Yash A Mishra' branding"
echo ""
echo "🎯 Expected Results:"
echo "  ✓ Navbar should show 'by Yash A Mishra' with photo"
echo "  ✓ Footer should show personal branding"
echo "  ✓ Background should have falling 'YASH A MISHRA' text"
echo ""
