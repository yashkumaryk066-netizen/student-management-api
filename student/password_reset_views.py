from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import UserProfile, Notification
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import random
import string
import logging

logger = logging.getLogger(__name__)

# Temporary In-Memory Store
# { 'identifier_string': {'otp': '1234', 'user_id': 1, 'expires_at': datetime} }
OTP_STORE = {}

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        identifier = request.data.get('identifier') # Email or Phone
        
        if not identifier:
            return Response({'error': 'Email or Phone is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Find User by Email OR Phone
        user = None
        
        # Try Email
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        
        # Try Phone (via Profile)
        if not user:
            try:
                profile = UserProfile.objects.filter(phone=identifier).first()
                if profile:
                    user = profile.user
            except:
                pass
        
        if not user:
            # Fake success for security (or just say sent)
            return Response({'message': 'If an account exists, OTP sent.'}, status=status.HTTP_200_OK)
            
        # 2. Generate OTP
        otp = ''.join(random.choices(string.digits, k=4))
        
        # 3. Store OTP mapped to the IDENTIFIER provided (so verify step works)
        OTP_STORE[identifier] = {
            'otp': otp,
            'user_id': user.id,
            'expires_at': timezone.now() + timedelta(minutes=10)
        }
        
        # 4. Send OTP to BOTH Email and Phone (if available)
        email_sent = False
        phone_sent = False
        
        # A) Send to Email
        if user.email:
            try:
                send_mail(
                    subject="Password Reset OTP - IMS Premium",
                    message=f"Your OTP is: {otp}\nValid for 10 minutes.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
                email_sent = True
                logger.info(f"OTP Email Sent to {user.email}")
            except Exception as e:
                logger.error(f"OTP Email Failed: {e}")

        # B) Send to Phone (Mock)
        user_phone = None
        if hasattr(user, 'profile') and user.profile.phone:
            user_phone = user.profile.phone
            self.send_whatsapp_mock(user_phone, f"Your IMS Password Reset OTP is: {otp}")
            phone_sent = True
        
        return Response({
            'message': f'OTP sent to registered Email & Phone.',
            'debug_info': 'Check console for OTP'
        }, status=status.HTTP_200_OK)

    def send_whatsapp_mock(self, number, message):
        log_msg = f"🚀 [WHATSAPP to {number}]: {message}"
        logger.info(log_msg)
        print(log_msg)

class VerifyAndResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        identifier = request.data.get('identifier')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not identifier or not otp or not new_password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        stored_data = OTP_STORE.get(identifier)
        
        if not stored_data:
            return Response({'error': 'Invalid or expired OTP request'}, status=status.HTTP_400_BAD_REQUEST)
            
        if timezone.now() > stored_data['expires_at']:
            del OTP_STORE[identifier]
            return Response({'error': 'OTP Expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        if stored_data['otp'] != otp:
             return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
             
        # OTP Valid - Perform Reset
        try:
            user_id = stored_data['user_id']
            user = User.objects.get(id=user_id)
            
            # 1. Update Password
            user.set_password(new_password)
            user.save()
            
            # 2. Get Credentials for Display/Notify
            username = user.username
            
            # 3. Notifications (Requested by User: "email phone pe notification jaye id password")
            msg_body = (
                f"🔐 *Credentials Recovered*\n"
                f"Your account password has been reset.\n\n"
                f"👤 *ID:* {username}\n"
                f"🔑 *PASS:* {new_password}\n\n"
                f"Use these to login immediately."
            )
            
            # A) Email
            if user.email:
                send_mail(
                    subject="New Credentials - IMS Premium",
                    message=msg_body.replace('*', ''),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True
                )
            
            # B) Phone
            if hasattr(user, 'profile') and user.profile.phone:
                self.send_whatsapp_mock(user.profile.phone, msg_body)
                
            # Clear OTP
            del OTP_STORE[identifier]
            
            # 4. Return Credentials for Screen Display
            return Response({
                'message': 'Password Reset Successful!',
                'username': username,
                'password': new_password
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def send_whatsapp_mock(self, number, message):
        log_msg = f"🚀 [WHATSAPP to {number}]:\n{message}\n{'-'*30}"
        logger.info(log_msg)
        print(log_msg)
