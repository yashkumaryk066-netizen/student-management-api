from .base import *
from student.models import ChatConversation, ChatMessage
from student.models import Student, Attendence, Grade, Exam, Payment
from student.serializers import ChatConversationSerializer, ChatMessageSerializer
from ai.manager import get_ai_manager
import time

class ChatSendMessageView(APIView):
    """
    REAL AI Chat - Sends message to AI and saves to database with RAG context
    """
    permission_classes = [IsAuthenticated]

    def _get_rag_context(self, user):
        """Build REAL-TIME context about the student for RAG"""
        context_lines = []
        student = getattr(user, 'student_profile', None)
        if not student:
            return f"User Role: {getattr(user, 'profile', None).role if hasattr(user, 'profile') else 'User'}"

        context_lines.append(f"Student: {student.name} (Grade {student.grade})")
        
        # Attendance
        total_days = Attendence.objects.filter(student=student).count()
        if total_days > 0:
            present = Attendence.objects.filter(student=student, is_present=True).count()
            context_lines.append(f"Attendance: {int(present/total_days*100)}% ({present}/{total_days})")
        
        # Grades
        recent_grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-exam__exam_date')[:5]
        if recent_grades:
            context_lines.append("Recent Grades:")
            for g in recent_grades:
                context_lines.append(f"- {g.exam.name}: {g.marks_obtained}/{g.exam.total_marks}")

        # Payments
        pending = Payment.objects.filter(student=student, status='PENDING').count()
        context_lines.append(f"Pending Payments: {pending}")
            
        return "\n".join(context_lines)

    def post(self, request):
        conversation_id = request.data.get('conversation_id')
        user_message = request.data.get('message')
        ai_model = request.data.get('model', 'gemini-1.5-flash')
        
        if not user_message:
            return Response({'error': 'Message is required'}, status=400)
        
        # Conversation logic
        if conversation_id:
            conversation = get_object_or_404(ChatConversation, id=conversation_id, user=request.user)
        else:
            conversation = ChatConversation.objects.create(user=request.user, ai_model=ai_model)
        
        # Save user message
        ChatMessage.objects.create(conversation=conversation, role='user', content=user_message)
        if not conversation.title:
            conversation.auto_generate_title()
        
        # Call AI
        ai = get_ai_manager()
        rag_context = self._get_rag_context(request.user)
        full_context = f"SYSTEM RAG CONTEXT:\n{rag_context}\n\nUSER MESSAGE:\n{user_message}"
        
        ai_response = ai.ask_tutor(user_message, context=rag_context)
        
        # Save AI message
        ChatMessage.objects.create(conversation=conversation, role='ai', content=ai_response)
        
        return Response({
            "conversation_id": conversation.id,
            "answer": ai_response
        })

class ChatConversationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatConversationSerializer # Need to ensure this exists

    def get_queryset(self):
        return ChatConversation.objects.filter(user=self.request.user).order_by('-updated_at')

class ChatHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer # Need to ensure this exists

    def get_queryset(self):
        conv_id = self.kwargs.get('conversation_id')
        return ChatMessage.objects.filter(conversation_id=conv_id, conversation__user=self.request.user).order_by('timestamp')


class ChatHistoryLegacyView(APIView):
    """
    Backward-compatible endpoint for frontend code expecting:
    { success: true, conversations: [...] }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = ChatConversation.objects.filter(user=request.user).order_by('-updated_at')[:50]
        return Response({
            "success": True,
            "conversations": ChatConversationSerializer(conversations, many=True).data
        })


class ChatConversationDetailLegacyView(APIView):
    """
    Backward-compatible endpoint for frontend code expecting:
    { success: true, messages: [...] }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = ChatConversation.objects.filter(id=conversation_id, user=request.user).first()
        if not conversation:
            return Response({"success": False, "error": "Conversation not found"}, status=404)

        messages = ChatMessage.objects.filter(conversation=conversation).order_by('timestamp')
        return Response({
            "success": True,
            "messages": ChatMessageSerializer(messages, many=True).data
        })


class ChatSearchLegacyView(APIView):
    """
    Backward-compatible search endpoint used by legacy chat UI.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = (request.query_params.get('q') or '').strip()
        if len(q) < 2:
            return Response({"success": True, "results": []})

        conversations = ChatConversation.objects.filter(
            user=request.user,
            title__icontains=q
        ).order_by('-updated_at')[:20]
        return Response({
            "success": True,
            "results": ChatConversationSerializer(conversations, many=True).data
        })
