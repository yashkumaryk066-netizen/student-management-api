from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from student.conf import CURRENCY_SYMBOL
from django.db import models, transaction
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

from .models import ClientSubscription, UserProfile, Payment, Notification, Student
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        try:
            email = request.data.get('email')
            plan_type_raw = request.data.get('plan_type')
            amount_raw = request.data.get('amount', '0')
            utr = request.data.get('utr')
            
            # Map frontend names to backend enums
            PLAN_MAP = {
                'Coaching Center': 'COACHING',
                'School': 'SCHOOL',
                'Institute': 'INSTITUTE',
                'COACHING': 'COACHING',
                'SCHOOL': 'SCHOOL',
                'INSTITUTE': 'INSTITUTE'
            }
            
            plan_type = PLAN_MAP.get(plan_type_raw, 'COACHING')
            try:
                amount = Decimal(str(amount_raw))
            except:
                amount = Decimal('0')

            # Branding Fields
            inst_name = request.data.get('institution_name')
            inst_logo = request.FILES.get('institution_logo')
            dig_sig = request.FILES.get('digital_signature')

            # Basic Check
            if Payment.objects.filter(transaction_id=utr).exists():
                return Response({"error": "Duplicate UTR/Transaction ID. Request already logged."}, status=400)

            with transaction.atomic():
                # 1. Identity Linkage
                username = email.split('@')[0]
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={'username': username}
                )
                if created:
                    user.set_unusable_password()
                    user.save()

                # 2. Profile Archetype
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': 'CLIENT', 'institution_type': plan_type}
                )
                
                # Save Branding & Identity Signatures
                if inst_name: profile.institution_name = inst_name
                if inst_logo: profile.institution_logo = inst_logo
                if dig_sig:  profile.digital_signature = dig_sig
                profile.institution_type = plan_type
                profile.save()

                # 3. Financial Record (Verification Pending)
                payment = Payment.objects.create(
                    user=user,
                    amount=amount,
                    transaction_id=utr,
                    payment_mode='BANK_TRANSFER',
                    status='PENDING_VERIFICATION',
                    description=f"Initial Subscription Request: {plan_type}",
                    due_date=date.today(),
                    metadata={
                        "email": email,
                        "plan_type": plan_type,
                        "plan_raw": plan_type_raw,
                        "institution_name": inst_name or email.split('@')[0].title(),
                        "submit_time": str(timezone.now())
                    }
                )

                # 4. Subscription Node (Dormant)
                ClientSubscription.objects.update_or_create(
                    user=user,
                    defaults={
                        "plan_type": plan_type,
                        "status": 'PENDING',
                        "transaction_id": utr
                    }
                )

            return Response({"message": "Sovereign request logged. Node activation pending root verification."}, status=201)

        except Exception as e:
            logger.exception("Subscription Submission Failure")
            return Response({"error": f"Critical Error: {str(e)}"}, status=500)


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
            # Fallback Logic for Robustness
            metadata = p.metadata or {}
            user = p.user
            
            # Determine best display name for Institute/User
            inst_name = metadata.get('institution_name')
            if not inst_name and user:
                # Try fetching from profile
                try:
                    profile = user.userprofile
                    inst_name = profile.institution_name or user.username.title()
                except:
                    inst_name = user.username.title()
            
            if not inst_name:
                inst_name = "Unknown Client"

            # Determine Plan
            plan_type = metadata.get('plan_type')
            if not plan_type and user:
                 try:
                    plan_type = user.userprofile.institution_type
                 except:
                    pass
            
            email = metadata.get('email') or (user.email if user else 'No Email')

            data.append({
                'id': p.id,
                'email': email,
                'user_email': email, # Frontend might look for this
                'amount': str(p.amount),
                'transaction_id': p.transaction_id or 'N/A',
                'plan_type': plan_type or 'STANDARD',
                'institution_name': inst_name,
                'date': p.created_at.strftime("%Y-%m-%d %H:%M"),
                'status': p.status,
                'raw_metadata': metadata # Pass full metadata just in case
            })

        return Response(data, status=status.HTTP_200_OK)


# =========================
# ADMIN – APPROVE / REJECT
# =========================
class AdminPaymentApprovalView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        # SECURITY: Strictly only SuperAdmin can approve/reject
        if not request.user.is_superuser:
            return Response({'error': 'Unauthorized. SuperAdmin access required.'}, status=403)

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

                    # Log approval details
                    logger.info(f"Payment approved: User={user.username} (ID={user.id}), Plan={sub.plan_type}, Created={created}")
                    logger.debug(f"Email={email}, Amount={payment.amount}, Transaction={payment.transaction_id}")

                    # Generate Invoice & Send Email
                    try:
                        invoice_pdf = generate_invoice_pdf(user, sub, payment)
                        logger.debug(f"Invoice PDF generated successfully")
                        
                        # Professional Email Service
                        from .email_service import send_approval_email
                        
                        if password:  # New account - send credentials
                            email_sent = send_approval_email(
                                email=email,
                                username=user.username,
                                password=password,
                                plan_type=sub.plan_type,
                                institution_type=sub.plan_type,
                                amount=str(payment.amount),
                                payment_id=payment.transaction_id or f"PAY-{payment.id}"
                            )
                            
                            if email_sent:
                                logger.info(f"✅ Professional email with credentials sent to {email}")
                            else:
                                logger.warning(f"⚠️ Email sending failed to {email}")
                        else:
                            logger.info(f"ℹ️ Renewal for existing user {user.username}")
                        
                        # --- TELEGRAM NOTIFICATION ---
                        tg_chat_id = os.environ.get('TELEGRAM_CHAT_ID', '5280398471')
                        
                        from .plan_permissions import DEFAULT_PLAN_BY_INSTITUTION, get_feature_meta
                        
                        # Resolve effective plan (e.g. SCHOOL -> PRO)
                        effective_plan = DEFAULT_PLAN_BY_INSTITUTION.get(sub.plan_type, 'BASIC')
                        plan_features = PLAN_FEATURES.get(effective_plan, [])
                        feature_icons = " ".join([get_feature_meta(f)['icon'] for f in plan_features][:8])

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
                            f"💰 *Amount Paid:* {CURRENCY_SYMBOL}{payment.amount}\n"
                            f"📅 *Valid Until:* {sub.end_date}\n\n"
                            f"🔓 *Unlocked Features:*\n"
                            f"{feature_icons} (+ more)\n\n"
                            f"{creds_text}\n\n"
                            f"🚀 _Automatic Notification from Y.S.M ERP_"
                        )
                        
                        send_telegram_notification(tg_chat_id, tg_message, invoice_pdf, invoice_filename=f"Invoice_{user.username}.pdf")
                        logger.info(f"Telegram notification sent for {user.username}")

                    except Exception as e:
                        logger.error(f"Notification error for {email}: {str(e)}")

                    return Response({'message': 'Payment approved'}, status=200)

                # REJECT
                payment.status = PAYMENT_REJECTED
                payment.save()

                if email:
                    try:
                        from .email_service import send_rejection_email
                        
                        metadata = payment.metadata or {}
                        # Generate "VOID" Invoice for Rejection
                        try:
                            # Create a temporary user object if user doesn't exist yet, just for the invoice
                            temp_user = payment.user
                            if not temp_user:
                                from django.contrib.auth.models import User
                                temp_user = User(username="Prospect", email=email, first_name=metadata.get('institution_name', 'Client'))
                            
                            # Create dummy subscription object for invoice context
                            from .models import ClientSubscription
                            temp_sub = ClientSubscription(plan_type=metadata.get('plan_type', 'N/A'), transaction_id=payment.transaction_id)
                            
                            invoice_pdf = generate_invoice_pdf(temp_user, temp_sub, payment)
                        except Exception as e:
                            logger.error(f"Failed to generate rejection invoice: {e}")
                            invoice_pdf = None

                        email_sent = send_rejection_email(
                            email=email,
                            plan_type=metadata.get('plan_type', 'N/A'),
                            amount=str(payment.amount),
                            payment_id=payment.transaction_id or f"PAY-{payment.id}",
                            reason=notes or "Payment verification failed",
                            invoice_pdf=invoice_pdf
                        )
                        
                        if email_sent:
                            logger.info(f"✅ Professional rejection email sent to {email}")
                        else:
                            logger.warning(f"⚠️ Rejection email failed for {email}")
                    except Exception as e:
                        logger.error(f"Rejection email error: {str(e)}")

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

        # Get real counts
        total_clients = User.objects.filter(is_superuser=False, is_staff=False).count()
        active_institutes = ClientSubscription.objects.filter(status=SUB_ACTIVE).count()
        
        # Count total students across all clients
        total_students = Student.objects.count()
        
        # Total approved revenue
        total_revenue = Payment.objects.filter(
            status=PAYMENT_APPROVED
        ).aggregate(total=models.Sum('amount'))['total'] or 0

        # Pending approvals count
        pending_count = Payment.objects.filter(status=PAYMENT_PENDING).count()

        # --- CHART DATA (Last 6 Months) ---
        six_months_ago = today - timedelta(days=180)
        # 1. Registration Trends
        reg_trends = ClientSubscription.objects.filter(created_at__gte=six_months_ago)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(count=Count('id'))\
            .order_by('month')
        
        # 2. Revenue Trends
        rev_trends = Payment.objects.filter(status=PAYMENT_APPROVED, created_at__gte=six_months_ago)\
            .annotate(month=TruncMonth('created_at'))\
            .values('month')\
            .annotate(total=Sum('amount'))\
            .order_by('month')

        chart_data = {
            'months': [item['month'].strftime('%b %Y') for item in reg_trends],
            'registrations': [item['count'] for item in reg_trends],
            'revenue': [float(item['total']) for item in rev_trends]
        }

        # Format approvals list for frontend
        approvals_list = []
        for p in Payment.objects.filter(status=PAYMENT_PENDING).order_by('-created_at')[:20]:
            metadata = p.metadata or {}
            email = metadata.get('email') or (p.user.email if p.user else 'Unknown')
            
            # Calculate time ago
            time_diff = timezone.now() - p.created_at
            if time_diff.days > 0:
                time_ago = f"{time_diff.days}d ago"
            elif time_diff.seconds >= 3600:
                time_ago = f"{time_diff.seconds // 3600}h ago"
            else:
                time_ago = f"{time_diff.seconds // 60}m ago"
            
            approvals_list.append({
                'id': p.id,
                'type': 'SUBSCRIPTION',
                'icon': '🏛️',
                'entity_name': metadata.get('institution_name', email.split('@')[0].title()),
                'sub_text': f"{metadata.get('plan_type', 'N/A')} Plan",
                'amount': str(p.amount),
                'transaction_id': p.transaction_id or 'N/A',
                'time_ago': time_ago,
                'email': email,
                'plan_type': metadata.get('plan_type', 'BASIC'),
                'institution_type': metadata.get('institution_type', 'SCHOOL')
            })

        # Format institutes list
        institutes_list = []
        for sub in ClientSubscription.objects.select_related('user').filter(
            user__is_superuser=False
        ).order_by('-created_at')[:50]:
            
            days_left = (sub.end_date - today).days if sub.end_date else 0
            
            institutes_list.append({
                'id': sub.user.id,
                'name': sub.user.username.replace('_', ' ').title(),
                'email': sub.user.email,
                'type': sub.plan_type, # Plan type IS the institution type essentially, or fetch from profile if needed
                'plan': sub.plan_type,
                'status': 'ACTIVE' if sub.status == SUB_ACTIVE else 'INACTIVE',
                'joined': sub.created_at.strftime('%Y-%m-%d'),
                'days_left': max(days_left, 0),
                'amount': str(sub.amount_paid)
            })

        # System health check
        db_status = 'HEALTHY'
        try:
            from django.db import connection
            connection.ensure_connection()
        except:
            db_status = 'ERROR'

        return Response({
            'stats': {
                'active_institutes': active_institutes,
                'students': total_students,
                'revenue': float(total_revenue),
                'pending': pending_count,
                'total_clients': total_clients
            },
            'charts': chart_data,
            'approvals': approvals_list,
            'institutes': institutes_list,
            'health': {
                'db_status': db_status,
                'storage_usage': '45%',
                'latency': '24ms'
            }
        })


# =========================
# SUPER ADMIN CLIENT ACTION
# =========================
# =========================
# SUPER ADMIN CLIENT ACTION
# =========================
class SuperAdminClientActionView(APIView):
    """
    Handle Specific Actions on Clients (Suspend, Activate, Extend, Delete)
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Unauthorized"}, status=403)

        client_id = request.data.get('client_id')
        action = request.data.get('action')
        
        if not client_id or not action:
            return Response({"error": "Missing client_id or action"}, status=400)

        try:
            with transaction.atomic():
                # Fetch User and Related Objects
                # Using select_related is good but let's be safe if relation missing
                # We need the user mainly.
                user = get_object_or_404(User, id=client_id)
                
                # Fetch or Create Subscription/Profile if missing (Edge case safety)
                # But typically they should exist.
                sub, _ = ClientSubscription.objects.get_or_create(user=user)
                profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'CLIENT'})

                msg = ""

                if action == 'SUSPEND':
                    sub.status = 'SUSPENDED'
                    profile.is_active = False # Optional: Blocks login entirely
                    msg = f"Client {user.username} suspended successfully."

                elif action == 'ACTIVATE':
                    sub.status = 'ACTIVE'
                    profile.is_active = True
                    # If expired, maybe extend? For now just activate status.
                    if sub.end_date and sub.end_date < date.today():
                         sub.end_date = date.today() + timedelta(days=30) # Auto refresh if activating expired
                    msg = f"Client {user.username} activated."

                elif action == 'REDUCE_DAYS':
                    if sub.end_date:
                        sub.end_date -= timedelta(days=7)
                        msg = "Plan duration reduced by 7 days."
                    else:
                        msg = "No active plan to reduce."

                elif action == 'EXTEND_DAYS':
                    base_date = sub.end_date if sub.end_date and sub.end_date >= date.today() else date.today()
                    sub.end_date = base_date + timedelta(days=30)
                    sub.status = 'ACTIVE' # Ensure active if extended
                    msg = f"Plan extended by 30 days. New expiry: {sub.end_date}"

                elif action == 'DELETE':
                    # Permanent Delete
                    # User.delete() cascades to Profile, Subscription, etc.
                    username = user.username
                    user.delete()
                    return Response({'message': f'Client {username} and all data deleted permanently.'})

                else:
                    return Response({'error': 'Invalid action type'}, status=400)

                # Save updates
                sub.save()
                
                # Sync Profile Expiry
                profile.subscription_expiry = sub.end_date
                profile.save()
                
                # Also save User if is_active changed
                user.save()

                return Response({'message': msg, 'new_status': sub.status, 'new_expiry': sub.end_date})

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            logger.exception("Client Action Failed")
            return Response({'error': f'Server Error: {str(e)}'}, status=500)


# =========================
# GLOBAL COMMAND SEARCH
# =========================
class GlobalSearchView(APIView):
    """
    Omni-Search for Super Admin.
    Searches: Clients (Institute Name, Email), Students (Name), Payments (Transaction ID).
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Unauthorized'}, status=403)

        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response([], status=200) # Too short

        results = []
        from django.db.models import Q

        # 1. Search Clients (Institutes)
        clients = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(profile__institution_name__icontains=query)
        ).select_related('profile')[:5]

        for c in clients:
            try:
                inst_name = c.profile.institution_name or c.username
                plan = c.profile.institution_type
            except:
                inst_name = c.username
                plan = 'N/A'
            
            results.append({
                'category': 'INSTITUTES',
                'title': inst_name,
                'subtitle': f"{c.email} • {plan}",
                'icon': 'fas fa-building',
                'action_type': 'CLIENT',
                'id': c.id
            })

        # 2. Search Students
        students = Student.objects.filter(
            name__icontains=query
        )[:5]

        for s in students:
            results.append({
                'category': 'STUDENTS',
                'title': s.name,
                'subtitle': f"Class {s.grade} • {s.enrollment_id}",
                'icon': 'fas fa-user-graduate',
                'action_type': 'STUDENT',
                'id': s.id
            })

        # 3. Search Payments (Transactions)
        payments = Payment.objects.filter(
            Q(transaction_id__icontains=query) |
            Q(metadata__institution_name__icontains=query) |
            Q(metadata__email__icontains=query)
        )[:5]

        for p in payments:
            results.append({
                'category': 'FINANCE',
                'title': f"₹{p.amount}",
                'subtitle': f"Ref: {p.transaction_id}",
                'icon': 'fas fa-receipt',
                'action_type': 'PAYMENT',
                'id': p.id
            })

        return Response(results, status=200)
