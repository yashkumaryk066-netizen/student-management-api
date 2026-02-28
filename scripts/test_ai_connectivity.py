from ai.manager import get_ai_manager
import os
import django
from django.conf import settings

# Configure minimal Django settings if needed for decouple/config to work or just run direct
# Actually ai.manager uses decouple.config which reads .env directly.
# We just need to ensure the path is correct.

print("--- Testing Y.S.M AI System ---")

try:
    ai = get_ai_manager(provider='gemini')
    print(f"Manager initialized. Provider: {ai.provider}")
    
    response = ai.ask_tutor("Hello, are you online?", subject="System Check")
    print("\n[AI Response]:")
    print(response)
    
    if "System Update In Progress" in response:
        print("\n⚠️  System returned Failsafe response (Offline Mode triggered inside manager)")
    else:
        print("\n✅ System is ONLINE and responding!")

except Exception as e:
    print(f"\n❌ Test Failed: {e}")
