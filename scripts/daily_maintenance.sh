#!/bin/bash

# ====================================================
#  ADVANCED DAILY MAINTENANCE SCRIPT - NEXTGEN ERP
# ====================================================
# This script handles:
# 1. 📧 Sending Expiry Reminders (7/3/1 days)
# 2. 🚫 Suspending Expired Accounts
# 3. 🧹 Cleaning Old Sessions & Temp Files
# 4. 📝 Logging for Audit
# ====================================================

# Set Paths (User specific)
PROJECT_DIR="/home/yashamishra/student-management-api"
LOG_FILE="$PROJECT_DIR/daily_automation.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 🚀 Starting Daily Maintenance..." >> $LOG_FILE

# Navigate
cd $PROJECT_DIR || { echo "❌ Failed to cd to project dir" >> $LOG_FILE; exit 1; }

# Activate Virtual Environment
source venv/bin/activate

# 1. Send Expiry Reminders & Suspend Users
echo "[$DATE] 📧 Running Expiry Check..." >> $LOG_FILE
python manage.py send_expiry_reminders >> $LOG_FILE 2>&1

# 2. Clear Expired User Sessions (Security Best Practice)
echo "[$DATE] 🧹 Clearing Expired Sessions..." >> $LOG_FILE
python manage.py clearsessions >> $LOG_FILE 2>&1

# 3. (Optional) Database Backup could go here
# python manage.py dumpdata > backup/weekly_backup.json

echo "[$DATE] ✅ Maintenance Complete." >> $LOG_FILE
echo "----------------------------------------------------" >> $LOG_FILE
