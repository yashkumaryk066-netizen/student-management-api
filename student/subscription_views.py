from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import ClientSubscription, UserProfile
from datetime import date
import random
import string
import logging

from decimal import Decimal

class SubscriptionPurchaseView(APIView):
    """
    Endpoint for purchasing a new subscription (School, Coaching, Institute).
    Enforces strict pricing and delays credential generation until payment success.
    """
    permission_classes = [permissions.AllowAny] 

    PRICING = {
        'SCHOOL': Decimal('1000.00'),
        'COACHING': Decimal('500.00'),
        'INSTITUTE': Decimal('1500.00')
    }

    def post(self, request):
        plan_type = request.data.get('plan_type') 
        email = request.data.get('email')
        phone = request.data.get('phone')
        try:
            amount = Decimal(str(request.data.get('amount', 0)))
        except:
            amount = Decimal('0.00')
        
        if not plan_type or not email:
             return Response({"error": "Plan Type and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
             
        # Strict Pricing Check
        expected_price = self.PRICING.get(plan_type)
        if not expected_price:
            return Response({"error": "Invalid Plan Type"}, status=status.HTTP_400_BAD_REQUEST)
            
        # STRICT VERIFICATION: If amount is LESS than price (even by 1 rupee), REJECT.
        if amount < expected_price:
             return Response({
                 "error": "Payment Verification Failed: Amount is less than required plan price.",
                 "required": str(expected_price),
                 "received": str(amount),
                 "message": "Full payment required. Username/Password will NOT be issued."
             }, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create or Get User (Without Password initially if new)
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        
        if created:
            user.set_unusable_password() # No access yet
            user.save()
        
        # 2. Create Profile if not exists
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(
                user=user, 
                role='CLIENT', 
                institution_type=plan_type,
                phone=phone or ''
            )
        else:
            # Update intended plan
            user.profile.institution_type = plan_type
            user.profile.save()

        # 3. Create Subscription Record (Pending Payment)
        sub, sub_created = ClientSubscription.objects.get_or_create(user=user)
        sub.plan_type = plan_type
        sub.amount_paid = amount
        sub.status = 'PENDING'
        sub.save()
        
        # 4. Return Payment Link
        return Response({
            "status": "INITIATED",
            "message": "Payment amount verified. Proceeding to gateway...",
            "payment_url": f"/api/subscription/success/?email={email}&amount={amount}&plan={plan_type}" 
        })


class SubscriptionSuccessView(APIView):
    """
    Callback/Success handler. 
    Verifies payment again and ONLY THEN generates credentials.
    """
    permission_classes = [permissions.AllowAny]

    PRICING = {
        'SCHOOL': Decimal('1000.00'),
        'COACHING': Decimal('500.00'),
        'INSTITUTE': Decimal('1500.00')
    }

    def get(self, request):
        email = request.query_params.get('email')
        try:
            received_amount = Decimal(str(request.query_params.get('amount', 0)))
        except:
             received_amount = Decimal('0.00')
             
        plan_type = request.query_params.get('plan')
        
        try:
            user = User.objects.get(email=email)
            sub = user.subscription
        except (User.DoesNotExist, AttributeError):
             return Response({"error": "Subscription request not found"}, status=status.HTTP_404_NOT_FOUND)

        # DOUBLE CHECK: Strict Pricing Verification
        expected_price = self.PRICING.get(plan_type, Decimal('999999.00')) # Default high to fail if unknown
        
        # CRITICAL SECURITY CHECK
        # If amount is less than expected price, DO NOT ISSUE CREDENTIALS.
        if received_amount < expected_price:
             # Transaction Failed or Manipulation Attempt
             sub.status = 'FAILED'
             sub.save()
             return Response({
                 "status": "FAILED", 
                 "error": "Strict Pricing Check Failed: Talk to Admin.",
                 "details": "Credential generation blocked due to insufficient payment."
             }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # SUCCESS PATH
        
        # 1. Activate Subscription
        sub.plan_type = plan_type
        sub.amount_paid = received_amount
        sub.activate(days=30) 
        
        # 2. Generate Credentials (ONLY NOW)
        credentials_generated = False
        plain_password = None
        
        if not user.has_usable_password():
             # Generate secure password
             plain_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
             user.set_password(plain_password)
             user.save()
             credentials_generated = True
        
        # 3. Return Success Details
        return Response({
            "status": "SUCCESS",
            "message": f"Plan {sub.plan_type} Activated Successfully! Payment Verified.",
            "credentials": {
                "username": user.username,
                "password": plain_password if credentials_generated else "****** (Existing)",
                "note": "Please save these credentials immediately."
            },
            "dashboard_url": "/dashboard/"
        })

class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'subscription'):
             return Response({"status": "NO_SUBSCRIPTION", "message": "No active plan found."})
        
        sub = request.user.subscription
        today = date.today()
        days_left = 0
        if sub.end_date:
            days_left = (sub.end_date - today).days
        
        return Response({
            "plan_type": sub.plan_type,
            "status": sub.status,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "days_left": days_left if days_left > 0 else 0,
            "amount_paid": sub.amount_paid,
            "is_expired": days_left <= 0
        })
