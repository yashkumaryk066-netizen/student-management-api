from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
import uuid

# Initialize Razorpay Client
# Use test keys if real ones aren't available yet
KEY_ID = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_YourKeyHere')
KEY_SECRET = getattr(settings, 'RAZORPAY_KEY_SECRET', 'YourSecretHere')

client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))

class CreateOrderView(APIView):
    """
    Creates a Razorpay Order ID for frontend checkout.
    """
    def post(self, request):
        try:
            amount = request.data.get('amount')
            currency = "INR"
            
            if not amount:
                 return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

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
                'key_id': KEY_ID
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
