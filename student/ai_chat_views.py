from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class AIChatView(APIView):
    """
    Serve the Premium Y.S.M AI Chat Interface.
    Publicly accessible but API calls might need auth.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return render(request, 'student/ai_chat.html')
