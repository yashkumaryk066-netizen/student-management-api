#!/bin/bash
# 🔧 Y.S.M AI - Fix Script
# This script will update your Gemini API key

echo "======================================================"
echo "🔧 Y.S.M AI - API Key Update Script"
echo "======================================================"
echo ""

# Check if new key provided
if [ -z "$1" ]; then
    echo "❌ Error: No API key provided"
    echo ""
    echo "Usage: ./fix_ai_key.sh YOUR_NEW_GEMINI_API_KEY"
    echo ""
    echo "📝 Steps:"
    echo "1. Get new key from: https://aistudio.google.com/app/apikey"
    echo "2. Run: ./fix_ai_key.sh YOUR_NEW_KEY"
    exit 1
fi

NEW_KEY="$1"

echo "📝 Updating .env file..."
cd /home/tele/manufatures

# Remove old key
sed -i '/GEMINI_API_KEY/d' .env

# Add new key
echo "GEMINI_API_KEY=$NEW_KEY" >> .env

echo "✅ API key updated successfully!"
echo ""
echo "🧪 Testing AI connection..."
python3 quick_ai_test.py

echo ""
echo "======================================================"
echo "✅ Fix Complete!"
echo "======================================================"
echo ""
echo "Next steps:"
echo "1. If tests passed, reload your web app"
echo "2. If on PythonAnywhere, click 'Reload' button"
echo "3. Test AI chat at /ai-chat/"
