from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

from rest_framework.permissions import AllowAny

class OnboardingPaymentView(APIView):
    permission_classes = [AllowAny]
    """
    Handles plan purchase and user onboarding.
    Mocks payment verification and sends credentials via 'WhatsApp'.
    """
    
    def post(self, request):
        phone = request.data.get('phone')
        email = request.data.get('email')
        plan_type = request.data.get('plan_type') # SCHOOL, COACHING, INSTITUTE
        amount = request.data.get('amount')
        
        if not phone or not email or not plan_type:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        PRICING = {
            'COACHING': 500,
            'SCHOOL': 10000,
            'INSTITUTE': 15000
        }
        expected_amount = PRICING.get(plan_type.upper(), 0)

        if int(amount) < expected_amount:
             return Response({
                 'error': f'Payment Amount Mismatch. Expected ₹{expected_amount} for {plan_type} plan, but received ₹{amount}.'
             }, status=status.HTTP_400_BAD_REQUEST)
        
        # Simulate Bank Verification Delay
        import time
        time.sleep(2)  # 2 seconds delay to simulate checking with Bank Server
        
        is_payment_verified = True 
        
        if is_payment_verified:
            # 2. Generate Credentials
            username = email.split('@')[0]
            # Ensure unique username
            if User.objects.filter(username=username).exists():
                username = f"{username}_{phone[-4:]}"
                
            password = phone[-6:] # Simple password: last 6 digits
            
            try:
                # Create or Get User
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={'username': username}
                )
                if created:
                    logger.info(f"Created new user: {username}")
                else:
                    logger.info(f"Updated existing user: {username}")
                
                # ALWAYS set the password to the generated one so the credentials shown to the user WORK.
                # This handles cases where a user retries payment or comes back.
                user.set_password(password)
                user.is_active = True
                user.save()
                
                # Update Profile Permissions
                # They get 'ADMIN' role for their specific Institution Type
                profile, p_created = UserProfile.objects.get_or_create(user=user)
                profile.role = 'ADMIN' 
                profile.phone = phone
                profile.institution_type = plan_type.upper()
                profile.save()
                
                # 3. Notification Content
                login_url = "https://yashamishra.pythonanywhere.com/login/"
                
                client_msg = (
                    f"🎉 *Welcome to IMS Premium!*\n\n"
                    f"Your *{plan_type} Management System* is ready.\n"
                    f"👤 *ID:* {username}\n"
                    f"🔑 *Pass:* {password}\n"
                    f"🔗 *Login:* {login_url}\n\n"
                    f"Please keep this confidential."
                )
                
                super_admin_msg = (
                    f"💰 *New Subscription Sold!*\n"
                    f"📦 *Plan:* {plan_type}\n"
                    f"💵 *Amount:* ₹{amount}\n"
                    f"👤 *Client:* {username} ({phone})\n"
                    f"📧 *Email:* {email}\n"
                    f"🔑 *Generated Creds:* {username} / {password}"
                )
                
                # 4. Send Notifications
                
                # A) WhatsApp
                self.send_whatsapp_mock(phone, client_msg, "CLIENT")
                self.send_whatsapp_mock('8356926231', super_admin_msg, "SUPER_ADMIN")
                
                # B) Email (Console Backend usually on Dev, but trying to send)
                from django.core.mail import send_mail
                try:
                    send_mail(
                        subject=f"Welcome to IMS - Your {plan_type} Dashboard Ready!",
                        message=client_msg.replace('*', ''), # Remove Markdown for plain text email
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=True
                    )
                    logger.info(f"📧 [EMAIL Sent] to {email}")
                except Exception as mail_err:
                    logger.warning(f"📧 [EMAIL Failed]: {mail_err}")

                return Response({
                    'message': 'Account created successfully! Credentials sent to Email & WhatsApp.',
                    'display_credentials': {'username': username, 'password': password}, # Explicitly for Frontend Display
                    'redirect_url': '/login/'
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Onboarding Error: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'error': 'Payment Verification Failed'}, status=status.HTTP_400_BAD_REQUEST)

    def send_whatsapp_mock(self, number, message, recipient_type="USER"):
        """
        Mock function to simulate sending WhatsApp message.
        """
        log_msg = f"🚀 [WHATSAPP to {recipient_type} - {number}]:\n{message}\n{'-'*30}"
        logger.info(log_msg)
        print(log_msg) # Print to console so it appears in server logs for User to see
