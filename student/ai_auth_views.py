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
        
        # Custom Check for Pending Approval
        try:
            user_check = User.objects.get(username=username)
            if user_check.check_password(password):
                if not user_check.is_active:
                    return Response({"error": "ACCESS DENIED: Account is Pending Approval by Super Admin."}, status=403)
        except User.DoesNotExist:
            pass

        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({"success": True, "redirect": "/api/ai/chat/"})
        else:
            return Response({"error": "Invalid Identity or Security Key."}, status=401)

    def handle_signup(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if not email or not password:
             return Response({"error": "Email and Password are required"}, status=400)
             
        # Basic Val
        if User.objects.filter(username=email).exists():
             return Response({"error": "User with this identity already exists. Please login."}, status=400)

        # Create User (INACTIVE by default)
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.is_active = False # WAIT FOR SUPER ADMIN APPROVAL
            user.save()
            
            # Create Profile with AI_USER role
            UserProfile.objects.create(
                user=user,
                role='AI_USER',
            )
            
            # Note: We do NOT login the user here.
            
            return Response({"success": True, "redirect": None, "message": "IDENTITY REGISTERED. STATUS: PENDING APPROVAL."})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)
