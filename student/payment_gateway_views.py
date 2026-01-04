from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
import uuid
import logging
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

# Initialize Razorpay Client
# Use test keys if real ones aren't available yet
KEY_ID = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_YourKeyHere')
KEY_SECRET = getattr(settings, 'RAZORPAY_KEY_SECRET', 'YourSecretHere')

client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

class CreateOrderView(APIView):
    permission_classes = [AllowAny]
    """
    Creates a Razorpay Order ID for frontend checkout.
    """
    def post(self, request):
        try:
            amount = request.data.get('amount')
            currency = "INR"
            
            if not amount:
                 return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if Razorpay keys are properly configured
            if not KEY_ID or not KEY_SECRET or 'YourKeyHere' in KEY_ID or len(KEY_ID) < 10:
                return Response({
                    'error': 'PAYMENT_GATEWAY_NOT_CONFIGURED',
                    'message': 'Automatic payment gateway is not available. Please use Manual Bank Transfer payment method.',
                    'payment_method': 'BANK_TRANSFER',
                    'instructions': 'You will be shown QR code and bank details for payment.',
                    'status': 'gateway_unavailable'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

            # REAL RAZORPAY ORDER CREATION
            # Razorpay expects amount in paise (1 INR = 100 paise)
            data = {
                "amount": int(amount) * 100,
                "currency": currency,
                "payment_capture": "1", # Auto capture
                "receipt": str(uuid.uuid4())
            }
            
            order = client.order.create(data=data)
            
            return Response({
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': KEY_ID,
                'receipt': order['receipt']
            }, status=status.HTTP_201_CREATED)
            
        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay BadRequest: {e}")
            return Response({
                'error': 'Invalid Payment Request',
                'message': 'Payment order creation failed. Please check amount and try again.',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Razorpay Error: {e}")
            return Response({
                'error': 'Payment Gateway Error',
                'message': 'Unable to create payment order. Please try again later.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
