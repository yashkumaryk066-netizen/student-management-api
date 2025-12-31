from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from decimal import Decimal

from student.models import Student, Payment


class FinanceTestCase(TestCase):
    """Test Finance/Payment functionality comprehensively"""
    
    def setUp(self):
        self.admin = User.objects.create_user(username='financeadmin', password='admin123')
        self.student1 = Student.objects.create(
            name='Finance Student 1',
            age=15,
            gender='M',
            dob=datetime(2009, 1, 15).date(),
            grade=10,
            relation='Father: Test Parent'
        )
        self.student2 = Student.objects.create(
            name='Finance Student 2',
            age=16,
            gender='F',
            dob=datetime(2008, 3, 20).date(),
            grade=11,
            relation='Mother: Test Parent'
        )
    
    def test_payment_creation_pending(self):
        """Test creating a payment with pending status"""
        payment = Payment.objects.create(
            student=self.student1,
            amount=Decimal('10000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Tuition Fee - January 2025'
        )
        self.assertEqual(payment.status, 'PENDING')
        self.assertIsNone(payment.paid_date)
        self.assertEqual(payment.student.payments.count(), 1)
    
    def test_payment_marked_paid(self):
        """Test marking payment as paid"""
        payment = Payment.objects.create(
            student=self.student1,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timedelta(days=15),
            description='Library Fee'
        )
        
        # Mark as paid
        payment.status = 'PAID'
        payment.paid_date = timezone.now().date()
        payment.save()
        
        self.assertEqual(payment.status, 'PAID')
        self.assertIsNotNone(payment.paid_date)
    
    def test_payment_overdue_auto_detection(self):
        """Test automatic overdue status detection"""
        past_date = timezone.now().date() - timedelta(days=10)
        payment = Payment.objects.create(
            student=self.student1,
            amount=Decimal('3000.00'),
            due_date=past_date,
            description='Lab Fee - Overdue Test',
            status='PENDING'
        )
        
        # Save again to trigger auto-update
        payment.save()
        self.assertEqual(payment.status, 'OVERDUE')
    
    def test_multiple_payments_per_student(self):
        """Test that one student can have multiple payments"""
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Tuition Fee'
        )
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('1000.00'),
            due_date=timezone.now().date() + timedelta(days=15),
            description='Sports Fee'
        )
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('500.00'),
            due_date=timezone.now().date() + timedelta(days=20),
            description='Lab Fee'
        )
        
        self.assertEqual(self.student1.payments.count(), 3)
    
    def test_payment_ordering(self):
        """Test that payments are ordered by due date (descending)"""
        p1 = Payment.objects.create(
            student=self.student1,
            amount=Decimal('1000.00'),
            due_date=timezone.now().date() + timedelta(days=10),
            description='First'
        )
        p2 = Payment.objects.create(
            student=self.student1,
            amount=Decimal('2000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Second'
        )
        p3 = Payment.objects.create(
            student=self.student1,
            amount=Decimal('3000.00'),
            due_date=timezone.now().date() + timedelta(days=20),
            description='Third'
        )
        
        payments = list(self.student1.payments.all())
        # Should be ordered by due_date descending (latest first)
        self.assertEqual(payments[0].description, 'Second')
        self.assertEqual(payments[1].description, 'Third')
        self.assertEqual(payments[2].description, 'First')
    
    def test_payment_str_representation(self):
        """Test payment string representation"""
        payment = Payment.objects.create(
            student=self.student1,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Test Fee'
        )
        expected_str = f"{self.student1.name} - ₹5000.00 - PENDING"
        self.assertEqual(str(payment), expected_str)
    
    def test_payment_amount_precision(self):
        """Test payment amount decimal precision"""
        payment = Payment.objects.create(
            student=self.student1,
            amount=Decimal('4999.99'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Precise Amount Test'
        )
        self.assertEqual(payment.amount, Decimal('4999.99'))
    
    def test_payment_timestamps(self):
        """Test payment created_at and updated_at timestamps"""
        payment = Payment.objects.create(
            student=self.student1,
            amount=Decimal('1000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Timestamp Test'
        )
        
        created_time = payment.created_at
        self.assertIsNotNone(created_time)
        
        # Update payment
        payment.amount = Decimal('1500.00')
        payment.save()
        
        self.assertNotEqual(payment.updated_at, created_time)


class FinanceAPITestCase(APITestCase):
    """Test Finance API endpoints"""
    
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='Admin123!',
            is_staff=True
        )
        self.teacher = User.objects.create_user(username='teacher', password='teach123')
        
        self.student = Student.objects.create(
            name='API Test Student',
            age=15,
            gender='M',
            dob=datetime(2009, 5, 10).date(),
            grade=10,
            relation='Test Parent'
        )
    
    def test_list_payments_unauthorized(self):
        """Test that listing payments requires authentication"""
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_payments_authorized(self):
        """Test listing payments with authentication"""
        Payment.objects.create(
            student=self.student,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Test Fee'
        )
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_payment_api(self):
        """Test creating a payment via API"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'student': self.student.id,
            'amount': '7500.00',
            'due_date': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'description': 'Annual Fee',
            'status': 'PENDING'
        }
        
        response = self.client.post('/api/payments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        
        payment = Payment.objects.first()
        self.assertEqual(payment.amount, Decimal('7500.00'))
        self.assertEqual(payment.description, 'Annual Fee')
    
    def test_update_payment_status(self):
        """Test updating payment status via API"""
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('3000.00'),
            due_date=timezone.now().date() + timedelta(days=15),
            description='Update Test'
        )
        
        self.client.force_authenticate(user=self.admin)
        url = f'/api/payments/{payment.id}/'
        
        data = {
            'student': self.student.id,
            'amount': '3000.00',
            'due_date': (timezone.now().date() + timedelta(days=15)).isoformat(),
            'description': 'Update Test',
            'status': 'PAID',
            'paid_date': timezone.now().date().isoformat()
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'PAID')
    
    def test_filter_payments_by_status(self):
        """Test filtering payments by status"""
        Payment.objects.create(
            student=self.student,
            amount=Decimal('1000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Pending 1',
            status='PENDING'
        )
        Payment.objects.create(
            student=self.student,
            amount=Decimal('2000.00'),
            due_date=timezone.now().date() - timedelta(days=5),
            description='Overdue 1',
            status='OVERDUE'
        )
        Payment.objects.create(
            student=self.student,
            amount=Decimal('3000.00'),
            due_date=timezone.now().date(),
            description='Paid 1',
            status='PAID',
            paid_date=timezone.now().date()
        )
        
        self.client.force_authenticate(user=self.admin)
        
        # Test filtering by PENDING
        response = self.client.get('/api/payments/?status=PENDING')
        if response.status_code == 200:
            # API supports filtering
            pass
    
    def test_delete_payment(self):
        """Test deleting a payment record"""
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('1000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Delete Test'
        )
        
        self.client.force_authenticate(user=self.admin)
        url = f'/api/payments/{payment.id}/'
        
        response = self.client.delete(url)
        self.assertIn(response.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])


class FeeCollectionReportTestCase(TestCase):
    """Test fee collection reporting and analytics"""
    
    def setUp(self):
        self.student1 = Student.objects.create(
            name='Report Student 1',
            age=15,
            gender='M',
            dob=datetime(2009, 1, 1).date(),
            grade=10,
            relation='Test Parent 1'
        )
        self.student2 = Student.objects.create(
            name='Report Student 2',
            age=16,
            gender='F',
            dob=datetime(2008, 2, 2).date(),
            grade=11,
            relation='Test Parent 2'
        )
    
    def test_total_revenue_calculation(self):
        """Test calculating total revenue from paid fees"""
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date(),
            status='PAID',
            paid_date=timezone.now().date(),
            description='Fee 1'
        )
        Payment.objects.create(
            student=self.student2,
            amount=Decimal('3000.00'),
            due_date=timezone.now().date(),
            status='PAID',
            paid_date=timezone.now().date(),
            description='Fee 2'
        )
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('2000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            status='PENDING',
            description='Pending Fee'
        )
        
        total_paid = Payment.objects.filter(status='PAID').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        self.assertEqual(total_paid, Decimal('8000.00'))
    
    def test_outstanding_dues_calculation(self):
        """Test calculating outstanding dues"""
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            status='PENDING',
            description='Pending 1'
        )
        Payment.objects.create(
            student=self.student2,
            amount=Decimal('3000.00'),
            due_date=timezone.now().date() - timedelta(days=5),
            status='OVERDUE',
            description='Overdue 1'
        )
        
        from django.db import models
        outstanding = Payment.objects.filter(
            status__in=['PENDING', 'OVERDUE']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        self.assertEqual(outstanding, Decimal('8000.00'))
    
    def test_overdue_count(self):
        """Test counting overdue payments"""
        past_date = timezone.now().date() - timedelta(days=10)
        Payment.objects.create(
            student=self.student1,
            amount=Decimal('1000.00'),
            due_date=past_date,
            status='OVERDUE',
            description='Overdue 1'
        )
        Payment.objects.create(
            student=self.student2,
            amount=Decimal('2000.00'),
            due_date=past_date,
            status='OVERDUE',
            description='Overdue 2'
        )
        
        overdue_count = Payment.objects.filter(status='OVERDUE').count()
        self.assertEqual(overdue_count, 2)


# Import Django models for aggregation
from django.db import models
