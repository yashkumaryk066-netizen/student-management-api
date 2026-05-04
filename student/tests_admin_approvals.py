from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from student.models import Student, UserProfile
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

class AdminApprovalsAndSoftDeleteTest(APITestCase):
    def setUp(self):
        # Admin User
        self.admin = User.objects.create_user(username='admin', password='password123')
        self.admin_profile, _ = UserProfile.objects.get_or_create(user=self.admin)
        self.admin_profile.role = 'CLIENT'
        self.admin_profile.save()
        self.admin.refresh_from_db()
        
        # Create Subscription
        from student.models import ClientSubscription
        ClientSubscription.objects.create(
            user=self.admin,
            plan_type='SCHOOL',
            status='ACTIVE',
            end_date=timezone.now().date() + timezone.timedelta(days=30)
        )
        
        # Staff User
        self.staff = User.objects.create_user(username='staff', password='password123')
        self.staff_profile, _ = UserProfile.objects.get_or_create(user=self.staff)
        self.staff_profile.role = 'TEACHER'
        self.staff_profile.save()
        
        from student.models import Employee, Designation
        designation = Designation.objects.create(title="Teacher", created_by=self.admin)
        Employee.objects.create(
            user=self.staff,
            created_by=self.admin,
            designation=designation,
            joining_date="2026-01-01",
            basic_salary=Decimal('25000'),
            contract_type='PERMANENT',
            department=None
        )
        
        self.client.force_authenticate(user=self.admin)

    def test_student_approval_workflow(self):
        """Test that a student created by staff can be approved by admin"""
        # Create unapproved student
        student = Student.objects.create(
            name="Unapproved Student", 
            dob="2000-01-01", 
            gender="MALE", 
            grade=10, 
            relation="SELF",
            is_approved=False,
            created_by=self.admin
        )
        
        # URL for approval
        url = reverse('student-approve', kwargs={'id': student.pk})
        
        response = self.client.post(url, data={'is_approved': True}, format='json')
        
        self.assertEqual(response.status_code, 200)
        student.refresh_from_db()
        self.assertTrue(student.is_approved)

    def test_soft_delete_student(self):
        """Test that soft delete hides student but preserves it in DB"""
        student = Student.objects.create(
            name="Delete Me", 
            dob="2000-01-01", 
            gender="MALE", 
            grade=10, 
            relation="SELF",
            created_by=self.admin
        )
        
        student_id = student.id
        
        # Soft delete
        student.delete() # Default is soft delete in AuditModel -> SoftDeleteModel
        
        # Should not be in objects
        self.assertFalse(Student.objects.filter(id=student_id).exists())
        
        # Should be in all_objects
        self.assertTrue(Student.all_objects.filter(id=student_id).exists())
        
        # Restore
        student.restore()
        self.assertTrue(Student.objects.filter(id=student_id).exists())

    def test_hard_delete_student(self):
        """Test that hard delete removes student permanently"""
        student = Student.objects.create(
            name="Permanent Delete", 
            dob="2000-01-01", 
            gender="MALE", 
            grade=10, 
            relation="SELF",
            created_by=self.admin
        )
        
        student_id = student.id
        student.delete(hard=True)
        
        self.assertFalse(Student.all_objects.filter(id=student_id).exists())
