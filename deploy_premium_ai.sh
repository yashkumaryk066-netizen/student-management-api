#!/bin/bash
# Quick deployment script for PythonAnywhere
# Run this on PythonAnywhere console

echo "🚀 Deploying Advanced Premium AI System..."
echo ""

# Navigate to project
cd ~/manufatures || exit

echo "📥 Pulling latest changes from GitHub..."
git pull origin main

echo ""
echo "✅ Verifying new files..."
if [ -f "ai/developer_profile.py" ]; then
    echo "  ✓ developer_profile.py found"
else
    echo "  ✗ developer_profile.py missing!"
fi

if [ -f "test_premium_ai.py" ]; then
    echo "  ✓ test_premium_ai.py found"
else
    echo "  ✗ test_premium_ai.py missing!"
fi

echo ""
echo "🔍 Checking developer name..."
if grep -q "Yash Ankush Mishra" ai/gemini.py; then
    echo "  ✓ Name correct: Yash Ankush Mishra"
else
    echo "  ✗ Name not found in gemini.py"
fi

echo ""
echo "🔄 Reloading web app..."
# Get username dynamically
USERNAME=$(whoami)
WSGI_FILE="/var/www/${USERNAME}_pythonanywhere_com_wsgi.py"

if [ -f "$WSGI_FILE" ]; then
    touch "$WSGI_FILE"
    echo "  ✓ Web app triggered for reload"
else
    echo "  ⚠️  WSGI file not found at $WSGI_FILE"
    echo "  → Please reload manually from Web tab"
fi

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Go to Web tab in PythonAnywhere"
echo "  2. Click 'Reload' button (green)"
echo "  3. Test with: 'Who created you?'"
echo ""
echo "🎉 Your Advanced Premium AI is ready!"
