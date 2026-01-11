
import os
import sys
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

import google.generativeai as genai

print("--- Y.S.M AI Diagnostics ---")

# 1. Check API Key Formatting
key = config('GEMINI_API_KEY', default="")
if not key:
    print("❌ ERROR: GEMINI_API_KEY is missing in .env")
    sys.exit(1)

print(f"Key detected: {key[:4]}...{key[-4:]} (Length: {len(key)})")

if " " in key:
    print("⚠️ WARNING: API Key contains spaces! Check .env file.")
if "'" in key or '"' in key:
    print("⚠️ WARNING: API Key contains quotes! Remove them in .env file.")

# 2. Configure Gemini
print("\n--- Connecting to Google AI ---")
try:
    genai.configure(api_key=key)
    
    print("Listing Available Models for this Key:")
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")
            found_any = True
            
    if not found_any:
        print("❌ NO MODELS FOUND! This API Key usually has no access to Generative AI.")
        print("   Possible causes: Billing disabled, API disabled in console, or wrong project.")
    
    # 3. Test Generation
    if found_any:
        print("\n--- Testing Generation (gemini-1.5-flash) ---")
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Say 'System OK'")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Generation Failed: {e}")

except Exception as e:
    print(f"❌ Connection Failed: {e}")
