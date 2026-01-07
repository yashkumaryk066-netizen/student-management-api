#!/usr/bin/env python
"""
ChatGPT AI Integration Test Script
Tests all AI endpoints to ensure proper functionality
"""
import os
import sys
import json
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from ai.chatgpt import get_chatgpt_service
from colorama import init, Fore, Style

# Initialize colorama for colored output
try:
    init(autoreset=True)
except:
    pass

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")

def print_header(message):
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{message}")
    print(f"{'='*60}{Style.RESET_ALL}\n")


def test_service_initialization():
    """Test if ChatGPT service can be initialized"""
    print_header("Test 1: Service Initialization")
    
    try:
        service = get_chatgpt_service()
        print_success(f"Service initialized successfully")
        print_info(f"Model: {service.default_model}")
        print_info(f"Temperature: {service.temperature}")
        print_info(f"Max Tokens: {service.max_tokens}")
        return True
    except Exception as e:
        print_error(f"Service initialization failed: {str(e)}")
        return False


def test_ai_tutor():
    """Test AI tutoring feature"""
    print_header("Test 2: AI Tutoring")
    
    try:
        service = get_chatgpt_service()
        question = "What is the Pythagorean theorem?"
        subject = "Mathematics"
        
        print_info(f"Question: {question}")
        print_info(f"Subject: {subject}")
        
        answer = service.ask_tutor(question, subject)
        
        print_success("AI Tutor response received")
        print(f"\n{Fore.MAGENTA}Answer:{Style.RESET_ALL}")
        print(answer[:300] + "..." if len(answer) > 300 else answer)
        return True
        
    except Exception as e:
        print_error(f"AI Tutoring failed: {str(e)}")
        return False


def test_quiz_generation():
    """Test quiz generation"""
    print_header("Test 3: Quiz Generation")
    
    try:
        service = get_chatgpt_service()
        topic = "Solar System"
        num_questions = 3
        
        print_info(f"Topic: {topic}")
        print_info(f"Questions: {num_questions}")
        
        quiz = service.generate_quiz(topic, num_questions, "medium", "multiple_choice")
        
        print_success("Quiz generated successfully")
        print(f"\n{Fore.MAGENTA}Quiz (first 500 chars):{Style.RESET_ALL}")
        print(quiz[:500] + "..." if len(quiz) > 500 else quiz)
        return True
        
    except Exception as e:
        print_error(f"Quiz generation failed: {str(e)}")
        return False


def test_summarization():
    """Test content summarization"""
    print_header("Test 4: Content Summarization")
    
    try:
        service = get_chatgpt_service()
        text = """
        Artificial intelligence (AI) is intelligence demonstrated by machines, 
        in contrast to the natural intelligence displayed by humans and animals. 
        Leading AI textbooks define the field as the study of "intelligent agents": 
        any device that perceives its environment and takes actions that maximize 
        its chance of successfully achieving its goals. Colloquially, the term 
        "artificial intelligence" is often used to describe machines that mimic 
        "cognitive" functions that humans associate with the human mind, such as 
        "learning" and "problem solving".
        """
        
        print_info(f"Original length: {len(text.split())} words")
        
        summary = service.summarize_content(text, max_length=50)
        
        print_success("Content summarized successfully")
        print(f"\n{Fore.MAGENTA}Summary:{Style.RESET_ALL}")
        print(summary)
        return True
        
    except Exception as e:
        print_error(f"Summarization failed: {str(e)}")
        return False


def test_concept_explanation():
    """Test concept explanation"""
    print_header("Test 5: Concept Explanation")
    
    try:
        service = get_chatgpt_service()
        concept = "Photosynthesis"
        grade_level = "middle school"
        
        print_info(f"Concept: {concept}")
        print_info(f"Grade Level: {grade_level}")
        
        explanation = service.explain_concept(concept, grade_level)
        
        print_success("Concept explained successfully")
        print(f"\n{Fore.MAGENTA}Explanation (first 300 chars):{Style.RESET_ALL}")
        print(explanation[:300] + "..." if len(explanation) > 300 else explanation)
        return True
        
    except Exception as e:
        print_error(f"Concept explanation failed: {str(e)}")
        return False


def test_translation():
    """Test content translation"""
    print_header("Test 6: Content Translation")
    
    try:
        service = get_chatgpt_service()
        text = "Education is the key to success"
        target_language = "Hindi"
        
        print_info(f"Original: {text}")
        print_info(f"Target Language: {target_language}")
        
        translated = service.translate_content(text, target_language)
        
        print_success("Translation successful")
        print(f"\n{Fore.MAGENTA}Translated:{Style.RESET_ALL}")
        print(translated)
        return True
        
    except Exception as e:
        print_error(f"Translation failed: {str(e)}")
        return False


def test_custom_prompt():
    """Test custom prompt"""
    print_header("Test 7: Custom Prompt")
    
    try:
        service = get_chatgpt_service()
        prompt = "List 3 benefits of using AI in education"
        
        print_info(f"Prompt: {prompt}")
        
        response = service.custom_prompt(prompt)
        
        print_success("Custom prompt executed successfully")
        print(f"\n{Fore.MAGENTA}Response:{Style.RESET_ALL}")
        print(response)
        return True
        
    except Exception as e:
        print_error(f"Custom prompt failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print(f"{Fore.CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      ChatGPT AI Integration - Test Suite                ║")
    print("║      Y.S.M Advanced Education System                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # Check for API key
    from decouple import config
    try:
        api_key = config('OPENAI_API_KEY')
        print_info(f"API Key found: {api_key[:10]}...{api_key[-4:]}")
    except Exception:
        print_error("OPENAI_API_KEY not found in environment variables")
        print_info("Please set OPENAI_API_KEY in your .env file")
        return

    
    tests = [
        ("Service Initialization", test_service_initialization),
        ("AI Tutoring", test_ai_tutor),
        ("Quiz Generation", test_quiz_generation),
        ("Content Summarization", test_summarization),
        ("Concept Explanation", test_concept_explanation),
        ("Content Translation", test_translation),
        ("Custom Prompt", test_custom_prompt),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print_error("\nTesting interrupted by user")
            break
        except Exception as e:
            print_error(f"Unexpected error in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
    
    if passed == total:
        print_success(f"All tests passed! ({passed}/{total})")
        print(f"\n{Fore.GREEN}🎉 ChatGPT AI Integration is working perfectly!{Style.RESET_ALL}")
    else:
        print_error(f"Some tests failed ({passed}/{total})")
        print_info("Check the errors above for details")
    
    print(f"\n{Fore.CYAN}Note: Some tests may fail if you're using a free API tier")
    print(f"or if you've exceeded your usage limits.{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
