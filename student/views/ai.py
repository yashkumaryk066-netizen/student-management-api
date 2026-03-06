from .base import *
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from student.models import (
    StudentLead, SubstituteAllocation, StudentPerformanceInsight,
    OnlineExam, OnlineQuestion, ExamAttempt, ExamResponse,
    AISubscription, Payment, UserProfile
)
from student.serializers import (
    StudentLeadSerializer, SubstituteAllocationSerializer, StudentPerformanceInsightSerializer, 
    OnlineExamSerializer, OnlineQuestionSerializer, ExamAttemptSerializer, ExamResponseSerializer
)
from student.permissions import IsTeacherOrAdmin
from ai.manager import get_ai_manager, AIServiceManager
from student.constants import AI_SUBSCRIPTION_PRICE
from decimal import Decimal
from drf_spectacular.utils import extend_schema

# --- AI HUB ---

class AIAuthView(APIView):
    """
    Legacy AI auth endpoint required by existing templates:
    GET  -> render auth page
    POST -> login/signup
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        return render(request, 'student/ai_auth.html')

    def post(self, request):
        action = (request.data.get('action') or '').strip().lower()
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=400)

        if action == 'signup':
            if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
                return Response({"error": "User already exists. Please login."}, status=400)

            user = User.objects.create_user(username=email, email=email, password=password)
            profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'AI_USER'})
            if profile.role != 'AI_USER':
                profile.role = 'AI_USER'
                profile.save(update_fields=['role'])
            AISubscription.objects.get_or_create(user=user)
            login(request, user)
            return Response({"success": True, "redirect": "/api/ai/chat/"})

        # Default behavior: login
        user = authenticate(request, username=email, password=password)
        if user is None:
            existing = User.objects.filter(email__iexact=email).first()
            if existing:
                user = authenticate(request, username=existing.username, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        login(request, user)
        AISubscription.objects.get_or_create(user=user)
        return Response({"success": True, "redirect": "/api/ai/chat/"})

class AIChatView(APIView):
    """Main AI Chat interface using AIServiceManager"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.shortcuts import redirect as django_redirect

        # If user is not logged in, send them to the AI auth page
        if not request.user.is_authenticated:
            return django_redirect('/api/ai/auth/')

        display_name = (
            getattr(request.user, 'first_name', None) or request.user.username
        )
        role = "Administrator" if request.user.is_staff else "Member"

        context = {
            "display_name": display_name,
            "role": role,
            "is_authenticated": True,
        }
        return render(request, 'student/ai_chat.html', context)

    def post(self, request):
        # Require authentication for AI chat API calls to prevent abuse
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required. Please login to use AI chat."}, status=401)

        question = request.data.get('message')
        if not question:
            return Response({"error": "Message is required"}, status=400)

        ai = get_ai_manager()
        response = ai.ask_tutor(question, context=request.data.get('context', ''))
        return Response({"answer": response})


class AIPaymentSubmitView(APIView):
    """
    Legacy endpoint used by AI chat template.
    Accepts manual UTR and creates pending verification payment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        transaction_id = (request.data.get('transaction_id') or '').strip()
        if not transaction_id:
            return Response({"error": "Transaction ID is required"}, status=400)

        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return Response({"error": "This transaction ID is already used."}, status=400)

        payment = Payment.objects.create(
            user=request.user,
            amount=Decimal(AI_SUBSCRIPTION_PRICE),
            transaction_id=transaction_id,
            payment_type='SUBSCRIPTION',
            payment_mode='UPI',
            status='PENDING_VERIFICATION',
            description='AI Subscription - Manual',
            due_date=timezone.now().date(),
            paid_date=timezone.now().date()
        )

        sub, _ = AISubscription.objects.get_or_create(user=request.user)
        sub.status = 'PENDING'
        sub.last_payment_id = transaction_id
        sub.amount_paid = (sub.amount_paid or Decimal('0')) + payment.amount
        sub.save()

        return Response({"success": True, "message": "Payment submitted. Waiting for approval."})

class AITutorView(APIView):
    """AI-powered tutoring endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        question = request.data.get('question')
        subject = request.data.get('subject', 'General')
        context = request.data.get('context', '')
        history = request.data.get('history', [])
        files = request.data.get('files', []) # Base64 images for vision
        
        if not question:
            return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        ai = get_ai_manager()
        answer = ai.ask_tutor(
            question, 
            subject=subject, 
            context=context, 
            history=history, 
            media_data=files
        )
        
        return Response({
            "success": True,
            "answer": answer,
            "provider": ai.provider
        })

class AIProvidersListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        ai = get_ai_manager()
        return Response(ai.get_available_providers())

class QuizGeneratorView(APIView):
    """AI-powered quiz generation"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        topic = request.data.get('topic')
        num_questions = request.data.get('num_questions', 5)
        difficulty = request.data.get('difficulty', 'medium')
        
        if not topic:
            return Response({"error": "Topic is required"}, status=400)
        
        ai = get_ai_manager()
        quiz = ai.generate_quiz(topic, num_questions, difficulty)
        return Response({"quiz": quiz})

class ContentSummarizerView(APIView):
    """Summarize long educational content"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        text = request.data.get('text')
        max_length = request.data.get('max_length', 200)
        
        if not text:
            return Response({"error": "Text content is required"}, status=400)
        
        ai = get_ai_manager()
        summary = ai.summarize_content(text, max_length)
        return Response({"summary": summary})

class ConceptExplainerView(APIView):
    """Explain complex concepts"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        concept = request.data.get('concept')
        grade_level = request.data.get('grade_level', 'high school')
        
        if not concept:
            return Response({"error": "Concept is required"}, status=400)
            
        ai = get_ai_manager()
        explanation = ai.explain_concept(concept, grade_level)
        return Response({"explanation": explanation})

class ContentTranslatorView(APIView):
    """Translate educational content"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        text = request.data.get('text')
        target_language = request.data.get('target_language')
        
        if not text or not target_language:
            return Response({"error": "Text and target language required"}, status=400)
            
        ai = get_ai_manager()
        translation = ai.translate_content(text, target_language)
        return Response({"translation": translation})
class UnifiedAITutorView(APIView):
    """
    Unified AI Tutor endpoint used by the AI Chat frontend.
    Supports Session Auth (browser) and JWT/Token Auth (API clients).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get('question') or request.data.get('message', '')
        subject = request.data.get('subject', 'General')
        context = request.data.get('context', '')
        history = request.data.get('history', [])
        files = request.data.get('files', [])
        provider = request.data.get('provider', None)

        if not question:
            return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ai = get_ai_manager()
            # If user requested a specific provider, switch to it
            if provider:
                try:
                    ai = AIServiceManager.switch_provider(provider)
                except Exception:
                    pass  # Fall back to default provider silently


            answer = ai.ask_tutor(
                question,
                subject=subject,
                context=context,
                history=history,
                media_data=files
            )

            return Response({
                "success": True,
                "answer": answer,
                "provider": getattr(ai, 'provider', 'ai')
            })
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"UnifiedAITutorView error: {e}", exc_info=True)
            return Response(
                {"error": "AI service temporarily unavailable. Please try again."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

class ExamPaperGeneratorView(QuizGeneratorView):
    """Alias for QuizGeneratorView specialized for exams"""
    pass

class AssignmentGraderView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        assignment_text = request.data.get('assignment_text')
        rubric = request.data.get('rubric', 'Standard academic grading criteria')
        grade_level = request.data.get('grade_level', 'High School')
        
        if not assignment_text:
            return Response({"error": "Assignment text is required"}, status=400)
            
        ai = get_ai_manager()
        prompt = (
            f"Act as an expert academic grader for grade/level: {grade_level}. "
            f"Grade the following assignment based on this rubric: '{rubric}'. "
            f"Provide: 1. A letter grade (A-F). 2. Detailed feedback on strengths/weaknesses. "
            f"3. Specific suggestions for improvement. "
            f"\n\nAssignment Content:\n{assignment_text}"
        )
        
        grading_report = ai.ask_tutor(prompt, subject='Pedagogy')
        
        return Response({
            "success": True, 
            "grading_report": grading_report,
            "provider": ai.provider
        })

class LessonPlanGeneratorView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        topic = (request.data.get('topic') or '').strip()
        grade_level = request.data.get('grade_level', 'General')
        duration = int(request.data.get('duration_minutes', 45) or 45)

        if not topic:
            return Response({"error": "Topic is required"}, status=400)

        ai = get_ai_manager()
        prompt = (
            f"Create a structured lesson plan for topic '{topic}', grade/class '{grade_level}', "
            f"duration {duration} minutes. Include objectives, warm-up, teaching steps, activities, assessment."
        )
        lesson_plan = ai.ask_tutor(prompt, subject='Pedagogy')
        return Response({
            "success": True,
            "lesson_plan": lesson_plan
        })

class WritingAnalyzerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        text = request.data.get('text')
        focus_area = request.data.get('focus_area', 'General Quality')
        
        if not text:
            return Response({"error": "Text to analyze is required"}, status=400)
            
        ai = get_ai_manager()
        prompt = (
            f"Analyze the following text for '{focus_area}'. "
            f"Check for grammar, clarity, tone, and flow. "
            f"Provide a rewritten version that improves these aspects while maintaining the original meaning. "
            f"\n\nText:\n{text}"
        )
        
        analysis = ai.ask_tutor(prompt, subject='Language Arts')
        
        return Response({
            "success": True,
            "analysis": analysis,
            "provider": ai.provider
        })

# --- INTELLIGENCE MODULES (ViewSets) ---

class StudentLeadViewSet(viewsets.ModelViewSet):
    serializer_class = StudentLeadSerializer
    permission_classes = [IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'marketing'

    def get_queryset(self):
        return filter_by_owner(StudentLead.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class SubstituteAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = SubstituteAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            SubstituteAllocation.objects.select_related('absent_teacher', 'substitute_teacher'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class StudentPerformanceInsightView(generics.RetrieveAPIView):
    serializer_class = StudentPerformanceInsightSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
             student = user.student_profile
             obj, created = StudentPerformanceInsight.objects.get_or_create(
                 student=student,
                 defaults={'created_by': get_owner_user(user)}
             )
             return obj
        return None

# --- ONLINE EXAM SYSTEM ---

class OnlineExamViewSet(viewsets.ModelViewSet):
    serializer_class = OnlineExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(OnlineExam.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class ExamPortalView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, exam_id):
        return render(request, 'student/take_exam.html', {'exam_id': exam_id})

class OnlineExamInteractionView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(operation_id='online_exam_session_retrieve')
    def get(self, request, exam_id):
        exam = get_object_or_404(OnlineExam, id=exam_id)
        # Check ownership
        if exam.created_by != get_owner_user(request.user):
            return Response({"error": "Access Denied"}, status=403)
        return Response(OnlineExamSerializer(exam).data)

    @extend_schema(operation_id='online_exam_session_action')
    def post(self, request, exam_id, action=None):
        exam = get_object_or_404(OnlineExam, id=exam_id)
        
        # Verify student access
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "Only students can take exams"}, status=status.HTTP_403_FORBIDDEN)
            
        student = request.user.student_profile
        
        if action == 'start':
            # Check timing
            now = timezone.now()
            if now < exam.start_window:
                return Response({"error": "Exam window not yet open"}, status=400)
            if now > exam.end_window:
                return Response({"error": "Exam window closed"}, status=400)
                
            attempt, created = ExamAttempt.objects.get_or_create(
                exam=exam,
                student=student,
                defaults={
                    'ip_address': request.META.get('REMOTE_ADDR'),
                    'status': 'IN_PROGRESS'
                }
            )
            return Response(ExamAttemptSerializer(attempt).data)
            
        elif action == 'submit':
            attempt = get_object_or_404(ExamAttempt, exam=exam, student=student)
            if attempt.is_submitted:
                return Response({"error": "Exam already submitted"}, status=400)
            
            # --- SECURITY ENFORCEMENT: TIMER CHECK ---
            now = timezone.now()
            elapsed_minutes = (now - attempt.start_time).total_seconds() / 60
            if elapsed_minutes > (exam.duration_minutes + 5): # 5 min grace for network lag
                attempt.status = 'TERMINATED'
                attempt.save()
                return Response({
                    "error": "Exam duration exceeded. Access revoked.",
                    "code": "TIME_EXPIRED"
                }, status=403)
                
            # Process Responses
            responses_data = request.data.get('responses', [])
            total_score = 0
            
            for resp in responses_data:
                question_id = resp.get('question_id')
                marked_answer = resp.get('marked_answer')
                
                question = get_object_or_404(OnlineQuestion, id=question_id, exam=exam)
                
                is_correct = False
                points = 0
                
                # 1. Basic Auto-grading for MCQ/TF
                if question.question_type in ['MCQ', 'TF']:
                    if str(marked_answer).strip().upper() == str(question.correct_answer).strip().upper():
                        is_correct = True
                        points = question.marks
                
                # 2. Advanced AI Auto-grading for Subjective Answers (SA/LA)
                elif question.question_type in ['SA', 'LA']:
                    # Use AI to evaluate semantic meaning
                    try:
                        ai = get_ai_manager()
                        prompt = (
                            f"Act as a strict academic examiner. Grade this student response.\n"
                            f"Question: {question.question_text}\n"
                            f"Student Answer: {marked_answer}\n"
                            f"Reference/Correct Answer Key: {question.correct_answer}\n"
                            f"Max Marks: {question.marks}\n\n"
                            f"Evaluate based on accuracy, relevance, and completeness. "
                            f"Provide a JSON response with keys: 'score' (numeric), 'feedback' (string), 'is_correct' (boolean)."
                        )
                        # We use a lower level call or parse the response
                        # For MVP/Robustness, let's ask for specific format or trust the AI to be smart
                        evaluation = ai.ask_tutor(prompt, subject='Exam Grading')
                        
                        # Basic parsing (AI usually returns text, we need to extract score)
                        # This is a simplified implementation. Pro version would use structured output.
                        if "score" in evaluation.lower() and str(question.marks) in evaluation:
                            # Attempt to extract score
                            import re
                            score_match = re.search(r"score:\s*(\d+(\.\d+)?)", evaluation.lower())
                            if score_match:
                                points = float(score_match.group(1))
                                if points > float(question.marks): points = float(question.marks)
                        
                        # Feedback is the evaluation text
                        ai_feedback = evaluation
                        
                        # Determine correctness threshold (e.g. > 50% marks)
                        if points >= (float(question.marks) / 2):
                            is_correct = True
                            
                    except Exception as e:
                        # Fallback: Manual Grading required
                        logger.error(f"AI Auto-grading failed for Q{question.id}: {e}")
                        ai_feedback = "AI Grading unavailable. Manual review required."
                        points = 0
                        is_correct = False
                
                ExamResponse.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={
                        'marked_answer': marked_answer,
                        'is_correct': is_correct,
                        'points_awarded': points,
                        'ai_feedback': ai_feedback if 'ai_feedback' in locals() else '',
                        'ai_accuracy_score': int((points / float(question.marks)) * 100) if float(question.marks) > 0 else 0
                    }
                )
                total_score += points
            
            attempt.is_submitted = True
            attempt.submitted_at = timezone.now()
            attempt.score_obtained = total_score
            attempt.status = 'SUBMITTED'
            attempt.save()
            
            return Response({
                "success": True,
                "message": "Exam submitted successfully",
                "score": total_score
            })

class OnlineExamResultView(generics.RetrieveAPIView):
    serializer_class = ExamAttemptSerializer
    permission_classes = [IsAuthenticated]
    queryset = ExamAttempt.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'attempt_id'

class OnlineExamTemplateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def post(self, request):
        topic = request.data.get('topic')
        question_count = request.data.get('question_count', 10)
        difficulty = request.data.get('difficulty', 'Medium')
        
        if not topic:
             return Response({"error": "Exam topic is required"}, status=400)
             
        ai = get_ai_manager()
        prompt = (
            f"Create a structured exam template for '{topic}'. "
            f"Include {question_count} questions of {difficulty} difficulty. "
            f"Format as JSON with keys: 'question', 'options' (list), 'correct_answer', 'marks'. "
            f"Ensure strict JSON format only."
        )
        
        # In a real premium app, we would parse this JSON and create OnlineQuestion objects.
        # For now, we return the generated structure for the teacher to review/edit.
        exam_structure = ai.ask_tutor(prompt, subject='Exam Creation')
        
        return Response({
            "success": True,
            "exam_template": exam_structure
        })

class OnlineExamCertificateDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, attempt_id):
        attempt = get_object_or_404(ExamAttempt, id=attempt_id, student__user=request.user)
        
        if not attempt.is_submitted:
            return Response({"error": "Exam not yet submitted"}, status=400)
            
        # Mock certificate generation
        # Real implementation would use ReportLab or WeasyPrint to generate PDF
        certificate_data = {
            "student_name": attempt.student.user.get_full_name(),
            "exam_title": attempt.exam.title,
            "score": attempt.score_obtained,
            "date": attempt.submitted_at,
            "certificate_id": f"CERT-{attempt.id}-{attempt.exam.id}"
        }
        
        return Response({
            "success": True,
            "message": "Certificate data ready for rendering",
            "data": certificate_data,
            "download_url": f"/api/media/certificates/{attempt.id}.pdf" # Placeholder
        })

class PublicResultVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        return Response({"message": "Verification service active"})


@extend_schema(exclude=True)
class OnlineExamInteractionActionAliasView(OnlineExamInteractionView):
    pass
