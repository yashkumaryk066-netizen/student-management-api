import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

key_id = os.getenv('RAZORPAY_KEY_ID')
key_secret = os.getenv('RAZORPAY_KEY_SECRET')

print(f"Testing with Key ID: {key_id}")

try:
    client = razorpay.Client(auth=(key_id, key_secret))
    # Try a simple fetch to verify credentials
    orders = client.order.all({'count': 1})
    print("SUCCESS: Razorpay Authentication Successful!")
except Exception as e:
    print(f"FAILURE: Razorpay Authentication Failed: {str(e)}")
