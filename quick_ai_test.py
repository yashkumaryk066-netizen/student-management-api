#!/usr/bin/env python3
"""
Y.S.M AI - Simple Health Check (No Django)
Tests AI engines directly
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🔍 Y.S.M AI - Quick Health Check")
print("=" * 60)
print()

# Check 1: Environment Variables
print("1️⃣ Checking Configuration...")
try:
    from decouple import config
    
    gemini_key = config('GEMINI_API_KEY', default='')
    hf_key = config('HUGGINGFACE_API_KEY', default='')
    
    if gemini_key:
        print(f"   ✅ Gemini API Key: SET ({gemini_key[:20]}...)")
    else:
        print(f"   ⚠️ Gemini API Key: NOT SET")
    
    if hf_key:
        print(f"   ✅ HuggingFace Key: SET ({hf_key[:20]}...)")
    else:
        print(f"   ℹ️ HuggingFace Key: Not set (using public mode)")
        
except Exception as e:
    print(f"   ❌ Config Error: {str(e)}")

print()

# Check 2: HuggingFace Direct Test
print("2️⃣ Testing HuggingFace AI...")
try:
    import requests
    
    url = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
    
    payload = {
        "inputs": "Hello, are you working? Reply with just 'Yes I am working'",
        "parameters": {"max_new_tokens": 50}
    }
    
    print("   Sending test request...")
    response = requests.post(url, json=payload, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            answer = result[0].get('generated_text', '')
            print(f"   ✅ HuggingFace AI: WORKING")
            print(f"   Response: {answer[:80]}")
        else:
            print(f"   ⚠️ HuggingFace: Unexpected response format")
    else:
        print(f"   ⚠️ HuggingFace: HTTP {response.status_code}")
        print(f"   Message: {response.text[:100]}")
        
except Exception as e:
    print(f"   ❌ HuggingFace Test Failed: {str(e)}")

print()

# Check 3: Gemini Test
print("3️⃣ Testing Google Gemini AI...")
try:
    from decouple import config
    gemini_key = config('GEMINI_API_KEY', default='')
    
    if not gemini_key:
        print("   ⚠️ Gemini: API key not configured")
        print("   To fix: echo 'GEMINI_API_KEY=AIzaSyAAQ9nTflOI56IBNUKxGJl7uM5ns0RWIuE' >> .env")
    else:
        import google.generativeai as genai
        
        genai.configure(api_key=gemini_key)
        
        # List available models
        print("   Scanning for available models...")
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        
        if models:
            print(f"   ✅ Found {len(models)} models")
            best_model = models[0]
            print(f"   Using: {best_model}")
            
            # Test generation
            model = genai.GenerativeModel(model_name=best_model)
            response = model.generate_content("Say 'Gemini is working'")
            
            print(f"   ✅ Gemini AI: WORKING")
            print(f"   Response: {response.text[:80]}")
        else:
            print(f"   ⚠️ No models found")
            
except ImportError:
    print("   ⚠️ google-generativeai not installed")
    print("   Run: pip install google-generativeai")
except Exception as e:
    print(f"   ❌ Gemini Test Failed: {str(e)[:150]}")

print()
print("=" * 60)
print("📊 Health Check Complete")
print("=" * 60)
print()

print("💡 NEXT STEPS:")
print()
print("If HuggingFace is working:")
print("  ✅ Your AI is ready! Just reload the web app.")
print()
print("If Gemini is working:")
print("  ✅ Your AI is ready! Just reload the web app.")
print()
print("If BOTH failed:")
print("  1. Check internet connection")
print("  2. Wait 30 seconds and try again (HuggingFace warmup)")
print("  3. Set Gemini key if not set")
print()
print("After any fixes, reload web app from PythonAnywhere Web tab")
print()
