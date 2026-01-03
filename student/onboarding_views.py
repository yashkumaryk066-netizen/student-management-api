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
            # 2. Generate Credentials based on Plan (Advanced: Separate accounts for separate businesses)
            # 2. Manage Subscription (Create or Renew)
            from datetime import timedelta
            from django.utils import timezone
            
            email_prefix = email.split('@')[0]
            plan_suffix = plan_type[:3].lower() 
            target_username = f"{email_prefix}_{plan_suffix}"
            
            password = phone[-6:] 
            
            # Check if this user already exists for this plan
            user = User.objects.filter(username=target_username).first()
            
            is_renewal = False
            
            if user:
                # RE-ACTIVATE / RENEW EXISTING ACCOUNT
                is_renewal = True
                user.set_password(password)
                user.is_active = True # Ensure active
                user.save()
                
                # Update Profile Expiry
                profile = UserProfile.objects.get(user=user)
                
                # If valid, extend. If expired, reset from today.
                if profile.subscription_expiry and profile.subscription_expiry > timezone.now().date():
                    profile.subscription_expiry += timedelta(days=30)
                else:
                    profile.subscription_expiry = timezone.now().date() + timedelta(days=30)
                
                profile.institution_type = plan_type.upper() # Ensure consistent
                profile.save()
                
                username = target_username
                logger.info(f"Renewed Subscription for: {username}")
                
            else:
                # CREATE NEW ACCOUNT
                username = target_username
                
                # Check collision with other email using same prefix (edge case)
                import random, string
                while User.objects.filter(username=username).exists():
                     random_digits = ''.join(random.choices(string.digits, k=3))
                     username = f"{target_username}{random_digits}"
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                user.is_active = True
                user.save()
                
                # Create Profile with 30 Day Expiry
                profile = UserProfile.objects.create(
                    user=user,
                    role='ADMIN',
                    phone=phone,
                    institution_type=plan_type.upper(),
                    subscription_expiry=timezone.now().date() + timedelta(days=30)
                )
                logger.info(f"Created New Subscription for: {username}")
                
                # 3. Notification Content
                
                # 3. Create Internal Notifications (Fixing "Notification System")
                from .models import Notification
                
                # A) For the New Client
                Notification.objects.create(
                    recipient=user,
                    recipient_type='ADMIN', # They are Admin of their institute
                    title='Welcome to IMS Premium!',
                    message=f'Your {plan_type} plan is active. Use the menu to manage your institution. Your credentials: {username} / {password} '
                )
                
                # B) For the Super Admin (You)
                super_admin = User.objects.filter(is_superuser=True).first()
                if super_admin:
                    Notification.objects.create(
                        recipient=super_admin,
                        recipient_type='ADMIN',
                        title='New Subscription Sold! 💰',
                        message=f'Plan: {plan_type}, Amount: ₹{amount}, Client: {username} ({phone}).'
                    )
                
                # 4. External Notification Content (WhatsApp/Email)
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
