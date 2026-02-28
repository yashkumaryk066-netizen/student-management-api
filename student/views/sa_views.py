from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken    
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
from student.models import ClientSubscription, UserProfile, User, Payment

class SuperAdminClientsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Access denied'}, status=403)
        
        clients = []
        subs = ClientSubscription.objects.select_related('user').all().order_by('-created_at')
        
        for sub in subs:
            user = sub.user
            if user.is_superuser:
                continue
                
            profile = getattr(user, 'profile', None)
            
            clients.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'institution_name': profile.institution_name if profile else 'N/A',
                'institution_type': profile.institution_type if profile else sub.plan_type,
                'plan': sub.plan_type,
                'days_remaining': sub.days_remaining,
                'subscription_status': sub.status,
                'is_active': user.is_active,
                'total_paid': str(sub.amount_paid),
                'created_at': sub.created_at.strftime('%Y-%m-%d')
            })
            
        return Response(clients)

class SuperAdminImpersonateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Function locked to Super Admin'}, status=403)
            
        target_user = get_object_or_404(User, pk=pk)
        
        # Don't impersonate another superuser (security measure)
        if target_user.is_superuser:
             return Response({'error': 'Cannot impersonate another Super Admin'}, status=400)
             
        # Generate tokens for the target user without password
        refresh = RefreshToken.for_user(target_user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': target_user.username,
            'role': target_user.profile.role if hasattr(target_user, 'profile') else 'USER'
        })


class SuperAdminSubscriptionOverviewView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Access denied'}, status=403)

        today = timezone.now().date()

        # Pending subscription payments for approval table
        pending_qs = Payment.objects.filter(
            payment_type='SUBSCRIPTION',
            status='PENDING_VERIFICATION'
        ).select_related('user').order_by('-created_at')

        pending_payments = []
        for p in pending_qs:
            metadata = p.metadata or {}
            email = metadata.get('email') or (p.user.email if p.user else 'Unknown')
            pending_payments.append({
                'id': p.id,
                'email': email,
                'plan_type': metadata.get('plan_type', 'COACHING'),
                'amount': str(p.amount),
                'utr': p.transaction_id or metadata.get('utr', 'N/A'),
                'date': p.created_at.strftime('%Y-%m-%d %H:%M'),
                'institution_name': metadata.get('institution_name', 'N/A')
            })

        # Client registry table
        client_subscriptions = []
        subs = ClientSubscription.objects.select_related('user').filter(
            user__is_superuser=False
        ).order_by('-created_at')

        for sub in subs:
            client_subscriptions.append({
                'id': sub.user.id,
                'username': sub.user.username,
                'email': sub.user.email,
                'plan_type': sub.plan_type,
                'status': sub.status,
                'is_expired': sub.days_remaining == 0,
                'start_date': sub.start_date.strftime('%Y-%m-%d') if sub.start_date else '-',
                'end_date': sub.end_date.strftime('%Y-%m-%d') if sub.end_date else '-',
                'days_left': sub.days_remaining,
                'amount_paid': str(sub.amount_paid)
            })

        total_revenue = Payment.objects.filter(
            payment_type='SUBSCRIPTION',
            status='APPROVED'
        ).aggregate(total=Sum('amount'))['total'] or 0

        active_subscriptions = ClientSubscription.objects.filter(status='ACTIVE').count()
        total_clients = ClientSubscription.objects.filter(user__is_superuser=False).count()

        return Response({
            'stats': {
                'total_revenue': float(total_revenue),
                'active_subscriptions': active_subscriptions,
                'total_clients': total_clients,
                'pending_approvals': pending_qs.count()
            },
            'pending_payments': pending_payments,
            'client_subscriptions': client_subscriptions
        })


class SuperAdminClientActionView(APIView):
    """
    Handle client lifecycle actions from super-admin dashboard.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Unauthorized'}, status=403)

        client_id = request.data.get('client_id')
        action = (request.data.get('action') or '').upper()

        if not client_id or not action:
            return Response({'error': 'Missing client_id or action'}, status=400)

        user = get_object_or_404(User, id=client_id)
        if user.is_superuser:
            return Response({'error': 'Cannot perform this action on super admin'}, status=400)

        with transaction.atomic():
            today = date.today()
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'CLIENT', 'institution_type': 'COACHING'}
            )
            default_plan = (profile.institution_type or 'COACHING').upper()
            if default_plan not in {'SCHOOL', 'COACHING', 'INSTITUTE'}:
                default_plan = 'COACHING'

            sub, _ = ClientSubscription.objects.get_or_create(
                user=user,
                defaults={
                    'plan_type': default_plan,
                    'status': 'PENDING',
                    'start_date': today,
                    'end_date': today
                }
            )

            msg = ''

            if action == 'SUSPEND':
                sub.status = 'SUSPENDED'
                user.is_active = False
                profile.is_active = False
                msg = f'Client {user.username} suspended successfully.'

            elif action == 'ACTIVATE':
                sub.status = 'ACTIVE'
                if not sub.start_date:
                    sub.start_date = today
                if not sub.end_date or sub.end_date < today:
                    sub.end_date = today + timedelta(days=30)
                user.is_active = True
                profile.is_active = True
                msg = f'Client {user.username} activated.'

            elif action == 'REDUCE_DAYS':
                if sub.end_date:
                    sub.end_date = sub.end_date - timedelta(days=7)
                    if sub.end_date < today and sub.status != 'SUSPENDED':
                        sub.status = 'EXPIRED'
                    msg = 'Plan duration reduced by 7 days.'
                else:
                    msg = 'No active plan to reduce.'

            elif action == 'EXTEND_DAYS':
                base = sub.end_date if sub.end_date and sub.end_date >= today else today
                sub.end_date = base + timedelta(days=30)
                if not sub.start_date:
                    sub.start_date = today
                sub.status = 'ACTIVE'
                user.is_active = True
                profile.is_active = True
                msg = f'Plan extended by 30 days. New expiry: {sub.end_date}'

            elif action == 'DELETE':
                username = user.username
                user.delete()
                return Response({'message': f'Client {username} and related account data deleted permanently.'})

            else:
                return Response({'error': 'Invalid action type'}, status=400)

            sub.save()
            profile.subscription_expiry = sub.end_date
            profile.save()
            user.save(update_fields=['is_active'])

            return Response({
                'message': msg,
                'new_status': sub.status,
                'new_expiry': sub.end_date
            })
