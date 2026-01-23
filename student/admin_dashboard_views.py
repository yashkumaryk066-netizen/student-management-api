from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

from .models import ClientSubscription, UserProfile, Payment, Notification
from .services.invoice_service import generate_invoice_pdf
from .services.email_service import send_credentials_with_invoice
from .services.telegram_service import send_telegram_notification
from .plan_permissions import PLAN_FEATURES, FEATURE_META
import os

from datetime import date, timedelta
from decimal import Decimal
import random, string, logging

logger = logging.getLogger(__name__)

# =========================
# CONSTANTS (ADVANCE)
# =========================
PAYMENT_PENDING = 'PENDING_VERIFICATION'
PAYMENT_APPROVED = 'APPROVED'
PAYMENT_REJECTED = 'REJECTED'

SUB_ACTIVE = 'ACTIVE'
SUB_SUSPENDED = 'SUSPENDED'


# =========================
# UTIL
# =========================
def generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


# =========================
# PUBLIC PAYMENT SUBMIT
# =========================
class PublicSubscriptionSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        plan_type = request.data.get('plan_type')
        amount = request.data.get('amount')
        utr = request.data.get('utr')

        # Map frontend names to backend enums
        PLAN_MAP = {
            'Coaching Center': 'COACHING',
            'School': 'SCHOOL',
            'Institute': 'INSTITUTE'
        }
        plan_type = PLAN_MAP.get(plan_type, 'SCHOOL')

        if not all([email, plan_type, amount, utr]):
            return Response(
                {'error': 'email, plan_type, amount, utr are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Payment.objects.filter(transaction_id=utr).exists():
            return Response(
                {'error': 'Duplicate UTR detected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        Payment.objects.create(
            amount=Decimal(str(amount)),
            transaction_id=utr,
            status=PAYMENT_PENDING,
            payment_type='SUBSCRIPTION',
            due_date=date.today(),
            description=f"Subscription: {plan_type}",
            metadata={
                'email': email,
                'plan_type': plan_type
            }
        )

        logger.info(f"New payment submitted | {email} | {utr}")

        return Response(
            {'message': 'Payment submitted. Admin will verify.'},
            status=status.HTTP_201_CREATED
        )


# =========================
# ADMIN – PENDING PAYMENTS
# =========================
class PendingPaymentsListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        payments = Payment.objects.filter(
            status=PAYMENT_PENDING
        ).order_by('-created_at')

        data = []
        for p in payments:
            email = (
                p.user.email if p.user else
                (p.metadata or {}).get('email', 'Unknown')
            )

            data.append({
                'id': p.id,
                'email': email,
                'amount': str(p.amount),
                'utr': p.transaction_id,
                'plan': (p.metadata or {}).get('plan_type'),
                'date': p.created_at
            })

        return Response(data, status=status.HTTP_200_OK)


# =========================
# ADMIN – APPROVE / REJECT
# =========================
class AdminPaymentApprovalView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        action = request.data.get('action')
        notes = request.data.get('notes', '')

        if not payment_id or action not in ['approve', 'reject']:
            return Response({'error': 'Invalid request'}, status=400)

        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(id=payment_id)

                email = (
                    (payment.metadata or {}).get('email') or
                    (payment.user.email if payment.user else None)
                )

                if not email:
                    return Response({'error': 'Email not found'}, status=400)

                if action == 'approve':
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': self._generate_username(email)
                        }
                    )

                    password = None
                    if created:
                        password = generate_password()
                        user.set_password(password)
                        user.is_active = True
                        user.save()

                    sub, _ = ClientSubscription.objects.get_or_create(user=user)
                    sub.plan_type = (payment.metadata or {}).get('plan_type', 'SCHOOL')
                    sub.transaction_id = payment.transaction_id
                    sub.amount_paid = payment.amount
                    sub.activate(days=30)

                    UserProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            'role': 'CLIENT',
                            'institution_type': sub.plan_type,
                            'subscription_expiry': sub.end_date
                        }
                    )

                    payment.status = PAYMENT_APPROVED
                    payment.user = user
                    payment.save()

                    
                    # Generate Invoice & Send Email
                    try:
                        invoice_pdf = generate_invoice_pdf(user, sub, payment)
                        send_credentials_with_invoice(user, password, sub.plan_type, invoice_pdf)
                        
                        # --- TELEGRAM NOTIFICATION ---
                        # Use the chat_id provided by the super admin (you)
                        # In a real SaaS, you might ask users for their own Telegram ID, 
                        # but here we are notifying YOU (the Super Admin) of the new approval 
                        # OR if this chat_id is the User's, we send it to them.
                        # Based on request, "Telegram notification on ke liye...", this seems to be for the Admin to see/forward, 
                        # or if we had the user's ID. For now, sending to the configured ID (yours).
                        
                        tg_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '5280398471')
                        
                        # Get features for this plan
                        plan_features = PLAN_FEATURES.get(sub.plan_type, [])
                        feature_icons = " ".join([FEATURE_META[f]['icon'] for f in plan_features if f in FEATURE_META][:8])

                        # Determine Title and Creds based on New/Renew
                        if created:
                            title_text = f"✅ *New Account Approved for {sub.plan_type}*"
                            creds_text = (
                                f"🔐 *Login Credentials:*\n"
                                f"🆔 ID: `{user.username}`\n"
                                f"🔑 Pass: `{password}`"
                            )
                        else:
                            title_text = f"🔄 *Account Renewed for {sub.plan_type}*"
                            creds_text = (
                                f"🔐 *Login Credentials:*\n"
                                f"🆔 ID: `{user.username}`\n"
                                f"🔑 Pass: _(Existing Password Valid)_"
                            )

                        tg_message = (
                            f"{title_text}!\n\n"
                            f"👤 *Client Name:* {user.first_name or user.username}\n"
                            f"📧 *Email:* `{email}`\n"
                            f"💰 *Amount Paid:* ₹{payment.amount}\n"
                            f"📅 *Valid Until:* {sub.end_date}\n\n"
                            f"🔓 *Unlocked Features:*\n"
                            f"{feature_icons} (+ more)\n\n"
                            f"{creds_text}\n\n"
                            f"🚀 _Automatic Notification from Y.S.M ERP_"
                        )
                        
                        send_telegram_notification(tg_chat_id, tg_message, invoice_pdf, invoice_filename=f"Invoice_{user.username}.pdf")

                    except Exception as e:
                        logger.error(f"Error sending notifications: {e}")


                    return Response({'message': 'Payment approved'}, status=200)

                # REJECT
                payment.status = PAYMENT_REJECTED
                payment.save()

                if email:
                    try:
                        send_mail(
                            "Subscription Rejected",
                            f"Reason: {notes}",
                            settings.DEFAULT_FROM_EMAIL,
                            [email],
                            fail_silently=True
                        )
                    except:
                        pass

                return Response({'message': 'Payment rejected'}, status=200)

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)
        except Exception as e:
            logger.exception("Approval error")
            return Response({'error': 'Server error'}, status=500)

    def _generate_username(self, email):
        base = email.split('@')[0]
        username = base
        while User.objects.filter(username=username).exists():
            username = f"{base}{random.randint(1000,9999)}"
        return username



# =========================
# SUPER ADMIN DASHBOARD
# =========================
class SuperAdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Access denied'}, status=403)

        today = date.today()

        total_clients = User.objects.filter(is_superuser=False).count()
        active_subs = ClientSubscription.objects.filter(status=SUB_ACTIVE).count()
        pending = Payment.objects.filter(status=PAYMENT_PENDING).count()

        total_revenue = Payment.objects.filter(
            status=PAYMENT_APPROVED
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        subs_data = []
        for sub in ClientSubscription.objects.select_related('user'):
            if sub.user.is_superuser:
                continue

            days_left = (sub.end_date - today).days if sub.end_date else 0

            subs_data.append({
                'id': sub.user.id,
                'username': sub.user.username,
                'email': sub.user.email,
                'plan_type': sub.plan_type,
                'status': sub.status,
                'days_left': max(days_left, 0),
                'amount_paid': str(sub.amount_paid)
            })

        # Fetch Pending Payments Details
        pending_payments_list = []
        for p in Payment.objects.filter(status=PAYMENT_PENDING).order_by('-created_at'):
            pending_payments_list.append({
                'id': p.id,
                'email': (p.metadata or {}).get('email') or (p.user.email if p.user else 'Unknown'),
                'plan_type': (p.metadata or {}).get('plan_type', 'N/A'),
                'amount': str(p.amount),
                'utr': p.transaction_id,
                'date': p.created_at.strftime('%Y-%m-%d')
            })

        return Response({
            'stats': {
                'total_clients': total_clients,
                'active_subscriptions': active_subs,
                'pending_approvals': pending,
                'total_revenue': str(total_revenue)
            },
            'pending_payments': pending_payments_list,
            'client_subscriptions': subs_data
        })


# =========================
# SUPER ADMIN CLIENT ACTION
# =========================
class SuperAdminClientActionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        client_id = request.data.get('client_id')
        action = request.data.get('action')

        try:
            with transaction.atomic():
                sub = ClientSubscription.objects.select_for_update().get(user_id=client_id)
                profile = UserProfile.objects.get(user_id=client_id)

                if action == 'SUSPEND':
                    sub.status = SUB_SUSPENDED

                elif action == 'ACTIVATE':
                    sub.status = SUB_ACTIVE

                elif action == 'REDUCE_DAYS' and sub.end_date:
                    sub.end_date -= timedelta(days=7)

                elif action == 'EXTEND_DAYS':
                    sub.end_date = (sub.end_date or date.today()) + timedelta(days=30)

                elif action == 'DELETE':
                    sub.user.delete()
                    return Response({'message': 'Client deleted'})

                else:
                    return Response({'error': 'Invalid action'}, status=400)

                sub.save()
                profile.subscription_expiry = sub.end_date
                profile.save()

                return Response({'message': f'Action {action} completed'})

        except ClientSubscription.DoesNotExist:
            return Response({'error': 'Subscription not found'}, status=404)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)
        except Exception as e:
            logger.exception("Client action error")
            return Response({'error': 'Server error'}, status=500)
