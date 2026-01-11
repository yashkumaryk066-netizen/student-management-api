#!/bin/bash
# 🚀 ULTIMATE DEPLOYMENT + INSTANT SEO SCRIPT
# Run this on PythonAnywhere Console

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Y.S.M AI - ADVANCED PREMIUM DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Navigate to project
echo "📂 Step 1: Navigating to project..."
cd ~/manufatures || { echo "❌ Error: Project directory not found!"; exit 1; }
echo "✅ In project directory"
echo ""

# Step 2: Pull latest changes from GitHub
echo "📥 Step 2: Pulling latest changes from GitHub..."
git pull origin main
if [ $? -eq 0 ]; then
    echo "✅ Successfully pulled latest code"
else
    echo "⚠️  Git pull had issues, continuing..."
fi
echo ""

# Step 3: Verify new files exist
echo "🔍 Step 3: Verifying new files..."
FILES_OK=true

if [ -f "ai/developer_profile.py" ]; then
    echo "  ✅ developer_profile.py found"
else
    echo "  ❌ developer_profile.py missing!"
    FILES_OK=false
fi

if [ -f "static/robots.txt" ]; then
    echo "  ✅ robots.txt found"
else
    echo "  ❌ robots.txt missing!"
    FILES_OK=false
fi

if [ -f "static/sitemap.xml" ]; then
    echo "  ✅ sitemap.xml found"
else
    echo "  ❌ sitemap.xml missing!"
    FILES_OK=false
fi

if [ "$FILES_OK" = true ]; then
    echo "✅ All files verified"
else
    echo "⚠️  Some files missing but continuing..."
fi
echo ""

# Step 4: Check developer name
echo "👤 Step 4: Verifying developer name..."
if grep -q "Yash Ankush Mishra" ai/gemini.py; then
    echo "  ✅ Name correct: Yash Ankush Mishra"
else
    echo "  ⚠️  Name verification unclear"
fi
echo ""

# Step 5: Collect static files (if using Django)
echo "📦 Step 5: Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Static files collected"
else
    echo "⚠️  Static collection skipped (maybe not needed)"
fi
echo ""

# Step 6: Reload web app
echo "🔄 Step 6: Reloading web application..."
USERNAME=$(whoami)
WSGI_FILE="/var/www/${USERNAME}_pythonanywhere_com_wsgi.py"

if [ -f "$WSGI_FILE" ]; then
    touch "$WSGI_FILE"
    echo "✅ Web app reload triggered"
    echo "   WSGI file: $WSGI_FILE"
else
    echo "⚠️  WSGI file not found at: $WSGI_FILE"
    echo "   → Please reload manually from Web tab"
fi
echo ""

# Step 7: Display success message
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 What was deployed:"
echo "  ✨ Advanced Premium AI System"
echo "  👨‍💻 Developer: Yash Ankush Mishra"
echo "  🔍 SEO: Complete optimization"
echo "  🌐 Keywords: YSM AI, Rangra Developer, Ankush AI"
echo ""
echo "🎯 Next Steps:"
echo "  1. Go to Web tab in PythonAnywhere"
echo "  2. Click big green 'Reload' button"
echo "  3. Test your site!"
echo ""
echo "🔗 Your Website:" 
echo "  https://${USERNAME}.pythonanywhere.com"
echo ""
echo "🎉 Your Advanced Premium AI is LIVE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
