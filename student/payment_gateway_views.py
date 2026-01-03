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

            # Check if keys are configured. If not, return a MOCK order for testing flow.
            # Real keys would start with 'rzp_live' or 'rzp_test' and not be the placeholder 'YourKeyHere'
            if 'YourKeyHere' in KEY_ID or len(KEY_ID) < 10:
                # MOCK MODE
                return Response({
                    'mock_order': True,
                    'order_id': f"order_mock_{uuid.uuid4().hex[:10]}",
                    'amount': int(amount) * 100,
                    'currency': currency,
                    'key_id': 'mock_key'
                }, status=status.HTTP_201_CREATED)

            # REAL RAZORPAY MODE
            # Razorpay expects amount in paise (1 INR = 100 paise)
            data = {
                "amount": int(amount) * 100,
                "currency": currency,
                "payment_capture": "1", # Auto capture
                "receipt": str(uuid.uuid4())
            }
            
            order = client.order.create(data=data)
            
            return Response({
                'mock_order': False,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': KEY_ID
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Fallback to mock if Razorpay connection fails strictly for demo continuity
            print(f"Razorpay Error: {e}, falling back to mock.")
            return Response({
                    'mock_order': True,
                    'order_id': f"order_mock_{uuid.uuid4().hex[:10]}",
                    'amount': int(request.data.get('amount', 500)) * 100,
                    'currency': "INR",
                    'key_id': 'mock_key_fallback'
            }, status=status.HTTP_201_CREATED)
