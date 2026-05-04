from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from student.models import Student, Payment, InstitutionExpense, Grade, UserProfile
from django.urls import reverse
from decimal import Decimal

class ROIAnalyticsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='password123')
        # Profile created by signal
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.role = 'ADMIN'
        self.profile.save()
        
        self.client.force_authenticate(user=self.user)
        self.roi_url = reverse('analytics-roi')
        
        # Create some students
        self.student1 = Student.objects.create(
            name="Good Student", roll_number="S1", dob="2000-01-01", 
            gender="MALE", grade=10, relation="SELF", created_by=self.user
        )
        self.student2 = Student.objects.create(
            name="At Risk Student", roll_number="S2", dob="2000-01-01", 
            gender="FEMALE", grade=10, relation="SELF", created_by=self.user
        )
        
        # Create Payments (Income)
        Payment.objects.create(student=self.student1, amount=Decimal('5000'), status='PAID', due_date="2026-01-01")
        
        # Create Expenses
        InstitutionExpense.objects.create(
            expense_type='RENT',
            amount=Decimal('2000'),
            created_by=self.user
        )
        
        # Create Exam
        from student.models import Exam
        self.exam = Exam.objects.create(
            name="Final Exam", exam_type="FINAL", total_marks=100, 
            passing_marks=40, exam_date="2026-01-01", created_by=self.user
        )
        
        # Create Grades
        Grade.objects.create(student=self.student1, exam=self.exam, marks_obtained=90, status='PASS')
        Grade.objects.create(student=self.student2, exam=self.exam, marks_obtained=30, status='FAIL')

    def test_roi_calculation(self):
        """Test that ROI and Risk analytics are calculated correctly"""
        response = self.client.get(self.roi_url)
        
        self.assertEqual(response.status_code, 200)
        data = response.data
        
        # Finance
        self.assertEqual(data['finance']['total_revenue'], 5000.0)
        self.assertEqual(data['finance']['total_expenses'], 2000.0)
        self.assertEqual(data['finance']['net_profit'], 3000.0)
        
        # Academic Risk
        # student2 has 30 marks (< 40), so they should be in the list
        self.assertEqual(len(data['academic_risk']), 1)
        self.assertEqual(data['academic_risk'][0]['student_name'], "At Risk Student")
        
        # Academic Health
        self.assertEqual(data['academic_health']['at_risk_count'], 1)
        self.assertEqual(data['academic_health']['success_ratio'], 50.0) # 1 of 2 students is at risk
