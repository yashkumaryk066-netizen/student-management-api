import logging
import razorpay
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
            # Initialize Client locally
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))
            
            # Create Razorpay Order
            order_params = {
                'amount': amount_paise,
                'currency': 'INR',
                'payment_capture': 1  # Auto-capture
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
        
        try:
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

            return Response({
                "success": True,
                "message": "Subscription activated successfully",
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
