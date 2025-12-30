#!/bin/bash
# PythonAnywhere Deployment Script
# Run this in PythonAnywhere Bash console

echo "🚀 Starting deployment..."

# Update username here
USERNAME="YOUR_USERNAME"  # CHANGE THIS!

# Clone repository (if not already done)
if [ ! -d "student-management-api" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/yashkumaryk066-netizen/student-management-api.git
fi

# Go to project
cd student-management-api

# Pull latest changes
echo "🔄 Pulling latest changes..."
git pull origin main

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install MySQL client
pip install mysqlclient

# Run migrations
echo "🗄️ Running migrations..."
export DJANGO_SETTINGS_MODULE=manufatures.pythonanywhere_settings
python manage.py migrate

# Create superuser (interactive)
echo "👤 Create superuser..."
python manage.py createsuperuser

# Setup sample data
echo "📊 Setting up sample data..."
python manage.py setup_roles

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Go to Web tab on PythonAnywhere"
echo "2. Add a new web app (Manual configuration, Python 3.10)"
echo "3. Configure WSGI file (see wsgi_config.py)"
echo "4. Set virtualenv: /home/$USERNAME/student-management-api/venv"
echo "5. Add static files mapping: /static/ -> /home/$USERNAME/student-management-api/staticfiles"
echo "6. Reload web app"
echo ""
echo "Your site will be live at: https://$USERNAME.pythonanywhere.com"
