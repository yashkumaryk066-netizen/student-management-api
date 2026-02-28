"""
ChatGPT AI API Views
Premium AI-powered endpoints for educational features
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ai.chatgpt import get_chatgpt_service
from .models import Student
from django.shortcuts import get_object_or_404
import logging

logger = logging.getLogger(__name__)


class ChatGPTHealthCheckView(APIView):
    """Health check for ChatGPT AI service"""
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        """Check if ChatGPT service is available"""
        try:
            service = get_chatgpt_service()
            return Response({
                "status": "operational",
                "service": "ChatGPT AI",
                "model": service.default_model,
                "features": [
                    "AI Tutoring",
                    "Quiz Generation",
                    "Assignment Grading",
                    "Content Summarization",
                    "Concept Explanation",
                    "Translation",
                    "Lesson Planning",
                    "Writing Analysis"
                ]
            })
        except Exception as e:
            return Response({
                "status": "unavailable",
                "error": str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class AITutorView(APIView):
    """AI-powered tutoring endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Ask the AI tutor a question
        
        Request body:
        {
            "question": "What is photosynthesis?",
            "subject": "Biology",
            "context": "Optional background info"
        }
        """
        try:
            question = request.data.get('question')
            subject = request.data.get('subject', 'General')
            context = request.data.get('context', '')
            
            if not question:
                return Response({
                    "error": "Question is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            answer = service.ask_tutor(question, subject, context)
            
            return Response({
                "success": True,
                "question": question,
                "subject": subject,
                "answer": answer,
                "model": service.default_model
            })
            
        except Exception as e:
            logger.error(f"AI Tutor error: {str(e)}")
            return Response({
                "error": "AI tutoring service failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizGeneratorView(APIView):
    """AI-powered quiz generation"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Generate quiz questions
        
        Request body:
        {
            "topic": "World War II",
            "num_questions": 5,
            "difficulty": "medium",
            "question_type": "multiple_choice"
        }
        """
        try:
            topic = request.data.get('topic')
            num_questions = request.data.get('num_questions', 5)
            difficulty = request.data.get('difficulty', 'medium')
            question_type = request.data.get('question_type', 'multiple_choice')
            
            if not topic:
                return Response({
                    "error": "Topic is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            quiz = service.generate_quiz(topic, num_questions, difficulty, question_type)
            
            return Response({
                "success": True,
                "topic": topic,
                "quiz": quiz,
                "num_questions": num_questions,
                "difficulty": difficulty
            })
            
        except Exception as e:
            logger.error(f"Quiz generation error: {str(e)}")
            return Response({
                "error": "Quiz generation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContentSummarizerView(APIView):
    """Summarize long educational content"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Summarize text content
        
        Request body:
        {
            "text": "Long text to summarize...",
            "max_length": 200
        }
        """
        try:
            text = request.data.get('text')
            max_length = request.data.get('max_length', 200)
            
            if not text:
                return Response({
                    "error": "Text content is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            summary = service.summarize_content(text, max_length)
            
            return Response({
                "success": True,
                "original_length": len(text.split()),
                "summary": summary,
                "summary_length": len(summary.split())
            })
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return Response({
                "error": "Summarization failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssignmentGraderView(APIView):
    """AI-powered assignment grading"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Grade an assignment
        
        Request body:
        {
            "assignment_text": "Student's submission...",
            "rubric": "Grading criteria...",
            "max_score": 100
        }
        """
        try:
            assignment_text = request.data.get('assignment_text')
            rubric = request.data.get('rubric')
            max_score = request.data.get('max_score', 100)
            
            if not assignment_text or not rubric:
                return Response({
                    "error": "Assignment text and rubric are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            grading_result = service.grade_assignment(assignment_text, rubric, max_score)
            
            return Response({
                "success": True,
                "grading": grading_result
            })
            
        except Exception as e:
            logger.error(f"Grading error: {str(e)}")
            return Response({
                "error": "Assignment grading failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConceptExplainerView(APIView):
    """Explain complex concepts in simple terms"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Explain a concept
        
        Request body:
        {
            "concept": "Quantum entanglement",
            "grade_level": "high school"
        }
        """
        try:
            concept = request.data.get('concept')
            grade_level = request.data.get('grade_level', 'high school')
            
            if not concept:
                return Response({
                    "error": "Concept is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            explanation = service.explain_concept(concept, grade_level)
            
            return Response({
                "success": True,
                "concept": concept,
                "grade_level": grade_level,
                "explanation": explanation
            })
            
        except Exception as e:
            logger.error(f"Concept explanation error: {str(e)}")
            return Response({
                "error": "Concept explanation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContentTranslatorView(APIView):
    """Translate educational content"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Translate content
        
        Request body:
        {
            "text": "Text to translate",
            "target_language": "Hindi"
        }
        """
        try:
            text = request.data.get('text')
            target_language = request.data.get('target_language')
            
            if not text or not target_language:
                return Response({
                    "error": "Text and target language are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            translated = service.translate_content(text, target_language)
            
            return Response({
                "success": True,
                "original": text,
                "target_language": target_language,
                "translated": translated
            })
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return Response({
                "error": "Translation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LessonPlanGeneratorView(APIView):
    """Generate comprehensive lesson plans"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Generate lesson plan
        
        Request body:
        {
            "topic": "Introduction to Algebra",
            "duration_minutes": 45,
            "grade_level": "middle school"
        }
        """
        try:
            topic = request.data.get('topic')
            duration_minutes = request.data.get('duration_minutes', 45)
            grade_level = request.data.get('grade_level', 'high school')
            
            if not topic:
                return Response({
                    "error": "Topic is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            lesson_plan = service.generate_lesson_plan(topic, duration_minutes, grade_level)
            
            return Response({
                "success": True,
                "topic": topic,
                "duration_minutes": duration_minutes,
                "grade_level": grade_level,
                "lesson_plan": lesson_plan
            })
            
        except Exception as e:
            logger.error(f"Lesson plan generation error: {str(e)}")
            return Response({
                "error": "Lesson plan generation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WritingAnalyzerView(APIView):
    """Analyze student writing"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Analyze writing sample
        
        Request body:
        {
            "writing_sample": "Student's essay or writing..."
        }
        """
        try:
            writing_sample = request.data.get('writing_sample')
            
            if not writing_sample:
                return Response({
                    "error": "Writing sample is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            analysis = service.analyze_student_writing(writing_sample)
            
            return Response({
                "success": True,
                "analysis": analysis
            })
            
        except Exception as e:
            logger.error(f"Writing analysis error: {str(e)}")
            return Response({
                "error": "Writing analysis failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomAIPromptView(APIView):
    """Custom AI prompts for flexible interactions"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Send custom prompt
        
        Request body:
        {
            "prompt": "Your custom question or request",
            "system_message": "Optional context for AI"
        }
        """
        try:
            prompt = request.data.get('prompt')
            system_message = request.data.get('system_message')
            
            if not prompt:
                return Response({
                    "error": "Prompt is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = get_chatgpt_service()
            response_text = service.custom_prompt(prompt, system_message)
            
            return Response({
                "success": True,
                "prompt": prompt,
                "response": response_text
            })
            
        except Exception as e:
            logger.error(f"Custom prompt error: {str(e)}")
            return Response({
                "error": "AI prompt failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
