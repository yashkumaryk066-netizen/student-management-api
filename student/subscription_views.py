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
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# =========================
# CONSTANTS (Single Source)
# =========================
PLAN_PRICING = {
    'SCHOOL': Decimal('1000.00'),
    'COACHING': Decimal('500.00'),
    'INSTITUTE': Decimal('1500.00')
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
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([permissions.AllowAny])
def verify_payment_api(request):
    try:
        email = request.data.get('email')
        phone = request.data.get('phone')
        plan_type = request.data.get('plan_type')
        utr = request.data.get('utr_number')
        amount = request.data.get('amount')

        if not all([email, plan_type, utr, amount]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if Payment.objects.filter(transaction_id=utr).exists():
            return JsonResponse({"error": "Duplicate UTR"}, status=400)

        amount = Decimal(str(amount))
        expected = PLAN_PRICING.get(plan_type)
        if not expected or amount < expected:
            return JsonResponse({"error": "Invalid amount"}, status=400)

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )

            if created:
                user.set_unusable_password()
                user.save()

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'CLIENT',
                    'institution_type': plan_type,
                    'phone': phone or ''
                }
            )

            payment = Payment.objects.create(
                transaction_id=utr,
                amount=amount,
                due_date=date.today(),
                status=PAYMENT_PENDING,
                description=f"{plan_type} Plan - Bank Transfer",
                metadata={
                    "email": email,
                    "plan_type": plan_type,
                    "user_id": user.id
                }
            )

        logger.info(f"Payment submitted | {email} | {utr}")

        return JsonResponse({
            "status": "SUBMITTED_FOR_VERIFICATION",
            "utr": utr
        })

    except Exception as e:
        logger.exception("Payment submit failed")
        return JsonResponse({"error": "Server error"}, status=500)


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
https://yashamishra.pythonanywhere.com/login/
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
        if not hasattr(request.user, 'subscription'):
            return Response({"status": "NO_SUBSCRIPTION"})

        sub = request.user.subscription
        today = date.today()
        days_left = (sub.end_date - today).days if sub.end_date else 0

        return Response({
            "plan_type": sub.plan_type,
            "status": sub.status,
            "days_left": max(days_left, 0),
            "is_expired": days_left <= 0
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
            "next_step": "/api/subscription/verify-payment/"
        })
