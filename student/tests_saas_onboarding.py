from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from student.models import ClientSubscription, UserProfile, Payment
from unittest.mock import patch
import json
from datetime import date, timedelta

class SaaSOnboardingTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('razorpay-verify')
        self.onboarding_email = "new_onboarding@test.com"
        
    @patch('student.views.payment_gateway.razorpay.Client')
    def test_new_user_onboarding_success(self, mock_client_class):
        """Test that a successful Razorpay verification creates a new user and subscription"""
        # Mock the instance returned by razorpay.Client()
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.utility.verify_payment_signature.return_value = True 
        
        payload = {
            "razorpay_order_id": "order_new_123",
            "razorpay_payment_id": "pay_new_123",
            "razorpay_signature": "sig_new_123",
            "plan_type": "SCHOOL",
            "amount": 4800,
            "email": self.onboarding_email,
            "institution_name": "Test Academy",
            "payment_type": "SUBSCRIPTION"
        }
        
        response = self.client.post(
            self.verify_url, 
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.json()['status'], 'success')
        
        # Verify User creation
        user = User.objects.filter(email=self.onboarding_email).first()
        self.assertIsNotNone(user)
        
        # Verify Profile and Password Flag
        profile = UserProfile.objects.get(user=user)
        self.assertTrue(profile.force_password_change)
        self.assertEqual(profile.institution_name, "Test Academy")
        self.assertEqual(profile.institution_type, "SCHOOL")
        
        # Verify Subscription
        sub = ClientSubscription.objects.get(user=user)
        self.assertEqual(sub.status, 'ACTIVE')
        self.assertEqual(sub.plan_type, 'SCHOOL')
        self.assertEqual(sub.end_date, date.today() + timedelta(days=30))
        
        # Verify Credentials returned
        creds = response.json().get('credentials')
        self.assertIsNotNone(creds)
        self.assertEqual(creds['username'], user.username)
        self.assertIn('password', creds)

    @patch('student.views.payment_gateway.razorpay.Client')
    def test_existing_user_renewal(self, mock_client_class):
        """Test that an existing user can renew their subscription"""
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.utility.verify_payment_signature.return_value = True
        
        # Setup existing user
        user = User.objects.create_user(username='existing_user', email='existing@test.com')
        # Profile is created by signal, so we get it and update it
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'ADMIN'
        profile.save()

        sub = ClientSubscription.objects.create(
            user=user, 
            plan_type='COACHING', 
            status='ACTIVE',
            end_date=date.today() + timedelta(days=5)
        )
        
        self.client.force_authenticate(user=user)
        
        payload = {
            "razorpay_order_id": "order_renew_123",
            "razorpay_payment_id": "pay_renew_123",
            "razorpay_signature": "sig_renew_123",
            "plan_type": "COACHING",
            "amount": 2400,
            "payment_type": "RENEWAL"
        }
        
        response = self.client.post(
            self.verify_url, 
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200, response.data)
        
        sub.refresh_from_db()
        # Should be original 5 days + 30 days
        self.assertEqual(sub.end_date, date.today() + timedelta(days=35))
        self.assertEqual(sub.status, 'ACTIVE')

    @patch('student.views.payment_gateway.razorpay.Client')
    def test_tier_upgrade(self, mock_client_class):
        """Test upgrading from COACHING to SCHOOL"""
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.utility.verify_payment_signature.return_value = True
        
        user = User.objects.create_user(username='upgrade_user', email='upgrade@test.com')
        # Profile created by signal
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'ADMIN'
        profile.institution_type = 'COACHING'
        profile.save()
        
        ClientSubscription.objects.create(user=user, plan_type='COACHING', status='ACTIVE')
        
        self.client.force_authenticate(user=user)
        
        payload = {
            "razorpay_order_id": "order_up_123",
            "razorpay_payment_id": "pay_up_123",
            "razorpay_signature": "sig_up_123",
            "plan_type": "SCHOOL",
            "amount": 4800,
            "payment_type": "UPGRADE"
        }
        
        response = self.client.post(
            self.verify_url, 
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, 200, response.data)
        
        sub = ClientSubscription.objects.get(user=user)
        self.assertEqual(sub.plan_type, 'SCHOOL')
        
        profile.refresh_from_db()
        self.assertEqual(profile.institution_type, 'SCHOOL')
