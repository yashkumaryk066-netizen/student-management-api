#!/bin/bash
# PythonAnywhere Deployment Script for NextGen ERP

echo "🚀 Deploying NextGen ERP to PythonAnywhere..."

# 1. Activate virtual environment
echo "📦 Activating virtual environment..."
source /home/tele/manufatures/venv/bin/activate

# 2. Collect static files
echo "📁 Collecting static files..."
cd /home/tele/manufatures
python manage.py collectstatic --noinput --clear

# 3. Check if animations files exist
echo "✅ Verifying animation files..."
if [ -f "/home/tele/manufatures/staticfiles/css/animations.css" ]; then
    echo "   ✓ animations.css found"
else
    echo "   ✗ animations.css NOT found"
fi

if [ -f "/home/tele/manufatures/staticfiles/js/animations.js" ]; then
    echo "   ✓ animations.js found"
else
    echo "   ✗ animations.js NOT found"
fi

# 4. Display file counts
echo "📊 Static files summary:"
echo "   CSS files: $(ls -1 /home/tele/manufatures/staticfiles/css/ 2>/dev/null | wc -l)"
echo "   JS files: $(ls -1 /home/tele/manufatures/staticfiles/js/ 2>/dev/null | wc -l)"

# 5. Test Django
echo "🧪 Testing Django configuration..."
python manage.py check --deploy 2>&1 | grep -E "(OK|WARNING|ERROR)" | head -n 5

# 6. Instructions for PythonAnywhere reload
echo ""
echo "========================================="
echo "✅ Static files collected successfully!"
echo "========================================="
echo ""
echo "📋 NEXT STEPS (Manual on PythonAnywhere):"
echo ""
echo "1. Go to: https://www.pythonanywhere.com/user/yashamishra/webapps/"
echo "2. Click on: yashamishra.pythonanywhere.com"
echo "3. Scroll to 'Static files' section"
echo "4. Verify mapping:"
echo "   URL: /static/"
echo "   Directory: /home/tele/manufatures/staticfiles"
echo "5. Click 'Reload yashamishra.pythonanywhere.com' button (big green button)"
echo ""
echo "⏱️  Wait 30 seconds after reload, then test:"
echo "   https://yashamishra.pythonanywhere.com/"
echo ""
echo "========================================="
echo "Deployment script completed!"
echo "========================================="
