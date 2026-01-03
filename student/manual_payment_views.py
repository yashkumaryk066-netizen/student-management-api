from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Payment
from datetime import date
import logging

logger = logging.getLogger(__name__)

class ManualPaymentSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Submit a manual payment reference (UTR/Transaction ID).
        Expects: { "amount": "500.00", "transaction_id": "UPI123456", "description": "Tuition Fee" }
        """
        user = request.user
        try:
            student = user.student_profile
        except AttributeError:
             return Response({"error": "Only students can submit fee payments"}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        txn_id = request.data.get('transaction_id')
        description = request.data.get('description', 'Fee Payment')

        if not amount or not txn_id:
            return Response({"error": "Amount and Transaction ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate transaction ID
        if Payment.objects.filter(transaction_id=txn_id).exists():
             return Response({"error": "This Transaction ID has already been submitted."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Pending Payment Record
        payment = Payment.objects.create(
            student=student,
            transaction_id=txn_id,
            amount=amount,
            due_date=date.today(),
            status='PENDING', # Needs Admin Approval
            description=f"{description} (Manual: {txn_id})"
        )

        # In a real app, notify admin here via SMS/Email
        
        return Response({
            "status": "SUBMITTED",
            "message": "Payment submitted for verification. It will be updated once approved by Admin."
        })
