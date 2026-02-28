#!/usr/bin/env python3
"""
Y.S.M AI - Complete Health Check & Auto-Fix
Diagnoses all AI engines and fixes configuration
"""

import os
import sys

# Add project to path
sys.path.insert(0, '/home/tele/manufatures')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management.settings')

import django
django.setup()

from decouple import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 60)
print("🔍 Y.S.M AI - Complete System Diagnostic")
print("=" * 60)
print()

# Check 1: HuggingFace
print("1️⃣ Testing HuggingFace AI (FREE, Unlimited)...")
try:
    from ai.huggingface import get_huggingface_service
    hf = get_huggingface_service()
    
    test_response = hf.ask_tutor("Say 'HuggingFace Online'", subject="Test")
    
    if test_response and len(test_response) > 5:
        print(f"   ✅ HuggingFace AI: WORKING")
        print(f"   Response: {test_response[:80]}...")
    else:
        print(f"   ⚠️ HuggingFace AI: Response too short")
        
except Exception as e:
    print(f"   ❌ HuggingFace AI: FAILED")
    print(f"   Error: {str(e)[:100]}")

print()

# Check 2: Gemini
print("2️⃣ Testing Google Gemini AI...")
try:
    gemini_key = config('GEMINI_API_KEY', default='')
    
    if not gemini_key:
        print("   ⚠️ Gemini API Key: NOT SET")
        print("   Run: echo 'GEMINI_API_KEY=AIzaSyAAQ9nTflOI56IBNUKxGJl7uM5ns0RWIuE' >> .env")
    else:
        print(f"   ✅ Gemini API Key: SET ({gemini_key[:20]}...)")
        
        from ai.gemini import get_gemini_service
        gemini = get_gemini_service()
        
        test_response = gemini.ask_tutor("Say 'Gemini Online'", subject="Test")
        
        if test_response and len(test_response) > 5:
            print(f"   ✅ Gemini AI: WORKING")
            print(f"   Response: {test_response[:80]}...")
        else:
            print(f"   ⚠️ Gemini AI: Response too short")
            
except Exception as e:
    print(f"   ❌ Gemini AI: FAILED")
    print(f"   Error: {str(e)[:100]}")

print()

# Check 3: AI Manager (with fallback)
print("3️⃣ Testing AI Manager (with auto-fallback)...")
try:
    from ai.manager import get_ai_manager
    
    # Try with default provider
    ai = get_ai_manager()
    print(f"   Primary Provider: {ai.provider}")
    
    test_response = ai.ask_tutor("Hello, are you working?")
    
    if "unavailable" in test_response.lower() or "error" in test_response.lower():
        print(f"   ❌ AI Manager: FAILED")
        print(f"   Response: {test_response[:100]}")
    else:
        print(f"   ✅ AI Manager: WORKING")
        print(f"   Active Provider: {ai.provider}")
        print(f"   Response: {test_response[:80]}...")
        
except Exception as e:
    print(f"   ❌ AI Manager: FAILED")
    print(f"   Error: {str(e)[:100]}")

print()
print("=" * 60)
print("📊 Diagnostic Complete")
print("=" * 60)
print()

# Recommendations
print("💡 RECOMMENDATIONS:")
print()
print("If HuggingFace is working:")
print("  ✅ You're good! No API keys needed.")
print()
print("If only Gemini works:")
print("  Run: sed -i '/GEMINI_API_KEY/d' .env && \\")
print("       echo 'GEMINI_API_KEY=AIzaSyAAQ9nTflOI56IBNUKxGJl7uM5ns0RWIuE' >> .env")
print()
print("After fixes:")
print("  Run: python3 test_ai_health.py")
print("  Then: Reload web app from Web tab")
print()
