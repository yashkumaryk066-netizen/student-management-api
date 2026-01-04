from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.db import models
from .models import ClientSubscription, UserProfile, Payment, Notification
from datetime import date, timedelta
import random
import string
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny

class PublicSubscriptionSubmitView(APIView):
    """
    Public endpoint for Clients to submit Manual Bank Transfer details for a new subscription.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        plan_type = request.data.get('plan_type')
        amount = request.data.get('amount')
        utr = request.data.get('utr')

        if not all([email, plan_type, amount, utr]):
            return Response({'error': 'All fields (email, plan_type, amount, utr) are required.'}, status=400)

        # Check duplicate UTR
        if Payment.objects.filter(transaction_id=utr).exists():
            return Response({'error': 'This UTR/Transaction ID has already been submitted.'}, status=400)

        # Create Payment Record
        Payment.objects.create(
            amount=amount,
            transaction_id=utr,
            plan_type=plan_type,
            status='PENDING_VERIFICATION',
            payment_type='SUBSCRIPTION',
            metadata={'email': email} # Store email for user creation later
        )

        return Response({'message': 'Payment submitted successfully! Admin will verify and email your credentials.'})


class PendingPaymentsListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        payments = Payment.objects.filter(status='PENDING_VERIFICATION').order_by('-created_at')
        data = []
        for p in payments:
            email = "Unknown"
            if p.user:
                email = p.user.email
            elif p.metadata:
                email = p.metadata.get('email', 'Unknown')
                
            data.append({
                'id': p.id,
                'email': email,
                'amount': p.amount,
                'utr': p.transaction_id,
                'plan': p.plan_type,
                'date': p.created_at
            })
        return Response(data)

class AdminPaymentApprovalView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        action = request.data.get('action') # 'approve' or 'reject'
        notes = request.data.get('notes', '')

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=404)

        if action == 'approve':
            # 1. Create User if not exists
            email = payment.metadata.get('email')
            if not email and payment.user:
                email = payment.user.email
            
            if not email:
                return Response({'error': 'No email found for this payment'}, status=400)

            user = None
            password = None
            created = False

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user
                username = email.split('@')[0]
                # Ensure unique username
                while User.objects.filter(username=username).exists():
                    username = email.split('@')[0] + str(random.randint(1000, 9999))
                
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                user = User.objects.create_user(username=username, email=email, password=password)
                created = True

            # 2. Create/Update Subscription
            sub, _ = ClientSubscription.objects.get_or_create(user=user)
            sub.plan_type = payment.plan_type or 'SCHOOL'
            sub.transaction_id = payment.transaction_id
            sub.amount_paid = payment.amount
            sub.activate(days=30) # Activates and sets dates

            # 3. Create Profile
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user, role='CLIENT', institution_type=sub.plan_type)

            # 4. Update Payment
            payment.status = 'APPROVED'
            payment.user = user
            payment.save()

            # 5. Send Email with Credentials
            if created:
                subject = 'Welcome to NextGen ERP - Assessment Approved'
                message = f"""
                Congratulations! Your {sub.plan_type} subscription is approved.

                Here are your login credentials:
                URL: https://yashamishra.pythonanywhere.com/dashboard/login
                Username: {user.username}
                Password: {password}

                Please login and change your password immediately.
                """
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
                except Exception as e:
                    logger.error(f"Failed to send email: {e}")
            else:
                 # Existing user - just notify
                 message = f"Your subscription for {sub.plan_type} has been renewed successfully."
                 try:
                    send_mail("Subscription Active", message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
                 except: pass

            return Response({'message': 'Approved and credentials sent.'})

        elif action == 'reject':
            payment.status = 'REJECTED'
            payment.save()
             # Notify rejection
            email = payment.metadata.get('email')
            if email:
                try:
                    send_mail("Subscription Rejected", f"Reason: {notes}", settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
                except: pass
            
            return Response({'message': 'Payment rejected.'})

        return Response({'error': 'Invalid action'}, status=400)

class SuperAdminDashboardView(APIView):
    """
    Super admin overview of all client subscriptions.
    Shows stats, pending approvals, and all client subscriptions.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        # Only allow superusers
        if not request.user.is_superuser:
            return Response({
                "error": "Access denied. Super admin only."
            }, status=status.HTTP_403_FORBIDDEN)

        # Get stats
        total_users = User.objects.filter(is_superuser=False).count()
        active_subscriptions = ClientSubscription.objects.filter(status='ACTIVE').count()
        pending_payments = Payment.objects.filter(status='PENDING_VERIFICATION').count()
        
        # Revenue stats
        total_revenue = Payment.objects.filter(status='APPROVED').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        # Get all client subscriptions
        subscriptions = []
        # Removed user__profile from select_related as it might not exist for all users or invalid lookup
        all_subs = ClientSubscription.objects.select_related('user').all()
        
        for sub in all_subs:
            if sub.user.is_superuser:
                continue  # Skip super admin
                
            today = date.today()
            days_left = 0
            if sub.end_date:
                days_left = (sub.end_date - today).days
                
            subscriptions.append({
                'user_id': sub.user.id,
                'username': sub.user.username,
                'email': sub.user.email,
                'plan_type': sub.plan_type,
                'status': sub.status,
                'start_date': sub.start_date,
                'end_date': sub.end_date,
                'days_left': days_left if days_left > 0 else 0,
                'amount_paid': str(sub.amount_paid),
                'is_expired': days_left <= 0
            })
        
        # Get pending payment details
        pending_list = []
        pending_pmts = Payment.objects.filter(status='PENDING_VERIFICATION').order_by('-created_at')[:10]
        
        for pmt in pending_pmts:
            user_name = "Unknown"
            if pmt.user:
                user_name = pmt.user.username
            elif pmt.student:
                user_name = pmt.student.name
            elif pmt.metadata:
                # Safer get
                user_name = pmt.metadata.get('email', 'Unknown') if pmt.metadata else 'Unknown'
                
            pending_list.append({
                'id': pmt.id,
                'user': user_name,
                'type': pmt.payment_type, # Using new field
                'amount': str(pmt.amount),
                'utr': pmt.transaction_id,
                'date': pmt.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return Response({
            'stats': {
                'total_clients': total_users,
                'active_subscriptions': active_subscriptions,
                'pending_approvals': pending_payments,
                'total_revenue': str(total_revenue)
            },
            'pending_payments': pending_list,
            'client_subscriptions': subscriptions,
            'recent_notifications': Notification.objects.filter(recipient_type='ADMIN').order_by('-created_at')[:5].values('title', 'message', 'created_at')
        })

class SuperAdminClientActionView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Superuser only

    def post(self, request):
        client_id = request.data.get('client_id')
        action = request.data.get('action') # SUSPEND, ACTIVATE, REDUCE_DAYS

        try:
            # We need to find the subscription. Client ID here is the User ID.
            subscription = ClientSubscription.objects.get(user_id=client_id)
            user_profile = UserProfile.objects.get(user_id=client_id)

            if action == 'SUSPEND':
                subscription.status = 'SUSPENDED'
                subscription.save()
                return Response({'message': 'Client account suspended successfully.'})

            elif action == 'ACTIVATE':
                subscription.status = 'ACTIVE'
                subscription.save()
                return Response({'message': 'Client account reactivated successfully.'})

            elif action == 'REDUCE_DAYS':
                if subscription.end_date:
                    from datetime import timedelta
                    subscription.end_date -= timedelta(days=7)
                    subscription.save()
                    # Sync Profile if exists
                    if user_profile:
                        user_profile.subscription_expiry = subscription.end_date
                        user_profile.save()
                    return Response({'message': 'Validity reduced by 7 days.'})
                else:
                    return Response({'error': 'Subscription has no end date.'}, status=400)

            return Response({'error': 'Invalid action'}, status=400)

        except ClientSubscription.DoesNotExist:
            return Response({'error': 'Subscription not found for this user.'}, status=404)
        except UserProfile.DoesNotExist:
             return Response({'error': 'User Profile not found.'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
