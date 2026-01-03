from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import ClientSubscription, UserProfile
from datetime import date
import random
import string
import logging

class SubscriptionPurchaseView(APIView):
    """
    Endpoint for purchasing a new subscription (School, Coaching, Institute).
    This mocks the payment initiation and success for the demo/backend fix.
    """
    permission_classes = [permissions.AllowAny] # Allow non-users to buy

    def post(self, request):
        plan_type = request.data.get('plan_type') # SCHOOL, COACHING, INSTITUTE
        email = request.data.get('email')
        phone = request.data.get('phone')
        amount = request.data.get('amount')
        
        if not plan_type or not email:
             return Response({"error": "Plan Type and Email are required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create or Get User
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        
        if created:
            # Generate random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user.set_password(password)
            user.save()
            # In real app: Send email with password
            print(f"Generated Credentials for {email}: {password}")
        
        # 2. Create Profile if not exists
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(
                user=user, 
                role='ADMIN', 
                institution_type=plan_type,
                phone=phone or ''
            )
        else:
            user.profile.institution_type = plan_type
            user.profile.save()

        # 3. Create Subscription Record (Pending Payment)
        sub, sub_created = ClientSubscription.objects.get_or_create(user=user)
        sub.plan_type = plan_type
        sub.amount_paid = amount
        sub.status = 'PENDING'
        sub.save()
        
        # 4. Return "Payment Link" (Mock or Real)
        # For this fix, we will simulate immediate success for the user to see the result
        # OR return the Eazypay link.
        
        return Response({
            "status": "INITIATED",
            "message": "Subscription initiated. Please proceed to payment.",
            "payment_url": f"/api/payment/subscription/mock_success/?email={email}" # Short-circuit for demo
        })


class SubscriptionSuccessView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        user = User.objects.get(email=email)
        
        # Activate Subscription (30 Days Standard)
        sub = user.subscription
        sub.activate(days=30) 
        
        # Generate credentials if new
        new_pass = ""
        if not user.password:
             new_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
             user.set_password(new_pass)
             user.save()

        return Response({
            "status": "SUCCESS",
            "message": f"Plan {sub.plan_type} Activated Successfully!",
            "credentials": {
                "username": user.username,
                "password_note": "Sent to email (Simulated)",
            },
            "dashboard_url": "/dashboard/"
        })
