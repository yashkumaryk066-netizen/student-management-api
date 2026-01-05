from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import random, string, logging

from .models import UserProfile, Notification
from .services.invoice_service import generate_invoice_pdf
from .services.email_service import send_credentials_with_invoice

logger = logging.getLogger(__name__)

# =========================
# CONSTANTS (SINGLE SOURCE)
# =========================
PLAN_PRICING = {
    'COACHING': Decimal('500.00'),
    'SCHOOL': Decimal('10000.00'),
    'INSTITUTE': Decimal('15000.00'),
}

SUBSCRIPTION_DAYS = 30


# =========================
# ONBOARDING + RENEWAL
# =========================
class OnboardingPaymentView(APIView):
    """
    New Purchase + Renewal (Same Flow)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        phone = request.data.get('phone')
        email = request.data.get('email')
        plan_type = (request.data.get('plan_type') or '').upper()
        amount = request.data.get('amount')

        if not all([phone, email, plan_type, amount]):
            return Response({"error": "Missing required fields"}, status=400)

        expected_amount = PLAN_PRICING.get(plan_type)
        if not expected_amount:
            return Response({"error": "Invalid plan type"}, status=400)

        try:
            amount = Decimal(str(amount))
        except:
            return Response({"error": "Invalid amount"}, status=400)

        if amount < expected_amount:
            return Response({
                "error": f"Payment mismatch. Expected ₹{expected_amount}"
            }, status=400)

        # =========================
        # USER LOOKUP (SAFE)
        # =========================
        user = User.objects.filter(email=email).first()
        is_renewal = bool(user)

        try:
            with transaction.atomic():
                password = None

                # =========================
                # NEW USER
                # =========================
                if not user:
                    password = ''.join(
                        random.SystemRandom().choices(
                            string.ascii_letters + string.digits, k=10
                        )
                    )

                    base_username = email.split('@')[0]
                    username = base_username
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{random.randint(100,999)}"

                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_active=True
                    )

                    profile = UserProfile.objects.create(
                        user=user,
                        role='ADMIN',
                        phone=phone,
                        institution_type=plan_type,
                        subscription_expiry=timezone.now().date() +
                        timezone.timedelta(days=SUBSCRIPTION_DAYS)
                    )

                # =========================
                # RENEWAL
                # =========================
                else:
                    profile = user.profile
                    today = timezone.now().date()

                    if profile.subscription_expiry and profile.subscription_expiry > today:
                        profile.subscription_expiry += timezone.timedelta(days=SUBSCRIPTION_DAYS)
                    else:
                        profile.subscription_expiry = today + timezone.timedelta(days=SUBSCRIPTION_DAYS)

                    profile.institution_type = plan_type
                    profile.phone = phone
                    profile.save()

                # =========================
                # NOTIFICATIONS
                # =========================
                Notification.objects.create(
                    recipient=user,
                    recipient_type='ADMIN',
                    title='Subscription Renewed' if is_renewal else 'Subscription Activated',
                    message=f'{plan_type} plan valid till {profile.subscription_expiry}'
                )

                # =========================
                # INVOICE
                # =========================
                invoice_pdf = generate_invoice_pdf(
                    user=user,
                    plan_type=plan_type,
                    amount=amount,
                    expiry_date=profile.subscription_expiry,
                    is_renewal=is_renewal
                )

                # =========================
                # EMAIL (NO PASSWORD RESET)
                # =========================
                send_credentials_with_invoice(
                    user=user,
                    password=password,   # None on renewal
                    plan_type=plan_type,
                    invoice_pdf=invoice_pdf,
                    is_renewal=is_renewal
                )

                return Response({
                    "message": "Subscription renewed successfully"
                    if is_renewal else "Subscription activated successfully",
                    "username": user.username,
                    "password": password,  # None on renewal
                    "expiry_date": profile.subscription_expiry
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Onboarding / Renewal failed")
            return Response({"error": "Server error"}, status=500)
