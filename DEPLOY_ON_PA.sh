#!/bin/bash

# Define project directory
PROJECT_DIR="/home/yashamishra/student-management-api"

echo "🚀 Starting Deployment on PythonAnywhere..."

# Navigate to project directory
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    echo "✅ Navigated to $PROJECT_DIR"
else
    echo "❌ Directory $PROJECT_DIR not found! Checking current directory..."
fi

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull origin main

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
# Apply Migrations
echo "🗄️ Applying database migrations..."
# Attempt to merge any conflicting migrations
echo "yes" | python manage.py makemigrations --merge
# Run migrations (safe with fake-initial)
python manage.py migrate --fake-initial

# Collect Static Files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Reload Web App
echo "🔄 Reloading web application..."
touch /var/www/yashamishra_pythonanywhere_com_wsgi.py

echo "✅ DEPLOYMENT COMPLETE! Please check your website."
