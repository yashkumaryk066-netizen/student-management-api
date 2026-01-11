#!/usr/bin/env python3
"""
Direct AI Test - Checks if Gemini is working properly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from ai.manager import get_ai_manager

print("="*60)
print("🧪 Direct AI Test")
print("="*60)
print()

try:
    # Get AI Manager
    ai = get_ai_manager(provider='gemini')
    
    print(f"✅ Provider: {ai.provider}")
    print(f"✅ Service: {type(ai.service).__name__}")
    print()
    
    # Test Question
    question = "Namaste! Tum kaun ho? Ek line mein batao."
    print(f"📝 Question: {question}")
    print()
    
    # Get Answer
    print("⏳ Asking AI...")
    answer = ai.ask_tutor(question, subject="Test")
    
    print("="*60)
    print("✅ AI Response:")
    print("="*60)
    print(answer)
    print()
    print("="*60)
    print("✅ SUCCESS! Gemini AI is working perfectly!")
    print("="*60)
    
except Exception as e:
    print("="*60)
    print(f"❌ ERROR: {str(e)}")
    print("="*60)
    import traceback
    traceback.print_exc()
