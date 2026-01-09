import google.generativeai as genai
import os
from decouple import config

# Try to get key from env, or hardcode the one user provided for testing
api_key = config('GEMINI_API_KEY', default="AIzaSyDukbuezLoIrvHJYAxOVc0siBlH2MD985g")
genai.configure(api_key=api_key)

print("🔍 Scanning Neural Engines (Available Models)...")
try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
            available_models.append(m.name)
        else:
            print(f"❌ Skipped (No generateContent): {m.name}")
            
    if not available_models:
        print("\n⚠️ CRITICAL: No models found with 'generateContent' capability.")
    else:
        print(f"\n🚀 Recommended Model: {available_models[0]}")
        
except Exception as e:
    print(f"\n☠️ CONNECTION FAILED: {str(e)}")
