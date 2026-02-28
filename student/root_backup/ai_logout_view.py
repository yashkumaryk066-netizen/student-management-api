from django.shortcuts import redirect
from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class AILogoutView(APIView):
    """
    Handle Secure Logout for AI Platform.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logout(request)
        return redirect('/api/ai/auth/')

    def post(self, request):
        logout(request)
        return redirect('/api/ai/auth/')
