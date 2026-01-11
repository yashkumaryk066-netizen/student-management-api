
import os
import django
from django.conf import settings
from decouple import config

# Setup Django standalone
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from ai.manager import get_ai_manager

print("--- Y.S.M AI System Check ---")

# Check Key Presence
key = config('GEMINI_API_KEY', default=None)
print(f"API Key Detected: {'YES' if key else 'NO'}")

if not key:
    print("❌ Critical: No API Key found in .env")
    exit(1)

# Check Manager Connection
try:
    manager = get_ai_manager(provider='gemini')
    print(f"AI Manager Initialized: {manager.provider.upper()}")
    
    # Live Test
    print("Testing Neural Connectivity...")
    response = manager.ask_tutor("Hello, confirm you are online.", subject="System Check")
    
    if "Offline" in response or "Error" in response:
        print(f"⚠️  System Warning: {response[:100]}...")
    else:
        print("✅  SUCCESS: AI is Online and Responding.")
        print(f"Response Preview: {response[:50]}...")

except Exception as e:
    print(f"❌ System Error: {e}")
