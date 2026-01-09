from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import AISubscription, Payment
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from rest_framework.permissions import AllowAny

class AIChatView(APIView):
    """
    Serve the Premium Y.S.M AI Chat Interface.
    Protected: Redirects unauthenticated to AI Login.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/api/ai/auth/')

        user = request.user
        
        # --- FREE ACCESS MODE (LOGIN REQUIRED) ---
        # Strictly enforces IsAuthenticated via permission_classes
        
        context = {
            'is_access_granted': True, # Always grant if logged in
            'status': 'ACTIVE',
            'days_remaining': '∞', # Infinite for now
            'username': user.username,
            'display_name': user.first_name if user.first_name else user.username.split('@')[0].title(),
            'role': getattr(user, 'profile', None).role if hasattr(user, 'profile') else 'USER',
            'qr_code_url': '/static/img/upi_qr.jpg' 
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
            
            if not transaction_id:
                return Response({"error": "Transaction ID is required"}, status=400)
            
            # Check for duplicates
            if Payment.objects.filter(transaction_id=transaction_id).exists():
                 return Response({"error": "This transaction ID is already used."}, status=400)

            # Create Payment Record
            payment = Payment.objects.create(
                user=request.user,
                amount=50.00,
                transaction_id=transaction_id,
                payment_type='SUBSCRIPTION',
                payment_mode='UPI',
                status='PENDING_VERIFICATION',
                description='AI Subscription - Weekly (Manual Premium)',
                due_date=timezone.now().date(),
                paid_date=timezone.now().date()
            )
            
            # Update Subscription to PENDING
            sub = AISubscription.objects.get(user=request.user)
            sub.status = 'PENDING'
            sub.last_payment_id = transaction_id
            sub.save()
            
            return Response({"success": True, "message": "Payment submitted. Waiting for approval."})
            
        except Exception as e:
            logger.error(f"AI Payment Error: {e}")
            return Response({"error": str(e)}, status=500)
