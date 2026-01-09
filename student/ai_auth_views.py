from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import UserProfile
import re

class AIAuthView(APIView):
    """
    Handle Login/Signup for AI Platform securely.
    Public Access allowed for this view.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'student/ai_auth.html')

    def post(self, request):
        action = request.data.get('action')
        
        if action == 'login':
            return self.handle_login(request)
        elif action == 'signup':
            return self.handle_signup(request)
        else:
            return Response({"error": "Invalid Action"}, status=400)

    def handle_login(self, request):
        username = request.data.get('email') # Using email/phone as username
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({"success": True, "redirect": "/api/ai/chat/"})
        else:
            return Response({"error": "Invalid Credentials"}, status=401)

    def handle_signup(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if not email or not password:
             return Response({"error": "Email and Password are required"}, status=400)
             
        # Basic Val
        if User.objects.filter(username=email).exists():
             return Response({"error": "User with this identity already exists. Please login."}, status=400)

        # Create User
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            
            # Create Profile with AI_USER role
            # Assuming phone is stored somewhere, but UserProfile doesn't strictly have 'phone' field in snippets seen, 
            # let's modify UserProfile or just store generic.
            # Ideally UserProfile should be created.
            
            UserProfile.objects.create(
                user=user,
                role='AI_USER',
                # institution_type can be blank or 'PERSONAL'
            )
            
            login(request, user)
            return Response({"success": True, "redirect": "/api/ai/chat/"})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
