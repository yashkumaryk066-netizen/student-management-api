from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from student.models import Student, UserProfile, Payment
from django.urls import reverse
import json
from datetime import date
from unittest.mock import patch

@override_settings(SECURE_SSL_REDIRECT=False)
class EazypayIntegrationTest(TestCase):
    def setUp(self):
        # Create a user and student profile
        self.user = User.objects.create_user(username='teststudent', password='password123')
        self.profile = UserProfile.objects.create(user=self.user, role='STUDENT')
        self.student = Student.objects.create(
            user=self.user,
            name='Test Student',
            age=20,
            gender='Male',
            dob=date(2000, 1, 1),
            grade=12,
            relation='Self'
        )
        self.client = Client()
        self.init_url = reverse('payment-eazypay-init')
        self.callback_url = reverse('payment-eazypay-callback')

    def test_init_payment_unauthenticated(self):
        """Test that unauthenticated users cannot initiate payment"""
        response = self.client.post(self.init_url, {'amount': '100.00'})
        self.assertEqual(response.status_code, 401)

    def test_init_payment_success(self):
        """Test successful payment initiation"""
        self.client.force_login(self.user)
        data = {
            'amount': '500.00',
            'description': 'Test Fee'
        }
        response = self.client.post(self.init_url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # Check response structure
        self.assertIn('transaction_id', response_data)
        self.assertIn('payment_url', response_data)
        self.assertEqual(response_data['status'], 'INITIATED')
        
        # Verify DB record created
        self.assertTrue(Payment.objects.filter(transaction_id=response_data['transaction_id']).exists())
        payment = Payment.objects.get(transaction_id=response_data['transaction_id'])
        self.assertEqual(float(payment.amount), 500.00)
        self.assertEqual(payment.description, 'Test Fee')

    def test_callback_success(self):
        """Test successful payment callback"""
        # Create a pending payment
        txn_id = 'test_txn_12345'
        payment = Payment.objects.create(
            student=self.student,
            transaction_id=txn_id,
            amount=1000.00,
            due_date=date.today(),
            status='PENDING',
            description='Pending Fee'
        )
        
        # Simulate Eazypay callback payload
        # Note: In real world, this payload is form-data or JSON depending on config, 
        # but our view handles `request.data` which works for both in DRF if parsers are right.
        # Standard Eazypay often sends Form Data.
        
        callback_data = {
            'Response_Code': 'E000',
            'ReferenceNo': txn_id,
            'Unique_Ref_Number': 'BANK123456',
            'Service_Tax_Amount': '0',
            'Processing_Fee_Amount': '0',
            'Total_Amount': '1000.00',
            'Transaction_Amount': '1000.00',
            'Transaction_Date': '2023-01-01',
            'Interchange_Value': '',
            'TDR': '',
            'Payment_Mode': 'NetBanking',
            'SubMerchantId': '1234',
            'ReferenceNo': txn_id,
            'ID': '123',
            'RS': 'hash_value_here',
            'TPS': 'Y',
        }
        
        response = self.client.post(self.callback_url, callback_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'SUCCESS')
        
        # Verify DB updated
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PAID')
        self.assertIn('BANK123456', payment.description)

    def test_callback_failure(self):
        """Test failed payment callback"""
        txn_id = 'fail_txn_12345'
        payment = Payment.objects.create(
            student=self.student,
            transaction_id=txn_id,
            amount=1000.00,
            due_date=date.today(),
            status='PENDING'
        )
        
        callback_data = {
            'Response_Code': 'E001', # Failed code
            'ReferenceNo': txn_id,
        }
        
        response = self.client.post(self.callback_url, callback_data)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'FAILED')

    def test_callback_invalid_txn(self):
        """Test callback with non-existent transaction"""
        callback_data = {
            'Response_Code': 'E000',
            'ReferenceNo': 'invalid_txn_id',
        }
        response = self.client.post(self.callback_url, callback_data)
        self.assertEqual(response.status_code, 404)
