import os
import django
import sys
import logging

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from notifications.telegram_service import telegram_service

def send_test_message():
    print("--------------------------------------------------")
    print("🚀 Testing Telegram Integrated Notification System...")
    
    # User Provided Chat ID
    TEST_CHAT_ID = "5280398471"
    
    print(f"📡 Specifc Target Chat ID: {TEST_CHAT_ID}")
    
    # Send a Premium "Welcome/Test" Message
    message = (
        "🌟 *Y.S.M ADVANCE NOTIFICATION SYSTEM* 🌟\n\n"
        "✅ *Integration Successful!*\n"
        "Your Telegram bot is now connected to the Student Management System.\n\n"
        "🔔 *You will now receive alerts for:*\n"
        "• New Account Credentials\n"
        "• Subscription Renewals\n"
        "• Critical System Updates\n\n"
        "🚀 *System is Online & Secure.*"
    )
    
    success = telegram_service.send_message(TEST_CHAT_ID, message)
    
    if success:
        print("✅ SUCCESS: Test message sent securely to Telegram.")
    else:
        print("❌ FAILED: Could not send message. Check Bot Token or Chat ID.")
        
    print("--------------------------------------------------")

if __name__ == "__main__":
    send_test_message()
