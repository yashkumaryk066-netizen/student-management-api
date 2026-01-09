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


from rest_framework.permissions import AllowAny

class UnifiedAITutorView(APIView):
    """
    Y.S.M Universal AI - Beyond ChatGPT
    Supports: Text, Images, Videos, Code, All Languages
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        """
        Universal AI Endpoint
        
        Capabilities:
        - Image Analysis (upload photo, get detailed explanation)
        - Video Understanding (coming soon)
        - Code Generation (any language)
        - Multilingual Chat (Hindi, English, Spanish, etc.)
        - Study Help, Math, Science, Everything
        """
        try:
            question = request.data.get('question')
            subject = request.data.get('subject', 'General')
            context = request.data.get('context', 'User is asking for advanced professional assistance.')
            provider = request.data.get('provider')
            model = request.data.get('model')
            
            if not question:
                return Response({
                    "error": "Question is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # File/Image Support for Multimodal AI
            files = request.data.get('files', [])
            
            # Get the most powerful AI available
            ai = get_ai_manager(provider=provider, model=model)
            
            # Send to AI with all capabilities
            answer = ai.ask_tutor(
                question=question,
                subject=subject,
                context=context,
                media_data=files
            )
            
            return Response({
                "success": True,
                "question": question,
                "answer": answer,
                "provider_info": ai.get_provider_info()
            })
            
        except Exception as e:
            logger.error(f"Universal AI error: {str(e)}")
            return Response({
                "error": f"Error: {str(e)}",
                "details": "The AI system encountered an issue. Please try again."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnifiedQuizGeneratorView(APIView):
    """Unified quiz generation - supports all providers"""
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]
    
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
    permission_classes = [AllowAny]
    
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
