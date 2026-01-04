from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.db import models
from .models import ClientSubscription, UserProfile, Payment
from datetime import date, timedelta
import random
import string
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

# ... (keep existing views: SubscriptionPurchaseView, SubscriptionPaymentVerifyView, AdminPaymentApprovalView, PendingPaymentsListView)

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
        all_subs = ClientSubscription.objects.select_related('user', 'user__profile').all()
        
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
                user_name = pmt.metadata.get('email', 'Unknown')
                
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
            'recent_notifications': models.Notification.objects.filter(recipient_type='ADMIN').order_by('-created_at')[:5].values('title', 'message', 'created_at')
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
