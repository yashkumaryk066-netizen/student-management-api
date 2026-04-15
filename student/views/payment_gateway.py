import logging
import razorpay
import hmac
import hashlib
import json
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from student.models import Payment, Student, ClientSubscription
from student.views.finance import approve_subscription_payment

logger = logging.getLogger(__name__)

# Client is initialized inside views to ensure latest settings are used

class RazorpayOrderCreateView(APIView):
    """
    Creates a Razorpay Order
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        amount = request.data.get('amount')
        payment_type = request.data.get('payment_type', 'FEE') # FEE or SUBSCRIPTION
        student_id = request.data.get('student_id')
        plan_type = request.data.get('plan_type')

        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        # Security check: FEE payments must be authenticated
        if payment_type == 'FEE' and not request.user.is_authenticated:
            return Response({"error": "Authentication required for fee payments"}, status=401)

        try:
            amount_paise = int(float(amount) * 100)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount format"}, status=400)

        try:
            # Debug logging (Masked)
            kid = settings.RAZORPAY_KEY_ID
            print(f"DEBUG: Initializing Razorpay with ID: {kid[:6] if kid else 'NONE'}...")

            if not kid or not settings.RAZORPAY_KEY_SECRET:
                return Response({"error": "Razorpay keys are not configured in your .env file or server needs a reload."}, status=500)

            # Initialize Client locally
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))
            
            # Create Razorpay Order with Metadata
            order_params = {
                'amount': amount_paise,
                'currency': 'INR',
                'payment_capture': 1,  # Auto-capture
                'notes': {
                    'plan_type': plan_type,
                    'payment_type': payment_type,
                    'email': request.data.get('email'),
                    'institution_name': request.data.get('institution_name'),
                    'phone': request.data.get('phone')
                }
            }
            razorpay_order = client.order.create(data=order_params)
            
            return Response({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': settings.RAZORPAY_KEY_ID
            })
        except Exception as e:
            logger.error(f"Razorpay Order Creation Failed: {str(e)}")
            return Response({"error": f"Failed to create order: {str(e)}"}, status=500)

class RazorpayQRCodeView(APIView):
    """
    Generates a Razorpay UPI QR Code for a specific amount
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        amount = request.data.get('amount')
        name = request.data.get('name', 'Y.S.M AI ERP')
        description = request.data.get('description', 'Payment to Y.S.M')

        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        try:
            amount_paise = int(float(amount) * 100)
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount format"}, status=400)

        try:
            # Initialize Client locally
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))
            
            # Create Razorpay QR Code
            qr_params = {
                "type": "upi_qr",
                "name": name,
                "usage": "single_payment",
                "fixed_amount": True,
                "payment_amount": amount_paise,
                "description": description,
                "notes": {
                    "payment_type": request.data.get('payment_type', 'FEE'),
                    "student_id": request.data.get('student_id', ''),
                    "email": request.data.get('email', '')
                }
            }
            qr_code = client.qrcode.create(data=qr_params)
            
            return Response({
                'qr_id': qr_code['id'],
                'image_url': qr_code.get('image_url'),
                'upi_id': qr_code.get('upi_id'),
                'amount': amount,
                'success': True
            })
        except Exception as e:
            logger.error(f"Razorpay QR Creation Failed: {str(e)}")
            return Response({"error": f"Could not generate QR: {str(e)}"}, status=500)

class RazorpayVerifyView(APIView):
    """
    Verifies Razorpay Payment Signature and Updates Database
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        # Original request data
        amount = request.data.get('amount')
        payment_type = request.data.get('payment_type', 'FEE')
        student_id = request.data.get('student_id')
        plan_type = request.data.get('plan_type')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response({"error": "Missing signature verification fields"}, status=400)

        try:
            # Initialize Client locally
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))
            
            # Verify Signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)

            # Payment verified, now update DB
            if payment_type == 'SUBSCRIPTION':
                # Handle Registration/Subscription
                email = request.data.get('email')
                institution_name = request.data.get('institution_name')
                phone = request.data.get('phone')
                
                # If guest user (registration), create account
                user = request.user if request.user.is_authenticated else None
                return self._handle_subscription_payment(user, amount, razorpay_payment_id, plan_type, email, institution_name, phone)
            else:
                if not request.user.is_authenticated:
                    return Response({"error": "Authentication required for fee payments"}, status=401)
                return self._handle_fee_payment(request.user, amount, razorpay_payment_id, student_id)

        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed. Invalid signature."}, status=400)
        except Exception as e:
            logger.error(f"Razorpay Verification Error: {str(e)}")
            return Response({"error": "An internal error occurred during verification."}, status=500)

    def _handle_subscription_payment(self, user, amount, transaction_id, plan_type, email=None, institution_name=None, phone=None):
        from django.contrib.auth.models import User
        from django.db import transaction
        
        # 0. Avoid Duplicate Processing (Idempotency)
        if Payment.objects.filter(transaction_id=transaction_id).exists():
            return Response({"success": True, "message": "Already processed", "transaction_id": transaction_id})

        try:
            is_new_user = False
            with transaction.atomic():
                # 1. Registration Flow (No User)
                if not user:
                    if not email:
                        return Response({"error": "Email required for registration"}, status=400)
                    
                    # Try to find user or create
                    user = User.objects.filter(email__iexact=email).first()
                    if not user:
                        # Generate unique username
                        base = (email.split('@')[0] or 'client').lower()
                        username = base
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f"{base}{counter}"
                            counter += 1
                        
                        user = User.objects.create_user(username=username, email=email)
                        user.set_unusable_password()
                        user.save()
                        is_new_user = True

                # 2. Profile Setup
                from student.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=user)
                if not user.is_superuser:
                    profile.role = 'CLIENT'
                if institution_name:
                    profile.institution_name = institution_name
                if phone:
                    profile.phone = phone
                if plan_type:
                    profile.institution_type = plan_type
                profile.save()

                # 3. Create/Update Payment record
                payment = Payment.objects.create(
                    user=user,
                    amount=Decimal(str(amount or 0)),
                    payment_type='SUBSCRIPTION',
                    payment_mode='ONLINE',
                    status='PAID',
                    transaction_id=transaction_id,
                    paid_date=timezone.now().date(),
                    description=f"Razorpay Subscription: {plan_type}",
                    metadata={'plan_type': plan_type, 'email': email, 'phone': phone}
                )

                # 4. Activate Subscription
                approve_subscription_payment(payment)

                # 5. GENERATE CREDENTIALS & SEND EMAIL (PREMIUM ONBOARDING)
                if is_new_user and email:
                    try:
                        import secrets
                        import string
                        from django.core.mail import send_mail
                        from django.template.loader import render_to_string
                        from django.utils.html import strip_tags

                        # Generate Secure Random Password
                        chars = string.ascii_letters + string.digits + "@#$%"
                        new_password = ''.join(secrets.choice(chars) for _ in range(10))
                        user.set_password(new_password)
                        user.save()

                        # Prepare Premium Email
                        subject = f"🚀 Y.S.M Universal AI ERP Activated: {institution_name or 'Institution Profile'}"
                        html_message = f"""
                        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; padding: 40px; color: white; border-radius: 20px;">
                            <div style="text-align: center; margin-bottom: 30px;">
                                <h1 style="color: #6366f1; margin: 0;">Y.S.M UNIVERSAL AI ERP</h1>
                                <p style="color: #94a3b8; font-size: 0.9rem;">The Ultimate AI-Powered Institutional Infrastructure</p>
                            </div>
                            
                            <h2 style="color: white;">Welcome to the Future of Management, {institution_name or 'Partner'}!</h2>
                            <p>Your <strong>{plan_type} ERP Protocol</strong> has been successfully initialized. You now have full access to our enterprise management suite, integrated with the <strong>Y.S.M AI Intelligence Cluster</strong>.</p>
                            
                            <div style="background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin: 30px 0;">
                                <h3 style="color: #6366f1; margin-top: 0;">🔒 Secure ERP Access Credentials</h3>
                                <p style="margin: 5px 0;"><strong>User ID / Username:</strong> <code style="background: #1e293b; padding: 4px 8px; border-radius: 4px;">{user.username}</code></p>
                                <p style="margin: 5px 0;"><strong>Master Password:</strong> <code style="background: #1e293b; padding: 4px 8px; border-radius: 4px;">{new_password}</code></p>
                                <p style="font-size: 0.8rem; color: #94a3b8; margin-top: 10px;">⚠️ For security, please change your password upon first neural login.</p>
                            </div>
                            
                            <div style="text-align: center; margin-top: 40px;">
                                <a href="https://yashamishra.pythonanywhere.com/login/" style="background: #6366f1; color: white; padding: 15px 35px; border-radius: 12px; text-decoration: none; font-weight: 800; display: inline-block;">LOG INTO CENTRAL COMMAND</a>
                            </div>
                            
                            <p style="color: #94a3b8; font-size: 0.8rem; margin-top: 40px; text-align: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                                <strong>System:</strong> Y.S.M Universal AI ERP | <strong>Plan:</strong> {plan_type}<br>
                                Verification Ref: {transaction_id} | Neural Engine Protocol 2026
                            </p>
                        </div>
                        """
                        plain_message = strip_tags(html_message)
                        
                        send_mail(
                            subject,
                            plain_message,
                            settings.EMAIL_HOST_USER,
                            [email],
                            html_message=html_message,
                            fail_silently=True
                        )
                        logger.info(f"Onboarding email sent successfully to {email}")
                    except Exception as email_err:
                        logger.error(f"Failed to send onboarding email: {str(email_err)}")

            return Response({
                "success": True,
                "message": "Subscription activated and credentials dispatched via email",
                "transaction_id": transaction_id
            })
        except Exception as e:
            logger.error(f"Subscription Payment Success Processing Failed: {str(e)}")
            return Response({"error": f"Payment successful but activation failed: {str(e)}"}, status=500)

    def _handle_fee_payment(self, user, amount, transaction_id, student_id):
        try:
            if not student_id:
                # If student is paying for themselves
                if hasattr(user, 'student_profile'):
                    student = user.student_profile
                else:
                    return Response({"error": "Student ID required"}, status=400)
            else:
                student = get_object_or_404(Student, id=student_id)

            # Create Payment Record
            payment = Payment.objects.create(
                student=student,
                amount=Decimal(str(amount)),
                payment_type='FEE',
                payment_mode='RAZORPAY',
                status='PAID',
                transaction_id=transaction_id,
                paid_date=timezone.now().date(),
                description="Razorpay Fee Payment"
            )

            return Response({
                "success": True,
                "message": "Fee payment successful",
                "transaction_id": transaction_id
            })
        except Exception as e:
            logger.error(f"Fee Payment Success Processing Failed: {str(e)}")
            return Response({"error": "Payment was successful but record update failed. Contact support."}, status=500)

class RazorpayWebhookView(APIView):
    """
    Handles Razorpay Webhooks (Server-to-Server notifications)
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = [] # No auth for webhooks

    def post(self, request):
        payload = request.body
        signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')

        # 1. Verify Signature if Secret is provided
        if webhook_secret and signature:
            try:
                expected_signature = hmac.new(
                    webhook_secret.encode(),
                    payload,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(expected_signature, signature):
                    return Response({"error": "Invalid signature"}, status=400)
            except Exception as e:
                logger.error(f"Webhook Signature Verification Failed: {str(e)}")
                return Response({"error": "Verification error"}, status=400)

        # 2. Parse Event
        try:
            data = json.loads(payload)
            event = data.get('event')
            
            if event == 'payment.captured' or event == 'order.paid':
                payment_data = data['payload']['payment']['entity']
                transaction_id = payment_data['id']
                amount = Decimal(str(payment_data['amount'] / 100)) # Convert paise to rupees
                notes = payment_data.get('notes', {})
                
                payment_type = notes.get('payment_type', 'SUBSCRIPTION')
                email = notes.get('email') or payment_data.get('email')
                phone = notes.get('phone') or payment_data.get('contact')
                institution_name = notes.get('institution_name') or notes.get('name')
                plan_type = notes.get('plan_type')

                # Avoid duplicate processing
                if Payment.objects.filter(transaction_id=transaction_id).exists():
                    return Response({"status": "already processed"})

                # Handle based on type
                if payment_type == 'SUBSCRIPTION':
                    view = RazorpayVerifyView()
                    view._handle_subscription_payment(None, amount, transaction_id, plan_type, email, institution_name, phone)
                else:
                    student_id = notes.get('student_id')
                    if student_id:
                        student = Student.objects.filter(id=student_id).first()
                        if student:
                            Payment.objects.create(
                                student=student,
                                amount=amount,
                                payment_type='FEE',
                                payment_mode='RAZORPAY',
                                status='PAID',
                                transaction_id=transaction_id,
                                paid_date=timezone.now().date(),
                                description=f"Razorpay Webhook: {event}"
                            )

            return Response({"status": "success"})
        except Exception as e:
            logger.error(f"Webhook Processing Failed: {str(e)}")
            return Response({"error": str(e)}, status=500)
