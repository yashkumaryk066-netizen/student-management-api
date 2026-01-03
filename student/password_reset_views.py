from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging

logger = logging.getLogger(__name__)

# Temporary In-Memory Store for OTPs (For Production, use Redis or Database)
# Structure: {'email': {'otp': '1234', 'expires_at': datetime}}
OTP_STORE = {}

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone') # Optional, but user mentioned it.
        
        # Priority on Email for delivery
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email=email).first()
        if not user:
            # Security: Don't reveal user existence
            return Response({'message': 'If an account exists, an OTP has been sent.'}, status=status.HTTP_200_OK)
            
        # Generate 4 Digit OTP
        otp = ''.join(random.choices(string.digits, k=4))
        
        # Save to Store
        OTP_STORE[email] = {
            'otp': otp,
            'expires_at': timezone.now() + timedelta(minutes=10)
        }
        
        # Send Email
        try:
            send_mail(
                subject="Password Reset OTP - IMS Premium",
                message=f"Your OTP for password reset is: {otp}\nValid for 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )
            logger.info(f"OTP Sent to {email}: {otp}") # Log for debugging/demo
        except Exception as e:
            logger.error(f"Failed to send OTP: {e}")
            return Response({'error': 'Failed to send OTP'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)

class VerifyAndResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not email or not otp or not new_password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        stored_data = OTP_STORE.get(email)
        
        if not stored_data:
            return Response({'error': 'Invalid or expired OTP request'}, status=status.HTTP_400_BAD_REQUEST)
            
        if timezone.now() > stored_data['expires_at']:
            del OTP_STORE[email]
            return Response({'error': 'OTP Expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        if stored_data['otp'] != otp:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
        # OTP Valid - Reset Password
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear OTP
            del OTP_STORE[email]
            
            # Send Confirmation Notification (Mock/Log)
            logger.info(f"Password reset success for {email}")
            
            return Response({'message': 'Password reset successful! You can now login.'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
