from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import razorpay
import uuid
import logging

logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    """
    Creates a Razorpay Order ID for frontend checkout.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        amount = request.data.get('amount')

        if not amount:
            return Response(
                {'error': 'Amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------
        # Razorpay keys (NO merchant ID)
        # -------------------------------
        key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)

        if not key_id or not key_secret:
            return Response({
                'error': 'PAYMENT_GATEWAY_NOT_CONFIGURED',
                'message': 'Online payment is currently unavailable.',
                'fallback_payment': 'BANK_TRANSFER'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except:
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client = razorpay.Client(auth=(key_id, key_secret))

            order_data = {
                "amount": amount * 100,  # INR → paise
                "currency": "INR",
                "payment_capture": 1,
                "receipt": f"rcpt_{uuid.uuid4().hex[:12]}"
            }

            order = client.order.create(order_data)

            return Response({
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': key_id,
                'receipt': order['receipt']
            }, status=status.HTTP_201_CREATED)

        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay BadRequest: {e}")
            return Response({
                'error': 'INVALID_PAYMENT_REQUEST',
                'message': 'Unable to create payment order'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Razorpay Error: {e}")
            return Response({
                'error': 'PAYMENT_GATEWAY_ERROR',
                'message': 'Payment service temporarily unavailable'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
