import json
from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from student.models import ClientSubscription, Payment, UserProfile, Student


@override_settings(SECURE_SSL_REDIRECT=False)
class AdminPaymentApprovalViewTest(TestCase):
    def setUp(self):
        self.super_admin = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='adminpass123',
        )
        self.owner = User.objects.create_user(
            username='owner_user',
            email='owner@example.com',
            password='ownerpass123',
        )
        owner_profile, _ = UserProfile.objects.get_or_create(
            user=self.owner,
            defaults={'role': 'ADMIN', 'institution_type': 'SCHOOL'},
        )
        owner_profile.role = 'ADMIN'
        owner_profile.institution_type = 'SCHOOL'
        owner_profile.save()
        self.client.force_login(self.super_admin)
        self.approve_url = reverse('admin-approve-payment')

    def _create_subscription_payment(self, username, email):
        user = User.objects.create_user(
            username=username,
            email=email,
            password='clientpass123',
        )
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'CLIENT', 'institution_type': 'SCHOOL'},
        )
        profile.role = 'CLIENT'
        profile.institution_type = 'SCHOOL'
        profile.save()
        return Payment.objects.create(
            user=user,
            payment_type='SUBSCRIPTION',
            amount=Decimal('15000.00'),
            due_date=date.today(),
            status='PENDING_VERIFICATION',
            transaction_id=f"TXN-{username}",
            description='Subscription plan payment',
            metadata={'plan_type': 'SCHOOL'},
        )

    def _create_fee_payment(self):
        student = Student.objects.create(
            user=self.owner,
            name='Fee Test Student',
            gender='MALE',
            dob=date(2005, 1, 1),
            grade=10,
            relation='Self',
            email='fee.student@example.com',
            created_by=self.owner,
        )
        return Payment.objects.create(
            student=student,
            payment_type='FEE',
            amount=Decimal('999.00'),
            due_date=date.today(),
            status='PENDING_VERIFICATION',
            transaction_id='FEE-TXN-001',
            description='Fee pending verification',
        )

    def test_subscription_approval_reason_no_email(self):
        payment = self._create_subscription_payment(username='client_no_email', email='')

        response = self.client.post(
            self.approve_url,
            data=json.dumps({'payment_id': payment.id, 'action': 'APPROVE'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'Payment Approved')
        self.assertFalse(data['email_dispatched'])
        self.assertEqual(data['email_dispatched_reason'], 'no_email')

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'APPROVED')
        self.assertTrue(ClientSubscription.objects.filter(user=payment.user, status='ACTIVE').exists())

    @patch('student.services.email_service.send_approval_email', return_value=True)
    @patch('student.services.invoice_service.generate_invoice_pdf', return_value=b'%PDF-1.4 fake')
    def test_subscription_approval_reason_sent(self, mock_generate_invoice_pdf, mock_send_approval_email):
        payment = self._create_subscription_payment(
            username='client_with_email',
            email='client_with_email@example.com',
        )

        response = self.client.post(
            self.approve_url,
            data=json.dumps({'payment_id': payment.id, 'action': 'APPROVE'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['message'], 'Payment Approved')
        self.assertTrue(data['email_dispatched'])
        self.assertEqual(data['email_dispatched_reason'], 'sent')
        self.assertEqual(mock_generate_invoice_pdf.call_count, 1)
        self.assertEqual(mock_send_approval_email.call_count, 1)

    @patch('student.services.email_service.send_approval_email', return_value=True)
    @patch('student.services.invoice_service.generate_invoice_pdf', return_value=b'%PDF-1.4 fake')
    def test_subscription_approval_is_idempotent(self, mock_generate_invoice_pdf, mock_send_approval_email):
        payment = self._create_subscription_payment(
            username='client_idempotent',
            email='client_idempotent@example.com',
        )

        first = self.client.post(
            self.approve_url,
            data=json.dumps({'payment_id': payment.id, 'action': 'APPROVE'}),
            content_type='application/json',
        )
        self.assertEqual(first.status_code, 200)

        sub = ClientSubscription.objects.get(user=payment.user)
        amount_after_first = sub.amount_paid
        end_after_first = sub.end_date

        second = self.client.post(
            self.approve_url,
            data=json.dumps({'payment_id': payment.id, 'action': 'APPROVE'}),
            content_type='application/json',
        )
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json().get('already_processed'))

        sub.refresh_from_db()
        self.assertEqual(sub.amount_paid, amount_after_first)
        self.assertEqual(sub.end_date, end_after_first)
        self.assertEqual(mock_generate_invoice_pdf.call_count, 1)
        self.assertEqual(mock_send_approval_email.call_count, 1)

    def test_approval_invalid_payment_id_returns_400(self):
        response = self.client.post(
            self.approve_url,
            data=json.dumps({'payment_id': 'abc', 'action': 'APPROVE'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get('error'), 'Invalid payment_id')

    def test_payment_update_status_endpoint(self):
        payment = self._create_fee_payment()
        update_url = reverse('payment-update-status', kwargs={'pk': payment.id})

        response = self.client.post(
            update_url,
            data=json.dumps({'status': 'APPROVED'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PAID')
        self.assertIsNotNone(payment.paid_date)

    def test_payment_detail_cross_owner_blocked(self):
        other_owner = User.objects.create_user(
            username='other_owner',
            email='other_owner@example.com',
            password='otherpass123',
        )
        UserProfile.objects.update_or_create(
            user=other_owner,
            defaults={'role': 'ADMIN', 'institution_type': 'SCHOOL'},
        )
        other_student = Student.objects.create(
            user=other_owner,
            name='Other Student',
            gender='MALE',
            dob=date(2004, 1, 1),
            grade=9,
            relation='Self',
            email='other.student@example.com',
            created_by=other_owner,
        )
        other_payment = Payment.objects.create(
            student=other_student,
            payment_type='FEE',
            amount=Decimal('500.00'),
            due_date=date.today(),
            status='PENDING',
            transaction_id='FEE-TXN-OTH-001',
            description='Other owner payment',
        )

        self.client.force_login(self.owner)
        detail_url = reverse('payment-detail', kwargs={'pk': other_payment.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)
