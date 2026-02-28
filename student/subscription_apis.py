from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework import serializers
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from student.models import ClientSubscription
import json

class SubscriptionApiFallbackSerializer(serializers.Serializer):
    detail = serializers.CharField(required=False)


class SchemaAPIView(APIView):
    serializer_class = SubscriptionApiFallbackSerializer

class SubscriptionApprovalAPI(SchemaAPIView):
    """Approve pending subscription request"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        try:
            data = json.loads(request.body) if request.body else request.data
            user_id = data.get('user_id')
            days = int(data.get('days', 30))
            
            if not user_id:
                return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return Response({'error': 'Cannot approve super admin account'}, status=status.HTTP_400_BAD_REQUEST)
            subscription, created = ClientSubscription.objects.get_or_create(user=user)
            
            # Activate subscription
            subscription.activate(days=days)
            
            return Response({
                'success': True,
                'message': f'Subscription activated for {user.username}',
                'subscription': {
                    'user': user.username,
                    'plan': subscription.plan_type,
                    'status': subscription.status,
                    'start_date': str(subscription.start_date),
                    'end_date': str(subscription.end_date),
                    'days_remaining': subscription.days_remaining
                }
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionRejectAPI(SchemaAPIView):
    """Reject pending subscription request"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        try:
            data = json.loads(request.body) if request.body else request.data
            user_id = data.get('user_id')
            
            if not user_id:
                return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return Response({'error': 'Cannot reject super admin account'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete subscription request or mark as rejected
            ClientSubscription.objects.filter(user=user, status='PENDING').delete()
            
            return Response({
                'success': True,
                'message': f'Subscription request rejected for {user.username}'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientBlockAPI(SchemaAPIView):
    """Block/Suspend client access"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        try:
            data = json.loads(request.body) if request.body else request.data
            user_id = data.get('user_id')
            
            if not user_id:
                return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return Response({'error': 'Cannot block super admin account'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Block user
            user.is_active = False
            user.save()
            
            # Suspend subscription
            if hasattr(user, 'subscription'):
                user.subscription.status = 'SUSPENDED'
                user.subscription.save()
            
            return Response({
                'success': True,
                'message': f'Client {user.username} has been blocked'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientUnblockAPI(SchemaAPIView):
    """Unblock client access"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        try:
            data = json.loads(request.body) if request.body else request.data
            user_id = data.get('user_id')
            
            if not user_id:
                return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
            
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return Response({'error': 'Cannot unblock super admin account'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Unblock user
            user.is_active = True
            user.save()
            
            # Reactivate subscription if it was suspended
            if hasattr(user, 'subscription') and user.subscription.status == 'SUSPENDED':
                user.subscription.status = 'ACTIVE'
                user.subscription.save()
            
            return Response({
                'success': True,
                'message': f'Client {user.username} has been unblocked'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientDeleteAPI(SchemaAPIView):
    """Delete client permanently"""
    permission_classes = [permissions.IsAdminUser]
    
    def delete(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return Response({'error': 'Cannot delete super admin account'}, status=status.HTTP_400_BAD_REQUEST)
            username = user.username
            
            # Delete user (cascade will delete subscription)
            user.delete()
            
            return Response({
                'success': True,
                'message': f'Client {username} has been permanently deleted'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClientCredentialsAPI(SchemaAPIView):
    """Get client credentials"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request, user_id):
        try:
            user = get_object_or_404(User, id=user_id)
            if user.is_superuser:
                return Response({'error': 'Cannot view super admin credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
            credentials = {
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'is_active': user.is_active,
            }
            
            if hasattr(user, 'subscription'):
                sub = user.subscription
                credentials.update({
                    'plan_type': sub.plan_type,
                    'status': sub.status,
                    'start_date': str(sub.start_date) if sub.start_date else None,
                    'end_date': str(sub.end_date) if sub.end_date else None,
                    'days_remaining': sub.days_remaining,
                    'amount_paid': str(sub.amount_paid),
                })
            
            return Response(credentials)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
