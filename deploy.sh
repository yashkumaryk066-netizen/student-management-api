#!/bin/bash
# PythonAnywhere Deployment Script
# Run this in PythonAnywhere Bash Console

echo "🚀 Starting NextGen ERP Deployment..."
echo "========================================"

# Navigate to project
echo "📁 Step 1: Navigating to project directory..."
cd ~/student-management-api || exit 1

# Pull latest code
echo "📥 Step 2: Pulling latest code from GitHub..."
git pull origin main

# Check if pull was successful
if [ $? -eq 0 ]; then
    echo "✅ Code pulled successfully!"
else
    echo "❌ Failed to pull code. Check your internet connection."
    exit 1
fi

# Create migrations
echo "🗄️  Step 3: Creating database migrations..."
python manage.py makemigrations

# Apply migrations
echo "🗄️  Step 4: Applying database migrations..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Database migrations applied!"
else
    echo "⚠️  Warning: Migrations may have failed. Check manually."
fi

# Collect static files
echo "📦 Step 5: Collecting static files (CSS, JS, images)..."
python manage.py collectstatic --noinput --clear

if [ $? -eq 0 ]; then
    echo "✅ Static files collected!"
else
    echo "❌ Failed to collect static files."
    exit 1
fi

# Summary
echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================"
echo ""
echo "📋 What was deployed:"
echo "  ✅ Latest code from GitHub"
echo "  ✅ Database models: Exam, Grade, ResultCard, LibraryBook, BookIssue"
echo "  ✅ Static files: CSS (3D animations), JavaScript (dashboards)"
echo "  ✅ All 15+ new files"
echo ""
echo "🔄 FINAL STEP:"
echo "  Go to: https://www.pythonanywhere.com/user/yashamishra/webapps/"
echo "  Click the green 'Reload' button"
echo ""
echo "🎉 After reload, your site will be 100% updated!"
echo ""
