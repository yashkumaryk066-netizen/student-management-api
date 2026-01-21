"""
Real Chat API - Complete Implementation
Connects frontend to backend AI
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg
from .chat_models import ChatConversation, ChatMessage, UserNotification
from .models import Student, Attendence, Grade, Exam, Payment, Subject
from django.utils import timezone
from ai.manager import get_ai_manager
import logging
import time

logger = logging.getLogger(__name__)


class ChatSendMessageView(APIView):
    """
    REAL AI Chat - Sends message to AI and saves to database
    """
    permission_classes = [IsAuthenticated]

    def _get_rag_context(self, user):
        """
        Build REAL-TIME context about the student for RAG.
        This allows AI to know the student's marks, attendance, and status.
        """
        context_lines = []
        
        # Check if user is a student
        try:
            # Access related name 'student_profile' from Student model
            student = getattr(user, 'student_profile', None)
            if not student:
                # Fallback: check if user has a profile with role
                role = getattr(user, 'profile', None).role if hasattr(user, 'profile') else 'User'
                return f"User Role: {role}"
                
        except Exception:
            return "User Type: Standard User"

        # 1. Basic Info
        context_lines.append(f"Student Profile: {student.name} (Grade {student.grade})")
        
        # 2. Attendance Summary
        total_days = Attendence.objects.filter(student=student).count()
        if total_days > 0:
            present_days = Attendence.objects.filter(student=student, is_present=True).count()
            attendance_pct = (present_days / total_days * 100)
            context_lines.append(f"Attendance Record: {attendance_pct:.1f}% ({present_days}/{total_days} days present)")
        else:
            context_lines.append("Attendance Record: No data yet.")
        
        # 3. Recent Academic Performance (Last 5 Grades)
        recent_grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-exam__exam_date')[:5]
        if recent_grades:
            context_lines.append("Recent Exam Results:")
            for g in recent_grades:
                subject_name = g.exam.subject.name if g.exam.subject else 'General'
                context_lines.append(f"- {g.exam.name} ({subject_name}): {g.marks_obtained}/{g.exam.total_marks} ({g.status})")
        else:
            context_lines.append("Academic Results: No grades recorded yet.")
        
        # 4. Upcoming Exams (Next 30 days)
        today = timezone.now().date()
        upcoming_exams = Exam.objects.filter(
            grade_class__icontains=str(student.grade),
            exam_date__gte=today
        ).order_by('exam_date')[:3]
        
        if upcoming_exams:
            context_lines.append("Upcoming Exams:")
            for e in upcoming_exams:
                days_left = (e.exam_date - today).days
                context_lines.append(f"- {e.name}: {e.exam_date} (in {days_left} days)")

        # 5. Fee Status
        overdue_payments = Payment.objects.filter(student=student, status='OVERDUE').count()
        if overdue_payments > 0:
            context_lines.append(f"Fee Status: ⚠️ {overdue_payments} Overdue Payments")
        else:
            context_lines.append("Fee Status: All clear")
            
        return "\n".join(context_lines)

    def post(self, request):
        try:
            conversation_id = request.data.get('conversation_id')
            user_message = request.data.get('message')
            ai_model = request.data.get('model', 'gemini-2.0-flash')
            system_prompt = request.data.get('system_prompt', '')
            images = request.data.get('images', [])  # List of Base64 strings
            
            if not user_message:
                return Response({
                    'error': 'Message is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create conversation
            if conversation_id:
                try:
                    conversation = ChatConversation.objects.get(
                        id=conversation_id,
                        user=request.user
                    )
                except ChatConversation.DoesNotExist:
                    conversation = ChatConversation.objects.create(
                        user=request.user,
                        ai_model=ai_model
                    )
            else:
                conversation = ChatConversation.objects.create(
                    user=request.user,
                    ai_model=ai_model
                )
            
            # Save user message
            user_msg = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_message,
                model=ai_model
            )
            
            # Call REAL AI with EXPERT MODE (Auto error detection + correction)
            start_time = time.time()
            try:
                # Import expert Gemini directly for full control
                from ai.gemini import get_gemini_service
                ai_service = get_gemini_service()
                
                # Build message history for context
                previous_messages = ChatMessage.objects.filter(
                    conversation=conversation
                ).order_by('timestamp')[:10]  # Last 10 messages
                
                context = []
                
                # --- INJECT RAG CONTEXT (Student Data) ---
                student_data = self._get_rag_context(request.user)
                rag_message = f"""
SYSTEM CONTEXT (REAL-TIME USER DATA):
You have access to the following live data about the student you are chatting with:
{student_data}

INSTRUCTIONS:
- Use this data to answer questions like "What are my marks?", "How is my attendance?", or "Any upcoming exams?".
- If marks are low, offer study tips.
- If attendance is low, suggest catching up.
- This is PRIVATE data, do not share it unless asked.
"""
                # Add as system context
                context.append({'role': 'system', 'content': rag_message})
                # -----------------------------------------
                
                for msg in previous_messages:
                    context.append({
                        'role': 'user' if msg.role == 'user' else 'assistant',
                        'content': msg.content
                    })
                
                # Detect mode based on message content
                mode = 'general'
                if any(keyword in user_message.lower() for keyword in ['error', 'bug', 'fix', 'wrong', 'не работает']):
                    mode = 'debug'
                elif any(keyword in user_message.lower() for keyword in ['review', 'check', 'optimize']):
                    mode = 'code_review'
                elif any(keyword in user_message.lower() for keyword in ['deploy', 'production', 'pythonanywhere']):
                    mode = 'production'
                elif any(keyword in user_message.lower() for keyword in ['security', 'safe', 'secure','vulnerable']):
                    mode = 'security'
                elif any(keyword in user_message.lower() for keyword in ['slow', 'fast', 'performance', 'optimize']):
                    mode = 'performance'
                
                # Use EXPERT CHAT with auto error detection
                ai_response = ai_service.expert_chat(
                    user_message=user_message,
                    mode=mode,
                    context=context,
                    detect_errors=True,  # ✅ ALWAYS detect and fix errors automatically
                    images=images # Pass images if any
                )
                
                response_time = int((time.time() - start_time) * 1000)  # ms
                
            except Exception as ai_error:
                logger.error(f"AI Error: {ai_error}")
                ai_response = f"⚠️ AI Error: {str(ai_error)}"
                response_time = 0
            
            # Save AI response
            ai_msg = ChatMessage.objects.create(
                conversation=conversation,
                role='ai',
                content=ai_response,
                model=ai_model,
                response_time_ms=response_time
            )
            
            # Auto-generate title from first message
            if conversation.total_messages == 0:
                conversation.auto_generate_title()
            
            # Update conversation stats
            conversation.total_messages += 2
            conversation.save()
            
            return Response({
                'success': True,
                'conversation_id': conversation.id,
                'message': {
                    'id': ai_msg.id,
                    'content': ai_response,
                    'timestamp': ai_msg.timestamp,
                    'response_time_ms': response_time
                },
                'conversation_title': conversation.title
            })
            
        except Exception as e:
            logger.error(f"Chat Error: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatHistoryView(APIView):
    """
    Get all conversations for user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        conversations = ChatConversation.objects.filter(
            user=request.user,
            is_archived=False
        )[:20]
        
        data = []
        for conversation in conversations:
            last_message = conversation.messages.last()
            data.append({
                'id': conversation.id,
                'title': conversation.title or f"Chat {conversation.created_at.strftime('%b %d')}",
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'message_count': conversation.total_messages,
                'is_pinned': conversation.is_pinned,
                'last_message': last_message.content[:100] if last_message else '',
                'ai_model': conversation.ai_model
            })
        
        return Response({
            'success': True,
            'conversations': data,
            'total': len(data)
        })


class ChatLoadConversationView(APIView):
    """
    Load specific conversation with all messages
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversation_id):
        try:
            conversation = ChatConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
            
            messages = ChatMessage.objects.filter(
                conversation=conversation
            ).order_by('timestamp')
            
            message_data = [{
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_edited': msg.is_edited
            } for msg in messages]
            
            return Response({
                'success': True,
                'conversation': {
                    'id': conversation.id,
                    'title': conversation.title,
                    'created_at': conversation.created_at.isoformat(),
                    'ai_model': conversation.ai_model
                },
                'messages': message_data
            })
            
        except ChatConversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ChatSearchView(APIView):
    """
    Search through chat history
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.GET.get('q', '')
        
        if len(query) < 2:
            return Response({
                'success': True,
                'results': []
            })
        
        # Search in messages
        messages = ChatMessage.objects.filter(
            Q(content__icontains=query),
            conversation__user=request.user,
            conversation__is_archived=False
        ).select_related('conversation')[:20]
        
        results = []
        seen_conversations = set()
        
        for msg in messages:
            if msg.conversation.id not in seen_conversations:
                results.append({
                    'conversation_id': msg.conversation.id,
                    'conversation_title': msg.conversation.title,
                    'content': msg.content[:200],
                    'timestamp': msg.timestamp.isoformat(),
                    'role': msg.role
                })
                seen_conversations.add(msg.conversation.id)
        
        return Response({
            'success': True,
            'results': results,
            'query': query
        })


class NotificationListView(APIView):
    """
    Get user notifications
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        notifications = UserNotification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        unread_count = UserNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        data = [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'action_link': n.action_link,
            'action_text': n.action_text
        } for n in notifications]
        
        return Response({
            'success': True,
            'notifications': data,
            'unread_count': unread_count
        })
    
    def post(self, request):
        """Mark notification as read"""
        notification_id = request.data.get('notification_id')
        
        try:
            notification = UserNotification.objects.get(
                id=notification_id,
                user=request.user
            )
            notification.is_read = True
            notification.save()
            
            return Response({'success': True})
        except UserNotification.DoesNotExist:
            return Response({
                'error': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ChatDeleteView(APIView):
    """
    Delete or archive conversation
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, conversation_id):
        try:
            conversation = ChatConversation.objects.get(
                id=conversation_id,
                user=request.user
            )
            
            # Archive instead of delete (safer)
            conversation.is_archived = True
            conversation.save()
            
            return Response({'success': True})
            
        except ChatConversation.DoesNotExist:
            return Response({
                'error': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
