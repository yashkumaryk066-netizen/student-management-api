#!/bin/bash
# Auto-fix deployment script

echo "🔍 Checking environment..."
cd ~/student-management-api

# Try to activate venv if it exists
if [ -d "venv" ]; then
    echo "✅ Found venv, activating..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "✅ Found ../venv, activating..."
    source ../venv/bin/activate
else
    echo "⚠️  No 'venv' folder found. Installing to user space (safe fallback)..."
    # If no venv, use pip with --user
    PIP_ARGS="--user"
fi

echo "📦 Installing missing requirements (including simplejwt)..."
pip install $PIP_ARGS -r requirements.txt

echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --settings=manufatures.pythonanywhere_settings

echo "✅ DONE! Go to Web Tab and Click Reload."
