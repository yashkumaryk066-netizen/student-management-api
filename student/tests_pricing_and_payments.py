from rest_framework.test import APITestCase
from django.urls import reverse
from decimal import Decimal
from student.plan_permissions import PLAN_PRICING, calculate_total_price
from unittest.mock import patch, MagicMock

class PricingAndPaymentsTest(APITestCase):
    def test_pricing_calculations(self):
        """Verify that plan pricing correctly includes platform fee and GST"""
        # Coaching: 500 + 3 = 503. GST(5%) = 25.15. Total = 528.15
        self.assertEqual(PLAN_PRICING['COACHING'], Decimal('528.15'))
        
        # School: 1500 + 3 = 1503. GST(5%) = 75.15. Total = 1578.15
        self.assertEqual(PLAN_PRICING['SCHOOL'], Decimal('1578.15'))
        
        # Institute: 5000 + 3 = 5003. GST(5%) = 250.15. Total = 5253.15
        self.assertEqual(PLAN_PRICING['INSTITUTE'], Decimal('5253.15'))

    def test_razorpay_order_creation_amount_override(self):
        """Verify that Razorpay order creation overrides any provided amount with official plan pricing"""
        url = reverse('razorpay-create-order')
        
        # Scenario: User tries to pay 1 Rupee for a COACHING plan
        data = {
            "amount": 1,
            "payment_type": "SUBSCRIPTION",
            "plan_type": "COACHING",
            "email": "test@example.com"
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
        # Expected amount in paise: 528.15 * 100 = 52815
        self.assertEqual(response.data['amount'], 52815)

    def test_razorpay_order_creation_school(self):
        """Verify amount for School plan"""
        url = reverse('razorpay-create-order')
        data = {
            "amount": 10,
            "payment_type": "SUBSCRIPTION",
            "plan_type": "SCHOOL"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        # 1578.15 * 100 = 157815
        self.assertEqual(response.data['amount'], 157815)

    @patch('razorpay.Client')
    def test_credentials_returned_after_payment(self, mock_razorpay):
        """Verify that new user credentials are returned after successful payment verification"""
        from student.models import UserProfile
        from django.contrib.auth.models import User
        
        url = reverse('razorpay-verify')
        data = {
            "razorpay_order_id": "order_123",
            "razorpay_payment_id": "pay_123",
            "razorpay_signature": "sig_123",
            "amount": 528.15,
            "payment_type": "SUBSCRIPTION",
            "plan_type": "COACHING",
            "email": "newuser@example.com",
            "institution_name": "New Coaching"
        }
        
        # Mock signature verification success
        mock_razorpay.return_value.utility.verify_payment_signature.return_value = True
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_new_user'])
        self.assertIn('credentials', response.data)
        self.assertIsNotNone(response.data['credentials']['username'])
        self.assertIsNotNone(response.data['credentials']['password'])
        self.assertTrue(response.data['credentials']['must_change_password'])
        
        # Verify user was created in DB
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())
