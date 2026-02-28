from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.db import transaction
from .models import ClientSubscription, UserProfile, Payment
from datetime import date, timedelta
import random
import string
import logging
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# =========================
# CONSTANTS (Single Source)
# =========================
PLAN_PRICING = {
    'SCHOOL': Decimal('1500.00'),
    'COACHING': Decimal('500.00'),
    'INSTITUTE': Decimal('3000.00')
}

PAYMENT_PENDING = 'PENDING_VERIFICATION'
PAYMENT_APPROVED = 'APPROVED'
PAYMENT_REJECTED = 'REJECTED'


# =========================
# SUBSCRIPTION PURCHASE
# =========================
class SubscriptionPurchaseView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        plan_type = request.data.get('plan_type')
        email = request.data.get('email')

        if not plan_type or not email:
            return Response(
                {"error": "Plan Type and Email are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        price = PLAN_PRICING.get(plan_type)
        if not price:
            return Response({"error": "Invalid Plan Type"}, status=400)

        return Response({
            "status": "PAYMENT_PENDING",
            "plan_type": plan_type,
            "amount_to_pay": str(price),
            "payment_method": "BANK_TRANSFER",
            "bank_details": {
                "account_name": "Your Institute Name",
                "account_number": "1234567890",
                "ifsc_code": "SBIN0001234",
                "bank_name": "State Bank of India",
                "upi_id": "yourinstitute@sbi"
            },
            "next_step": "/api/subscription/verify-payment/"
        })


# =========================
# VERIFY PAYMENT (UTR)
# =========================
# =========================
# VERIFY PAYMENT (NEW SIGNUP)
# =========================
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def verify_payment_api(request):
    """
    Handle payment verification for NEW signups.
    Accepts multipart/form-data for Logo/Signature uploads.
    """
    try:
        # Support both JSON and Form Data
        email = request.data.get('email')
        phone = request.data.get('phone')
        plan_type = request.data.get('plan_type')
        utr = request.data.get('utr_number')
        amount = request.data.get('amount')
        
        # Branding Fields
        inst_name = request.data.get('institution_name')
        inst_logo = request.FILES.get('institution_logo')
        dig_sig = request.FILES.get('digital_signature')

        if not all([email, plan_type, utr, amount]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if Payment.objects.filter(transaction_id=utr).exists():
            return JsonResponse({"error": "Duplicate UTR/Transaction ID"}, status=400)

        amount = Decimal(str(amount))
        
        # Verify amount matches plan
        expected = PLAN_PRICING.get(plan_type)
        if not expected or amount < expected:
            return JsonResponse({"error": f"Invalid amount. {plan_type} requires {expected}"}, status=400)

        with transaction.atomic():
            # Check if user exists
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )

            if created:
                user.set_unusable_password()
                user.save()
            
            # Ensure profile exists or update it
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'CLIENT',
                    'institution_type': plan_type,
                }
            )
            
            # Update Profile Data
            profile.phone = phone or profile.phone
            if inst_name:
                profile.institution_name = inst_name
            if inst_logo:
                profile.institution_logo = inst_logo
            if dig_sig:
                profile.digital_signature = dig_sig
            
            profile.save()

            payment = Payment.objects.create(
                user=user, # Link the payment to the user!
                transaction_id=utr,
                amount=amount,
                due_date=date.today(),
                status=PAYMENT_PENDING,
                description=f"{plan_type} Plan - Signup Payment",
                payment_mode='BANK_TRANSFER',
                metadata={
                    "email": email,
                    "plan_type": plan_type,
                    "user_id": user.id,
                    "type": "NEW_SIGNUP"
                }
            )

        logger.info(f"Signup Payment submitted | {email} | {utr}")

        return JsonResponse({
            "status": "SUBMITTED_FOR_VERIFICATION",
            "utr": utr,
            "message": "Payment submitted. Admin will verify and activate your account."
        })

    except Exception as e:
        logger.exception("Payment submit failed")
        return JsonResponse({"error": str(e)}, status=500)


# =========================
# RENEWAL PAYMENT SUBMISSION (AUTHENTICATED)
# =========================
class RenewalSubmissionView(APIView):
    """
    Handle payment submission for EXISTING users (Renewals).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            utr = request.data.get('utr_number')
            amount = request.data.get('amount')
            plan_type = request.data.get('plan_type')

            if not all([utr, amount, plan_type]):
                return Response({"error": "Missing UTR, Amount or Plan Type"}, status=400)

            if Payment.objects.filter(transaction_id=utr).exists():
                return Response({"error": "Duplicate UTR/Transaction ID"}, status=400)

            amount = Decimal(str(amount))
            expected = PLAN_PRICING.get(plan_type)
            if not expected or amount < expected:
                 return Response({"error": f"Invalid amount for {plan_type} plan"}, status=400)

            # Create Payment record linked to current user
            Payment.objects.create(
                user=request.user,
                transaction_id=utr,
                amount=amount,
                due_date=date.today(),
                status=PAYMENT_PENDING,
                payment_type='SUBSCRIPTION',
                payment_mode='UPI', # Assuming UPI/Bank Transfer
                description=f"{plan_type} Plan Renewal",
                metadata={
                    "email": request.user.email,
                    "plan_type": plan_type,
                    "user_id": request.user.id,
                    "type": "RENEWAL"
                }
            )
            
            return Response({
                "status": "SUBMITTED", 
                "message": "Renewal request submitted. Access will be extended upon approval."
            })

        except Exception as e:
            logger.exception("Renewal submission failed")
            return Response({"error": "Submission failed"}, status=500)


# =========================
# ADMIN APPROVAL
# =========================
class AdminPaymentApprovalView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)

        payment_id = request.data.get('payment_id')
        action = request.data.get('action')

        if not payment_id or action not in ['approve', 'reject']:
            return Response({"error": "Invalid request"}, status=400)

        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(
                    id=payment_id,
                    status=PAYMENT_PENDING
                )

                metadata = payment.metadata or {}
                user = User.objects.get(id=metadata.get('user_id'))
                plan_type = metadata.get('plan_type')

                if action == 'approve':
                    password = None
                    if not user.has_usable_password():
                        password = ''.join(
                            random.choices(string.ascii_letters + string.digits, k=12)
                        )
                        user.set_password(password)
                        user.is_active = True
                        user.save()

                    profile = user.profile
                    profile.subscription_expiry = date.today() + timedelta(days=30)
                    profile.role = 'ADMIN'
                    profile.institution_type = plan_type
                    profile.save()

                    sub, _ = ClientSubscription.objects.get_or_create(user=user)
                    sub.plan_type = plan_type
                    sub.amount_paid = payment.amount
                    sub.activate(days=30)

                    payment.status = PAYMENT_APPROVED
                    payment.save()

                    # Email (credentials only first time)
                    try:
                        msg = f"""
Your {plan_type} subscription is active.

Login URL:
/login/
Username: {user.username}
"""
                        if password:
                            msg += f"Password: {password}\n"

                        send_mail(
                            "Subscription Active",
                            msg,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            fail_silently=True
                        )
                    except:
                        pass

                    return Response({"status": "APPROVED"})

                payment.status = PAYMENT_REJECTED
                payment.save()
                return Response({"status": "REJECTED"})

        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        except Exception as e:
            logger.exception("Approval failed")
            return Response({"error": "Server error"}, status=500)


# =========================
# PENDING PAYMENTS LIST
# =========================
class PendingPaymentsListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        payments = Payment.objects.filter(status=PAYMENT_PENDING).order_by('-created_at')
        data = []

        for p in payments:
            meta = p.metadata or {}
            data.append({
                "id": p.id,
                "utr": p.transaction_id,
                "amount": str(p.amount),
                "email": meta.get('email'),
                "plan": meta.get('plan_type'),
                "date": p.due_date
            })

        return Response({"total": len(data), "payments": data})


# =========================
# SUBSCRIPTION STATUS
# =========================
class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Use the correct reverse relationship
            sub = ClientSubscription.objects.get(user=request.user)
        except ClientSubscription.DoesNotExist:
            return Response({"status": "NO_SUBSCRIPTION"})

        today = date.today()
        days_left = (sub.end_date - today).days if sub.end_date else 0

        return Response({
            "plan_type": sub.plan_type,
            "status": sub.status,
            "days_left": max(days_left, 0),
            "is_expired": days_left <= 0,
            "start_date": sub.start_date.strftime('%Y-%m-%d') if sub.start_date else None,
            "end_date": sub.end_date.strftime('%Y-%m-%d') if sub.end_date else None
        })


# =========================
# SUBSCRIPTION RENEW
# =========================
class SubscriptionRenewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'subscription'):
            return Response({"error": "No subscription"}, status=404)

        sub = request.user.subscription
        plan_type = request.data.get('plan_type', sub.plan_type)
        price = PLAN_PRICING.get(plan_type)

        return Response({
            "status": "RENEWAL_PAYMENT_PENDING",
            "plan_type": plan_type,
            "amount_to_pay": str(price),
            "next_step": "/api/subscription/submit-renewal/"
        })


# =========================
# MANUAL PAYMENT & RENEWAL SUBMISSION
# =========================
class ManualPaymentSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        txn_id = request.data.get('transaction_id')
        p_type = request.data.get('payment_type', 'SUBSCRIPTION')
        desc = request.data.get('description', 'Manual Payment')
        
        if not amount or not txn_id:
            return Response({"error": "Start Amount and Transaction ID are required"}, status=400)

        try:
            Payment.objects.create(
                user=request.user,
                transaction_id=txn_id,
                amount=amount,
                payment_type=p_type,
                status=PAYMENT_PENDING,
                description=desc,
                metadata={
                    "user_id": request.user.id,
                    "email": request.user.email,
                    "plan_type": "RENEWAL" if p_type == 'SUBSCRIPTION' else 'MANUAL'
                }
            )
            return Response({"status": "SUBMITTED", "message": "Payment submitted for approval"})
        except Exception as e:
            logger.error(f"Payment Submit Error: {e}")
            return Response({"error": "Submission Failed"}, status=500)

# Aliases for URL compatibility
RenewalSubmissionView = ManualPaymentSubmitView
ClientSubscriptionView = SubscriptionStatusView
SubscriptionRenewalView = SubscriptionRenewView
