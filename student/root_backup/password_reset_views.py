from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import UserProfile, PasswordResetOTP, ClientSubscription
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from datetime import timedelta
import random
import string
import logging

logger = logging.getLogger(__name__)

def get_premium_otp_html(otp):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .email-container {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; }}
            .header {{ background: #020617; padding: 40px; text-align: center; color: #ffffff; }}
            .logo {{ font-family: 'Orbitron', Arial, sans-serif; font-size: 24px; font-weight: 900; letter-spacing: 4px; color: #ffffff; text-decoration: none; }}
            .subtitle {{ color: #e2b036; font-size: 10px; letter-spacing: 4px; margin-top: 5px; font-weight: 700; text-transform: uppercase; }}
            .content {{ padding: 40px; line-height: 1.6; color: #334155; }}
            .otp-box {{ background: #f8fafc; border: 2px dashed #e2b036; border-radius: 8px; padding: 20px; text-align: center; margin: 30px 0; font-size: 32px; font-weight: 900; letter-spacing: 12px; color: #020617; }}
            .footer {{ background: #f1f5f9; padding: 20px; text-align: center; font-size: 12px; color: #64748b; }}
            .caution {{ color: #ef4444; font-weight: 600; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div style="font-size: 28px; font-weight: 900; letter-spacing: 2px;">Y.S.M ADVANCE</div>
                <div class="subtitle">International Education System</div>
            </div>
            <div class="content">
                <p>Greetings from <strong>Y.S.M Intelligence</strong>,</p>
                <p>You have requested a secure access recovery for your management portal. Please use the following Protection Protocol Key to verify your identity:</p>
                <div class="otp-box">{otp}</div>
                <p>This code is valid for <strong>10 minutes</strong>. After verification, you will be prompted to apply a new security protocol (password).</p>
                <p class="caution">⚠️ If you did not initiate this request, please ignore this email and ensure your account security remains uncompromised.</p>
            </div>
            <div class="footer">
                <p>Engineered by Yash Kumar | Telepathy Infotech Intelligence</p>
                <p>© 2026 Y.S.M Advance Education System. All Rights Reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')

        if not identifier:
            return Response({'error': 'Identity handle is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. AUTHENTICATE SUBSCRIPTION CONTRACT
        user = None
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()
        else:
            profile = UserProfile.objects.filter(phone=identifier).first()
            if profile: user = profile.user

        if not user:
            return Response({'error': 'No portal found with this handle'}, status=status.HTTP_404_NOT_FOUND)

        # 2. VERIFY PURCHASED PLAN (Security check requested by user)
        # Check explicit subscription record or active profile plan
        has_plan = False
        sub = ClientSubscription.objects.filter(user=user, status='ACTIVE').first()
        if sub:
            has_plan = True
        else:
            profile = getattr(user, 'profile', None)
            if profile and profile.subscription_expiry and profile.subscription_expiry >= timezone.now().date():
                has_plan = True
        
        # Superusers are exempted from plan checks for maintenance
        if not has_plan and not user.is_superuser:
            return Response({
                'error': 'Restricted Access: No active purchased plan found for this identity.'
            }, status=status.HTTP_403_FORBIDDEN)

        # 3. GENERATE SECURE OTP
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        otp = ''.join(random.choices(string.digits, k=4))
        
        PasswordResetOTP.objects.create(
            user=user,
            otp_code=otp,
            identifier=identifier,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # 4. DISPATCH ELITE EMAIL
        if user.email:
            subject = "SECURITY RECOVERY: Protection Protocol Key — Y.S.M ADVANCE"
            text_content = f"Greetings from Y.S.M Intelligence. Your Recovery OTP is: {otp}. Valid for 10 minutes."
            html_content = get_premium_otp_html(otp)
            
            email = EmailMultiAlternatives(
                subject, 
                text_content, 
                settings.DEFAULT_FROM_EMAIL, 
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

        return Response({'message': 'Protocol key transmitted successfully.'}, status=status.HTTP_200_OK)


class VerifyAndResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not identifier or not otp or not new_password:
            return Response({'error': 'Incomplete data synchronization.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_record = PasswordResetOTP.objects.filter(
            identifier=identifier,
            otp_code=otp,
            is_used=False
        ).first()

        if not otp_record or not otp_record.is_valid():
            return Response({'error': 'Invalid or Expired Protocol Key.'}, status=status.HTTP_400_BAD_REQUEST)

        # RESET
        user = otp_record.user
        user.set_password(new_password)
        user.save()
        otp_record.is_used = True
        otp_record.save()

        # LOG & NOTIFY
        logger.info(f"🗝️ Password reset successful for user: {user.username}")
        
        return Response({
            'message': 'Security Protocol Overwritten Successfully.',
            'username': user.username,
            'password': new_password
        }, status=status.HTTP_200_OK)
