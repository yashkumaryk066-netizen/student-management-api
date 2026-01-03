from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class OnboardingPaymentView(APIView):
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

        # 1. Verify Payment (Mock Logic for now)
        # In real world, verify signature from Payment Gateway
        is_payment_verified = True 
        
        if is_payment_verified:
            # 2. Create User Credentials
            username = email.split('@')[0]
            password = phone[-6:] # Simple password logic: last 6 digits of phone
            
            try:
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    # Update existing user role/plan if upgrading
                else:
                    user = User.objects.create_user(username=username, email=email, password=password)
                
                # Update Profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                profile.role = 'ADMIN'
                profile.phone = phone
                profile.institution_type = plan_type.upper()
                profile.save()
                
                # 3. Simulate WhatsApp Notification to Admin (8356926231)
                admin_msg = f"💰 New Payment Received!\nUser: {email}\nPhone: {phone}\nPlan: {plan_type}\nAmount: ₹{amount}\nStatus: Active"
                self.send_whatsapp_mock('8356926231', admin_msg)
                
                # 4. Simulate WhatsApp Credentials to User
                user_msg = f"✅ Account Activated!\nWelcome to IMS.\nUsername: {username}\nPassword: {password}\nLogin here: https://yashamishra.pythonanywhere.com/login/"
                self.send_whatsapp_mock(phone, user_msg)
                
                return Response({
                    'message': 'Account created successfully! Credentials sent to WhatsApp.',
                    'credentials': {'username': username, 'password': password}, # Returning for demo purposes
                    'redirect_url': '/login/'
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Onboarding Error: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'error': 'Payment Verification Failed'}, status=status.HTTP_400_BAD_REQUEST)

    def send_whatsapp_mock(self, number, message):
        """
        Mock function to simulate sending WhatsApp message.
        In production, replace with Twilio or similar API.
        """
        logger.info(f"🚀 [WHATSAPP to {number}]: {message}")
        print(f"🚀 [WHATSAPP to {number}]: {message}")
