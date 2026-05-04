from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from student.models import Employee, UserProfile, ClientSubscription, Designation, HRDepartment, LeaveRequest, Payroll
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

class HRPayrollTest(APITestCase):
    def setUp(self):
        # Setup Owner (Client)
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.profile, _ = UserProfile.objects.get_or_create(user=self.owner)
        self.profile.role = 'CLIENT'
        self.profile.institution_type = 'INSTITUTE'
        self.profile.save()
        self.owner.refresh_from_db()
        
        ClientSubscription.objects.create(
            user=self.owner,
            plan_type='INSTITUTE',
            status='ACTIVE',
            end_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        
        # Setup Designation and Dept
        self.designation = Designation.objects.create(title="Teacher", created_by=self.owner)
        self.dept = HRDepartment.objects.create(name="Science", created_by=self.owner)
        
        self.client.force_authenticate(user=self.owner)

    def test_add_staff_member(self):
        """Test that Account Owner can add a new team member via TeamManagementView"""
        url = reverse('team-manage')
        data = {
            "username": "new_staff",
            "password": "password123",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role": "TEACHER",
            "designation_id": self.designation.id,
            "department_id": self.dept.id,
            "basic_salary": 30000,
            "contract_type": "PERMANENT"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="new_staff").exists())
        self.assertTrue(Employee.objects.filter(user__username="new_staff").exists())

    def test_leave_request_workflow(self):
        """Test staff applying for leave and admin visibility"""
        # Create a staff user first
        staff_user = User.objects.create_user(username='staff1', password='password123')
        UserProfile.objects.update_or_create(user=staff_user, defaults={'role': 'TEACHER', 'institution_type': 'SCHOOL'})
        employee = Employee.objects.create(
            user=staff_user,
            created_by=self.owner,
            designation=self.designation,
            joining_date=timezone.now().date(),
            basic_salary=Decimal('25000'),
            contract_type='PERMANENT'
        )
        
        # Apply for leave
        self.client.force_authenticate(user=staff_user)
        url = reverse('leave-requests-alias')
        data = {
            "employee": employee.id,
            "leave_type": "SICK",
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date() + timezone.timedelta(days=2),
            "reason": "Fever",
            "status": "PENDING"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Admin checks leave requests
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Fever", str(response.data))

    def test_payroll_visibility(self):
        """Test that payroll records are visible to admin"""
        staff_user = User.objects.create_user(username='staff2', password='password123')
        employee = Employee.objects.create(
            user=staff_user,
            created_by=self.owner,
            designation=self.designation,
            joining_date=timezone.now().date(),
            basic_salary=Decimal('25000'),
            contract_type='PERMANENT'
        )
        
        Payroll.objects.create(
            employee=employee,
            month="June",
            year=2026,
            basic_salary=Decimal('25000'),
            net_salary=Decimal('25000'),
            status='PAID',
            payment_date=timezone.now().date(),
            created_by=self.owner
        )
        
        url = reverse('payroll-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("25000", str(response.data))
