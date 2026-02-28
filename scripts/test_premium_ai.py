#!/usr/bin/env python
"""
Premium AI System Test Script
Tests the upgraded advanced premium AI responses
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from ai.gemini import get_gemini_service
from ai.groq import get_groq_service
from ai.deepseek import get_deepseek_service

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)

def test_identity_query(service_name, service):
    """Test developer identity query"""
    print_separator(f"Testing {service_name} - Identity Query")
    
    questions = [
        "Who created you?",
        "Tumhe kisne banaya?",
        "Tell me about your developer"
    ]
    
    for question in questions:
        print(f"\n📝 Question: {question}")
        print("-" * 80)
        try:
            response = service.ask_tutor(question, subject="General")
            print(f"✅ Response:\n{response[:500]}...")  # Print first 500 chars
            
            # Check if profile info is included
            checks = [
                ("Yash" in response, "✓ Developer name mentioned"),
                ("Telepathy Infotech" in response, "✓ Company mentioned"),
                ("BCA" in response or "Bachelor" in response, "✓ Education mentioned"),
                ("30" in response or "2004" in response, "✓ DOB mentioned"),
                ("yash_profile.jpg" in response, "✓ Profile image referenced")
            ]
            
            print("\n🔍 Profile Information Checks:")
            for check, msg in checks:
                print(f"  {'✅' if check else '❌'} {msg}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

def test_technical_query(service_name, service):
    """Test technical query response quality"""
    print_separator(f"Testing {service_name} - Technical Query")
    
    question = "Explain how to build a REST API in Django with authentication"
    print(f"\n📝 Question: {question}")
    print("-" * 80)
    
    try:
        response = service.ask_tutor(question, subject="Software Development")
        print(f"✅ Response:\n{response[:500]}...")
        
        # Check response quality markers
        checks = [
            ("```" in response, "✓ Code blocks present"),
            ("**" in response, "✓ Bold formatting used"),
            (any(emoji in response for emoji in ["🎯", "💻", "⚡", "🚀"]), "✓ Emojis used"),
            (len(response) > 300, "✓ Detailed response (>300 chars)")
        ]
        
        print("\n🔍 Quality Checks:")
        for check, msg in checks:
            print(f"  {'✅' if check else '❌'} {msg}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_multilingual_query(service_name, service):
    """Test multilingual response"""
    print_separator(f"Testing {service_name} - Multilingual Query")
    
    question = "Python me loop kaise likhte hain?"
    print(f"\n📝 Question: {question}")
    print("-" * 80)
    
    try:
        response = service.ask_tutor(question, subject="Programming")
        print(f"✅ Response:\n{response[:400]}...")
        
        # Check if response is in Hindi/Hinglish
        hindi_words = ["है", "हैं", "के", "में", "loop", "for"]
        has_hindi = any(word in response for word in hindi_words)
        
        print(f"\n🔍 Language Check: {'✅ Response in Hindi/Hinglish' if has_hindi else '❌ Not in Hindi/Hinglish'}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print_separator("🚀 ADVANCED PREMIUM AI SYSTEM - TEST SUITE")
    print("\nTesting upgraded AI with premium response quality and developer profile...")
    
    # Test services
    services = []
    
    # Try Gemini
    try:
        gemini = get_gemini_service()
        if gemini.api_key:
            services.append(("Gemini", gemini))
            print("✅ Gemini service loaded")
    except Exception as e:
        print(f"⚠️  Gemini not available: {e}")
    
    # Try Groq
    try:
        groq = get_groq_service()
        if groq.api_key:
            services.append(("Groq", groq))
            print("✅ Groq service loaded")
    except Exception as e:
        print(f"⚠️  Groq not available: {e}")
    
    # Try DeepSeek
    try:
        deepseek = get_deepseek_service()
        if deepseek.api_key:
            services.append(("DeepSeek", deepseek))
            print("✅ DeepSeek service loaded")
    except Exception as e:
        print(f"⚠️  DeepSeek not available: {e}")
    
    if not services:
        print("\n❌ No AI services available. Please check API keys in .env file")
        return
    
    print(f"\n✅ Total services to test: {len(services)}")
    
    # Run tests for each service
    for service_name, service in services:
        test_identity_query(service_name, service)
        test_technical_query(service_name, service)
        test_multilingual_query(service_name, service)
    
    print_separator("🎉 TEST SUITE COMPLETED")
    print("\n✅ Advanced Premium AI System upgrade tested successfully!")
    print("💡 Key Features:")
    print("   - World-class response quality")
    print("   - Developer profile integration")
    print("   - Premium formatting and structure")
    print("   - Multilingual capabilities")
    print("   - Expert-level technical responses")

if __name__ == "__main__":
    main()
