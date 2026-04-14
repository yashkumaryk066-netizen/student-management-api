from datetime import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from student.models import Payment, Student, UserProfile


class SuperAdminDashboardIntegrationTestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_user(
            username='root_admin',
            password='Super123!',
            is_staff=True,
            is_superuser=True,
        )
        super_profile = UserProfile.objects.get(user=self.superuser)
        super_profile.role = 'ADMIN'
        super_profile.save()

        self.client_user = User.objects.create_user(
            username='client_owner',
            password='Client123!',
            email='client@example.com',
        )
        client_profile = UserProfile.objects.get(user=self.client_user)
        client_profile.role = 'CLIENT'
        client_profile.institution_name = 'Alpha Academy'
        client_profile.institution_type = 'SCHOOL'
        client_profile.subscription_expiry = timezone.now().date() + timezone.timedelta(days=30)
        client_profile.save()

        self.pending_payment = Payment.objects.create(
            user=self.client_user,
            payment_type='SUBSCRIPTION',
            amount='2000.00',
            due_date=timezone.now().date(),
            status='PENDING_VERIFICATION',
            description='Subscription Renewal',
            transaction_id='SUB-12345',
        )

        self.pending_student = Student.objects.create(
            name='Pending Student',
            gender='MALE',
            dob=datetime(2010, 1, 1).date(),
            grade=8,
            relation='Father: Client Owner',
            email='pending.student@example.com',
            created_by=self.client_user,
            institution_type='SCHOOL',
            is_approved=False,
        )

        self.client.force_authenticate(user=self.superuser)

    def test_advanced_dashboard_returns_pending_approvals(self):
        response = self.client.get('/api/admin/advanced/dashboard/', secure=True, HTTP_HOST='localhost')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['stats']['students'], 1)
        self.assertTrue(any(
            item['type'] == 'SUBSCRIPTION' and item['id'] == self.pending_payment.id
            for item in response.data['approvals']
        ))
        self.assertTrue(any(
            item['type'] == 'STUDENT' and item['id'] == self.pending_student.id
            for item in response.data['approvals']
        ))


class StudentApprovalIntegrationTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='tenant_admin',
            password='Admin123!',
            is_staff=True,
            is_superuser=True,
        )
        profile = UserProfile.objects.get(user=self.admin)
        profile.role = 'ADMIN'
        profile.institution_type = 'SCHOOL'
        profile.subscription_expiry = timezone.now().date() + timezone.timedelta(days=365)
        profile.save()

        self.pending_student = Student.objects.create(
            name='Needs Approval',
            gender='FEMALE',
            dob=datetime(2011, 5, 15).date(),
            grade=7,
            relation='Mother: Example',
            email='needs.approval@example.com',
            created_by=self.admin,
            institution_type='SCHOOL',
            is_approved=False,
        )
        Student.objects.create(
            name='Approved Student',
            gender='MALE',
            dob=datetime(2010, 7, 20).date(),
            grade=9,
            relation='Father: Example',
            email='approved.student@example.com',
            created_by=self.admin,
            institution_type='SCHOOL',
            is_approved=True,
        )

        self.client.force_authenticate(user=self.admin)

    def test_student_list_can_filter_pending_approvals(self):
        response = self.client.get('/api/students/?is_approved=False', secure=True, HTTP_HOST='localhost')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = {student['id'] for student in response.data}
        self.assertEqual(returned_ids, {self.pending_student.id})

    def test_pending_student_can_be_approved_via_compat_endpoint(self):
        response = self.client.post(
            f'/api/students/{self.pending_student.id}/approve/',
            secure=True,
            HTTP_HOST='localhost'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_student.refresh_from_db()
        self.assertTrue(self.pending_student.is_approved)
