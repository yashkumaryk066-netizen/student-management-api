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
            metadata = pmt.metadata or {}
            pending_list.append({
                'id': pmt.id,
                'email': metadata.get('email'),
                'plan_type': metadata.get('plan_type'),
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
            'client_subscriptions': subscriptions
        })
