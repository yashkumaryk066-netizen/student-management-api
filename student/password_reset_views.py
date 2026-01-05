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
        identifier = request.data.get('identifier')  # Email or Phone

        if not identifier:
            return Response(
                {'error': 'Email or Phone is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = None

        # -------- Find user --------
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()

        if not user:
            profile = UserProfile.objects.filter(phone=identifier).first()
            if profile:
                user = profile.user

        # Fake success (security)
        if not user:
            return Response(
                {'message': 'If an account exists, OTP sent.'},
                status=status.HTTP_200_OK
            )

        # -------- Invalidate old OTPs --------
        PasswordResetOTP.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        # -------- Generate OTP --------
        otp = ''.join(random.choices(string.digits, k=4))

        PasswordResetOTP.objects.create(
            user=user,
            otp_code=otp,
            identifier=identifier,
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        # -------- Send Email --------
        if user.email:
            send_mail(
                subject="Password Reset OTP - IMS Premium",
                message=f"Your OTP is: {otp}\nValid for 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )

        # -------- Send WhatsApp (Mock) --------
        if hasattr(user, 'profile') and user.profile.phone:
            self.send_whatsapp_mock(
                user.profile.phone,
                f"Your IMS Password Reset OTP is: {otp}"
            )

        return Response(
            {'message': 'OTP sent to registered Email & Phone.'},
            status=status.HTTP_200_OK
        )

    def send_whatsapp_mock(self, number, message):
        logger.info(f"[WHATSAPP → {number}] {message}")
        print(f"🚀 [WHATSAPP → {number}] {message}")


class VerifyAndResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not identifier or not otp or not new_password:
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_record = PasswordResetOTP.objects.filter(
            identifier=identifier,
            otp_code=otp,
            is_used=False
        ).first()

        if not otp_record:
            return Response(
                {'error': 'Invalid or Used OTP'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp_record.expires_at:
            return Response(
                {'error': 'OTP has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------- Reset password --------
        user = otp_record.user
        user.set_password(new_password)
        user.save()

        # -------- Mark ALL OTPs used --------
        PasswordResetOTP.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)

        # -------- Notifications --------
        msg_body = (
            f"Your password has been reset successfully.\n\n"
            f"Username: {user.username}\n"
            f"Password: {new_password}"
        )

        if user.email:
            send_mail(
                subject="Password Reset Successful - IMS Premium",
                message=msg_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )

        if hasattr(user, 'profile') and user.profile.phone:
            self.send_whatsapp_mock(user.profile.phone, msg_body)

        return Response(
            {'message': 'Password reset successful'},
            status=status.HTTP_200_OK
        )

    def send_whatsapp_mock(self, number, message):
        logger.info(f"[WHATSAPP → {number}] {message}")
        print(f"🚀 [WHATSAPP → {number}] {message}")
