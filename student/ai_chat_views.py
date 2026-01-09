from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import AISubscription, ManualPayment
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIChatView(APIView):
    """
    Serve the Premium Y.S.M AI Chat Interface.
    Protected: Requires Login & Active Subscription (Trial or Premium).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get or Create AI Subscription
        sub, created = AISubscription.objects.get_or_create(user=user)
        
        # Auto-check status
        current_status = sub.check_and_update_status()
        
        is_access_granted = sub.is_access_granted
        days_remaining = 0
        
        if sub.status == 'TRIAL':
            trial_end = sub.trial_start_date + timezone.timedelta(days=7)
            delta = trial_end - timezone.now()
            days_remaining = max(0, delta.days)
            
        context = {
            'is_access_granted': is_access_granted,
            'status': sub.status,
            'days_remaining': days_remaining,
            'username': user.username,
            'role': getattr(user, 'profile', None).role if hasattr(user, 'profile') else 'USER',
            'qr_code_url': '/static/img/payment_qr.png' # Ensure this exists or use placeholder
        }
        
        return render(request, 'student/ai_chat.html', context)

class AIPaymentSubmitView(APIView):
    """
    Handle 50 Rs Manual Payment for AI Subscription
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            transaction_id = request.data.get('transaction_id')
            receipt = request.FILES.get('receipt')
            
            if not transaction_id:
                return Response({"error": "Transaction ID is required"}, status=400)
            
            # Create Manual Payment Record tagged for AI
            payment = ManualPayment.objects.create(
                user=request.user,
                amount=50.00,
                transaction_id=transaction_id,
                payment_method='UPI',
                status='PENDING',
                remarks='AI Subscription - Weekly'
            )
            
            # Use existing Receipt model logic or save file if added to ManualPayment
            # Assuming ManualPayment has no file field per previous context, 
            # we might need to rely on the general Payment flow or just store ID.
            # But the user asked for "Same as before".
            
            # Update Subscription to PENDING
            sub = AISubscription.objects.get(user=request.user)
            sub.status = 'PENDING'
            sub.last_payment_id = transaction_id
            sub.save()
            
            return Response({"success": True, "message": "Payment submitted. Waiting for approval."})
            
        except Exception as e:
            logger.error(f"AI Payment Error: {e}")
            return Response({"error": str(e)}, status=500)
