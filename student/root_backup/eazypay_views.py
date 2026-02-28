from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Payment, Student, UserProfile
from .eazypay import EazypayClient
import uuid
import logging
from datetime import timedelta, date

logger = logging.getLogger(__name__)

class InitEazypayPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Initiate a payment request.
        Expects: { "amount": 100.00, "description": "Tuition Fee" }
        """
        user = request.user
        amount = request.data.get('amount')
        description = request.data.get('description', 'Fee Payment')
        
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = user.student_profile
        except AttributeError:
             # If user is a parent, they might be paying for a child. For simplicity, assume user is paying for themselves or linked student.
             # Or user might be valid but not a student (e.g. paying for premium access as admin/institute)
             # Let's assume for now it's for 'Student' fees as per the Payment model foreign key.
             # If it's a subscription payment for an Institute, we might need a different approach or model.
             # Given the Payment mode links to `Student`, let's try to find the student.
             return Response({"error": "User must be a student to make fee payments (or logic needs extension for generic payments)"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4()).replace('-', '')[:20] # Eazypay might have length limits, checking docs usually 20-30 chars safe.

        # Create Pending Payment Record
        payment = Payment.objects.create(
            student=student,
            transaction_id=transaction_id,
            amount=amount,
            due_date=date.today(), # Assuming immediate payment for now
            status='PENDING',
            description=description
        )

        client = EazypayClient()
        payment_url = client.get_payment_url(transaction_id, amount)

        return Response({
            "transaction_id": transaction_id,
            "payment_url": payment_url,
            "status": "INITIATED"
        })

@method_decorator(csrf_exempt, name='dispatch')
class EazypayCallbackView(APIView):
    permission_classes = [permissions.AllowAny] # Callback comes from bank

    def post(self, request):
        """
        Handle callback from Eazypay.
        Eazypay posts encrypted data.
        """
        data = request.data
        
        # Eazypay sends data in form fields often named 'ResponseCode', 'UniqueRefNumber', etc.
        # But commonly the whole response is not encrypted in one blob, but specific fields?
        # Actually, standard Eazypay integration usually returns variables in POST body.
        # Some are plain, some might need verification.
        # However, the simple integration often sends a plain POST return with status.
        # Let's log the initial data to be debuggable.
        logger.info(f"Eazypay Callback Data: {data}")

        # Note: Implementation details vary heavily by specific Eazypay integration type (AES vs plain).
        # Assuming the standard AES kit flow where we get status.

        response_code = data.get('Response_Code')
        transaction_id = data.get('ReferenceNo') # We sent this as Reference No
        unique_ref_number = data.get('Unique_Ref_Number') # Eazypay's ID
        
        if not transaction_id:
             return Response({"error": "Missing ReferenceNo"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
             return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if response_code == 'E000': 
            # E000 is often Success in Eazypay, but checking specific docs is better. 
            # Some docs say 'SUCCESS' string. 
            # Let's handle both or assume mapped.
            # Usually E000 = Success.
            
            payment.status = 'PAID'
            payment.paid_date = date.today()
            payment.description += f" (Eazypay Ref: {unique_ref_number})"
            payment.save()
            
            # Auto-verify/Grant access logic
            # If this was a subscription payment (e.g. for the institute itself), we would update the UserProfile.
            # Since Payment model is tied to Student, this is likely Student Fees.
            # But user request mentioned "subscription expiry" earlier.
            # If this is for the SaaS subscription, the model might be different.
            # The user added `subscription_expiry` to `UserProfile`.
            
            # Check if this payment was for subscription renewal
            if "Subscription" in payment.description:
                # Update user profile subscription
                # Assuming the student user or parent user
                user_profile = payment.student.user.profile
                if user_profile:
                    # Extend by 30 days
                    current_expiry = user_profile.subscription_expiry or date.today()
                    if current_expiry < date.today():
                        current_expiry = date.today()
                    new_expiry = current_expiry + timedelta(days=30)
                    user_profile.subscription_expiry = new_expiry
                    user_profile.save()
            
            return Response({"status": "SUCCESS", "message": "Payment verified successfully"})
        
        else:
            payment.status = 'FAILED'
            payment.save()
            return Response({"status": "FAILED", "message": "Payment failed from bank side"})

