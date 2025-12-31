#!/bin/bash
# 🚀 Super Admin Setup Script for PythonAnywhere
# Run this script in your PythonAnywhere Bash Console to create your Super Admin account.

cd ~/student-management-api
source venv/bin/activate

echo "==============================================="
echo "🎓 NextGen ERP - Super Admin Setup"
echo "==============================================="
echo "This script will create a Super Admin user for"
echo "your live server: yashamishra.pythonanywhere.com"
echo "==============================================="

python create_client_admin.py

echo "==============================================="
echo "✅ Setup Complete!"
echo "Login at: https://yashamishra.pythonanywhere.com/admin/"
echo "==============================================="
