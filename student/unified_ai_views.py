"""
Unified Multi-Model AI API Views
Supports ChatGPT, Gemini, and Claude with model selection
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ai.manager import get_ai_manager, AIServiceManager
import logging

logger = logging.getLogger(__name__)
from .models import AISubscription



class AIProvidersListView(APIView):
    """List all available AI providers and models"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        """Get list of available AI providers"""
        try:
            providers = AIServiceManager.get_available_providers()
            
            return Response({
                "success": True,
                "providers": providers,
                "total_providers": len(providers),
                "supported": ["chatgpt", "gemini", "claude"]
            })
        except Exception as e:
            logger.error(f"Error fetching providers: {str(e)}")
            return Response({
                "error": "Failed to fetch AI providers",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnifiedAITutorView(APIView):
    """Unified AI tutoring endpoint - supports all providers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Ask AI tutor with provider selection
        
        Request body:
        {
            "question": "What is photosynthesis?",
            "subject": "Biology",
            "context": "Optional context",
            "provider": "chatgpt|gemini|claude",  // Optional
            "model": "specific-model-name"  // Optional
        }
        """
        try:
            question = request.data.get('question')
            subject = request.data.get('subject', 'General')
            context = request.data.get('context', '')
            provider = request.data.get('provider')  # Optional
            model = request.data.get('model')  # Optional
            
            # --- FREE ACCESS (LOGIN REQUIRED) ---
            # IsAuthenticated handles the login check.
            # We removed the subscription block here.
            # ------------------------------------
            
            if not question:
                return Response({
                    "error": "Question is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get AI manager with specified provider/model
            ai = get_ai_manager(provider=provider, model=model)
            answer = ai.ask_tutor(question, subject, context)
            
            return Response({
                "success": True,
                "question": question,
                "subject": subject,
                "answer": answer,
                "provider_info": ai.get_provider_info()
            })
            
        except Exception as e:
            logger.error(f"Unified AI Tutor error: {str(e)}")
            return Response({
                "error": "AI tutoring service failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnifiedQuizGeneratorView(APIView):
    """Unified quiz generation - supports all providers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Generate quiz with provider selection
        
        Request body:
        {
            "topic": "World War II",
            "num_questions": 5,
            "difficulty": "medium",
            "provider": "chatgpt|gemini|claude",  // Optional
            "model": "specific-model-name"  // Optional
        }
        """
        try:
            topic = request.data.get('topic')
            num_questions = request.data.get('num_questions', 5)
            difficulty = request.data.get('difficulty', 'medium')
            provider = request.data.get('provider')
            model = request.data.get('model')
            
            if not topic:
                return Response({
                    "error": "Topic is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ai = get_ai_manager(provider=provider, model=model)
            quiz = ai.generate_quiz(topic, num_questions, difficulty)
            
            return Response({
                "success": True,
                "topic": topic,
                "quiz": quiz,
                "num_questions": num_questions,
                "difficulty": difficulty,
                "provider_info": ai.get_provider_info()
            })
            
        except Exception as e:
            logger.error(f"Unified Quiz generation error: {str(e)}")
            return Response({
                "error": "Quiz generation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnifiedContentSummarizerView(APIView):
    """Unified content summarization - supports all providers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Summarize content with provider selection"""
        try:
            text = request.data.get('text')
            max_length = request.data.get('max_length', 200)
            provider = request.data.get('provider')
            model = request.data.get('model')
            
            if not text:
                return Response({
                    "error": "Text content is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ai = get_ai_manager(provider=provider, model=model)
            summary = ai.summarize_content(text, max_length)
            
            return Response({
                "success": True,
                "original_length": len(text.split()),
                "summary": summary,
                "summary_length": len(summary.split()),
                "provider_info": ai.get_provider_info()
            })
            
        except Exception as e:
            logger.error(f"Unified Summarization error: {str(e)}")
            return Response({
                "error": "Summarization failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnifiedConceptExplainerView(APIView):
    """Unified concept explanation - supports all providers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Explain concepts with provider selection"""
        try:
            concept = request.data.get('concept')
            grade_level = request.data.get('grade_level', 'high school')
            provider = request.data.get('provider')
            model = request.data.get('model')
            
            if not concept:
                return Response({
                    "error": "Concept is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ai = get_ai_manager(provider=provider, model=model)
            explanation = ai.explain_concept(concept, grade_level)
            
            return Response({
                "success": True,
                "concept": concept,
                "grade_level": grade_level,
                "explanation": explanation,
                "provider_info": ai.get_provider_info()
            })
            
        except Exception as e:
            logger.error(f"Unified Concept explanation error: {str(e)}")
            return Response({
                "error": "Concept explanation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnifiedContentTranslatorView(APIView):
    """Unified content translation - supports all providers"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Translate content with provider selection"""
        try:
            text = request.data.get('text')
            target_language = request.data.get('target_language')
            provider = request.data.get('provider')
            model = request.data.get('model')
            
            if not text or not target_language:
                return Response({
                    "error": "Text and target language are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            ai = get_ai_manager(provider=provider, model=model)
            translated = ai.translate_content(text, target_language)
            
            return Response({
                "success": True,
                "original": text,
                "target_language": target_language,
                "translated": translated,
                "provider_info": ai.get_provider_info()
            })
            
        except Exception as e:
            logger.error(f"Unified Translation error: {str(e)}")
            return Response({
                "error": "Translation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
