from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from .models import UserProfile, Notification, PasswordResetOTP
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging

logger = logging.getLogger(__name__)

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
            # Fake success for security
            return Response({'message': 'If an account exists, OTP sent.'}, status=status.HTTP_200_OK)
            
        # 2. Generate OTP
        otp = ''.join(random.choices(string.digits, k=4))
        
        # 3. Store OTP in Database (Persistent & Scalable)
        PasswordResetOTP.objects.create(
            user=user,
            otp_code=otp,
            identifier=identifier,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # 4. Send OTP to BOTH Email and Phone (if available)
        
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
                logger.info(f"OTP Email Sent to {user.email}")
            except Exception as e:
                logger.error(f"OTP Email Failed: {e}")

        # B) Send to Phone (Mock)
        if hasattr(user, 'profile') and user.profile.phone:
            self.send_whatsapp_mock(user.profile.phone, f"Your IMS Password Reset OTP is: {otp}")
        
        return Response({
            'message': f'OTP sent to registered Email & Phone.',
            'debug_info': 'Check console or logs for OTP if SMTP acts up.'
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
            
        # Debugging: Log what we received
        logger.info(f"Verify Attempt - ID: {identifier} | OTP: {otp}")

        # 1. Check if we have ANY record for this identifier
        candidates = PasswordResetOTP.objects.filter(identifier=identifier)
        if not candidates.exists():
            logger.warning(f"No OTP records found for identifier: {identifier}")
            return Response({'error': 'No OTP request found for this email/phone'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Check for Specific OTP Match
        otp_record = candidates.filter(otp_code=otp).first()
        
        if not otp_record:
            logger.warning(f"Invalid OTP code provided for {identifier}")
            return Response({'error': 'Invalid OTP Code'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 3. Check Status
        if otp_record.is_used:
            logger.warning(f"OTP already used for {identifier}")
            return Response({'error': 'This OTP has already been used'}, status=status.HTTP_400_BAD_REQUEST)
            
        # 4. Check Expiry
        if timezone.now() > otp_record.expires_at:
            logger.warning(f"OTP expired for {identifier}. Now: {timezone.now()}, Exp: {otp_record.expires_at}")
            return Response({'error': 'OTP has Expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
             
        # OTP Valid - Perform Reset
        try:
            user = otp_record.user
            
            # 1. Update Password
            user.set_password(new_password)
            user.save()
            
            # 2. Mark OTP as used
            otp_record.is_used = True
            otp_record.save()
            
            # 3. Notifications
            username = user.username
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
