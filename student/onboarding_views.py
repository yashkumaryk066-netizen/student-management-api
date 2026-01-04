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
        
        
        # Bank-Grade Triple-Layer Verification
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        # Require ALL three parameters - no bypass allowed
        if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
            return Response({
                'error': 'Payment Verification Failed',
                'message': 'Complete payment through official payment gateway. Manual entries are not accepted.',
                'required_fields': ['razorpay_payment_id', 'razorpay_order_id', 'razorpay_signature']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # STRICT RAZORPAY VERIFICATION - Three Security Layers
        is_payment_verified = False
        
        try:
            import razorpay
            # Load credentials from settings
            key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
            key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
            
            # Check if keys are configured
            if not key_id or not key_secret or 'YourKeyHere' in key_id or 'test_key' in key_id:
                return Response({
                    'error': 'Payment Gateway Not Configured',
                    'message': 'Payment processing is currently unavailable. Please contact support.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            client = razorpay.Client(auth=(key_id, key_secret))
            
            # === LAYER 1: Signature Verification ===
            # Prevents tampering with payment data
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
                logger.info(f"✅ Layer 1 Passed: Signature verified for {razorpay_payment_id}")
            except razorpay.errors.SignatureVerificationError as e:
                logger.error(f"❌ Layer 1 Failed: Signature verification failed - {e}")
                return Response({
                    'error': 'Security Alert: Payment Signature Invalid',
                    'message': 'Payment verification failed. This transaction appears to be tampered with.',
                    'action': 'Please retry payment or contact support'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # === LAYER 2: Fetch Payment Details from Bank ===
            # Cross-check with actual bank/Razorpay server
            try:
                payment_details = client.payment.fetch(razorpay_payment_id)
                logger.info(f"✅ Layer 2: Fetched payment details from bank - Status: {payment_details.get('status')}")
            except Exception as e:
                logger.error(f"❌ Layer 2 Failed: Could not fetch payment from bank - {e}")
                return Response({
                    'error': 'Bank Verification Failed',
                    'message': 'Unable to verify payment with bank. Please try again.',
                    'details': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # === LAYER 3: Payment Status Verification ===
            # Ensure payment was actually captured (completed)
            payment_status = payment_details.get('status')
            if payment_status != 'captured':
                logger.error(f"❌ Layer 3 Failed: Payment not captured - Status: {payment_status}")
                return Response({
                    'error': 'Payment Not Confirmed by Bank',
                    'message': f'Payment status is "{payment_status}". Only captured payments are accepted.',
                    'current_status': payment_status,
                    'action': 'Please complete the payment or try again'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # === LAYER 4: Amount Verification ===
            # Ensure paid amount matches expected amount (strict pricing)
            paid_amount_paise = payment_details.get('amount', 0)
            paid_amount = paid_amount_paise / 100  # Convert paise to rupees
            
            if int(paid_amount) < expected_amount:
                logger.error(f"❌ Layer 4 Failed: Amount mismatch - Expected: ₹{expected_amount}, Received: ₹{paid_amount}")
                return Response({
                    'error': 'Payment Amount Insufficient',
                    'message': f'Required ₹{expected_amount} for {plan_type} plan, but received ₹{paid_amount}',
                    'required': expected_amount,
                    'received': int(paid_amount)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # === ALL LAYERS PASSED ===
            is_payment_verified = True
            logger.info(f"✅✅✅ All Security Layers Passed for payment {razorpay_payment_id}")
            
        except Exception as e:
            logger.error(f"❌ Payment Verification Error: {str(e)}")
            return Response({
                'error': 'Payment Verification Failed',
                'message': 'An error occurred during bank verification.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


        if is_payment_verified:
            # 2. Generate Credentials based on Plan (Advanced: Separate accounts for separate businesses)
            try:
                # 2. Manage Subscription (Create or Renew)
                from datetime import timedelta
                from django.utils import timezone
                from .models import Notification
                from django.core.mail import send_mail
                
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
                    profile.phone = phone # Update phone number to latest provided
                    profile.save()
                    
                    username = target_username
                    logger.info(f"Renewed Subscription for: {username} - Preserving all existing data.")
                    
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
                
                # --- COMMON LOGIC FOR BOTH NEW AND RENEWAL ---
                
                # 3. Create Internal Notifications
                # A) For the Client
                Notification.objects.create(
                    recipient=user,
                    recipient_type='ADMIN',
                    title='Welcome to IMS Premium!',
                    message=f'Your {plan_type} plan is active (Valid for 30 Days). Credentials: {username} / {password} '
                )
                
                # B) For the Super Admin
                super_admin = User.objects.filter(is_superuser=True).first()
                if super_admin:
                    Notification.objects.create(
                        recipient=super_admin,
                        recipient_type='ADMIN',
                        title='Subscription Active 💰',
                        message=f'Type: {plan_type} {"(Renewed)" if is_renewal else "(New)"}, Amount: ₹{amount}, Client: {username}.'
                    )
                
                # 4. External Notifications
                login_url = "https://yashamishra.pythonanywhere.com/login/"
                
                client_msg = (
                    f"🎉 *IMS Premium Activated!*\n\n"
                    f"Plan: *{plan_type}*\n"
                    f"Status: *Active (30 Days)*\n"
                    f"👤 *ID:* {username}\n"
                    f"🔑 *Pass:* {password}\n"
                    f"🔗 *Login:* {login_url}\n"
                )
                
                super_admin_msg = (
                    f"💰 *Subscription Sold!*\n"
                    f"📦 *Type:* {plan_type} {'(Renewed)' if is_renewal else '(New)'}\n"
                    f"💵 *Amount:* ₹{amount}\n"
                    f"👤 *Client:* {username} ({phone})\n"
                )
                
                # Send WhatsApp (Mock)
                self.send_whatsapp_mock(phone, client_msg, "CLIENT")
                self.send_whatsapp_mock('8356926231', super_admin_msg, "SUPER_ADMIN")
                
                # Send Email (Real SMTP)
                try:
                    send_mail(
                        subject=f"IMS Premium Activated - {plan_type}",
                        message=client_msg.replace('*', ''),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        fail_silently=False # We want to know if it fails
                    )
                    logger.info(f"📧 [EMAIL Sent] to {email}")
                except Exception as mail_err:
                    logger.error(f"📧 [EMAIL Failed]: {mail_err}")

                # 5. Generate JWT Tokens for Auto-Login (Advance Feature)
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
    
                return Response({
                    'message': 'Subscription Activated Successfully!',
                    'display_credentials': {'username': username, 'password': password},
                    'tokens': tokens, # Auto-login tokens
                    'redirect_url': '/dashboard/student/' # Or admin dashboard
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
