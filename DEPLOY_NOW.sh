#!/bin/bash

# Define project directory - Using current directory
PROJECT_DIR="$(pwd)"

echo "🚀 Starting Deployment/Update..."

# Navigate to project directory
cd "$PROJECT_DIR" || exit

# Activate Virtual Environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated."
else
    echo "❌ Virtual environment not found! Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install Dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Apply Migrations
echo "🗄️ Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect Static Files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ DEPLOYMENT TASKS COMPLETED!"
echo "ℹ️  If running on PythonAnywhere, go to the Web tab and click 'Reload'."
echo "ℹ️  If running with Gunicorn, restart the service."
