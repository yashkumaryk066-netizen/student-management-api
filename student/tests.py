from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Subject, Classroom, Exam, Grade, LibraryBook, BookIssue
)


class StudentModelTestCase(TestCase):
    """Test Student model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='parent1', password='test123')
        self.student = Student.objects.create(
            name='John Doe',
            age=15,
            gender='M',
            dob=datetime(2009, 1, 15).date(),
            grade=10,
            relation='Father: Mike Doe',
            parent=self.user
        )
    
    def test_student_creation(self):
        """Test creating a student"""
        self.assertEqual(self.student.name, 'John Doe')
        self.assertEqual(self.student.age, 15)
        self.assertEqual(self.student.grade, 10)
        self.assertEqual(str(self.student), 'John Doe')
    
    def test_student_parent_relation(self):
        """Test student-parent relationship"""
        self.assertEqual(self.student.parent, self.user)
        self.assertEqual(self.user.children.count(), 1)


class AttendanceTestCase(TestCase):
    """Test Attendance functionality"""
    
    def setUp(self):
        self.student = Student.objects.create(
            name='Jane Smith',
            age=16,
            gender='F',
            dob=datetime(2008, 5, 20).date(),
            grade=11,
            relation='Mother: Mary Smith'
        )
    
    def test_attendance_marking(self):
        """Test marking attendance"""
        today = timezone.now().date()
        attendance = Attendence.objects.create(
            student=self.student,
            date=today,
            is_present=True
        )
        self.assertTrue(attendance.is_present)
        self.assertEqual(attendance.student, self.student)
    
    def test_unique_attendance_per_day(self):
        """Test that only one attendance record per student per day"""
        today = timezone.now().date()
        Attendence.objects.create(student=self.student, date=today, is_present=True)
        
        # Try creating duplicate - should raise error
        with self.assertRaises(Exception):
            Attendence.objects.create(student=self.student, date=today, is_present=False)
    
    def test_attendance_history(self):
        """Test attendance history across multiple days"""
        for i in range(5):
            date = timezone.now().date() - timedelta(days=i)
            Attendence.objects.create(
                student=self.student,
                date=date,
                is_present=i % 2 == 0  # Alternate present/absent
            )
        
        total_records = Attendence.objects.filter(student=self.student).count()
        self.assertEqual(total_records, 5)


class PaymentTestCase(TestCase):
    """Test Payment/Fee functionality"""
    
    def setUp(self):
        self.student = Student.objects.create(
            name='Alex Johnson',
            age=14,
            gender='M',
            dob=datetime(2010, 3, 10).date(),
            grade=9,
            relation='Father: Bob Johnson'
        )
    
    def test_payment_creation(self):
        """Test creating a payment record"""
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('5000.00'),
            due_date=timezone.now().date() + timedelta(days=30),
            description='Tuition Fee - January 2025',
            status='PENDING'
        )
        self.assertEqual(payment.amount, Decimal('5000.00'))
        self.assertEqual(payment.status, 'PENDING')
    
    def test_overdue_payment_auto_status(self):
        """Test that overdue payments get auto-marked"""
        # Create payment with past due date
        past_date = timezone.now().date() - timedelta(days=5)
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('3000.00'),
            due_date=past_date,
            description='Late Fee Test',
            status='PENDING'
        )
        # Save again to trigger auto-status update
        payment.save()
        self.assertEqual(payment.status, 'OVERDUE')
    
    def test_paid_payment(self):
        """Test marking payment as paid"""
        payment = Payment.objects.create(
            student=self.student,
            amount=Decimal('2000.00'),
            due_date=timezone.now().date() + timedelta(days=10),
            description='Lab Fee'
        )
        payment.status = 'PAID'
        payment.paid_date = timezone.now().date()
        payment.save()
        
        self.assertEqual(payment.status, 'PAID')
        self.assertIsNotNone(payment.paid_date)


class StudentAPITestCase(APITestCase):
    """Test Student API endpoints"""
    
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_user(username='admin', password='Admin123!')
        self.admin.is_staff = True
        self.admin.save()
        
        # Create test students
        self.student1 = Student.objects.create(
            name='Test Student 1',
            age=15,
            gender='M',
            dob=datetime(2009, 1, 1).date(),
            grade=10,
            relation='Father: Test Parent'
        )
    
    def test_list_students_unauthorized(self):
        """Test that listing students requires authentication"""
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_students_authorized(self):
        """Test listing students with authentication"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_student(self):
        """Test creating a student via API"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'New Student',
            'age': 14,
            'gender': 'F',
            'dob': '2010-05-15',
            'grade': 9,
            'relation': 'Mother: Jane Doe'
        }
        response = self.client.post('/api/students/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 2)
    
    def test_update_student(self):
        """Test updating student information"""
        self.client.force_authenticate(user=self.admin)
        url = f'/api/students/{self.student1.id}/'
        data = {
            'name': 'Updated Name',
            'age': 16,
            'gender': 'M',
            'dob': '2009-01-01',
            'grade': 11,
            'relation': 'Updated Relation'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.student1.refresh_from_db()
        self.assertEqual(self.student1.name, 'Updated Name')
        self.assertEqual(self.student1.grade, 11)
    
    def test_delete_student(self):
        """Test deleting a student"""
        self.client.force_authenticate(user=self.admin)
        url = f'/api/students/{self.student1.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Student.objects.count(), 0)


class AttendanceAPITestCase(APITestCase):
    """Test Attendance API endpoints"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher1', password='teach123')
        self.student = Student.objects.create(
            name='Student Test',
            age=15,
            gender='M',
            dob=datetime(2009, 6, 10).date(),
            grade=10,
            relation='Test Parent'
        )
    
    def test_mark_attendance(self):
        """Test marking attendance via API"""
        self.client.force_authenticate(user=self.teacher)
        data = {
            'student': self.student.id,
            'date': timezone.now().date().isoformat(),
            'is_present': True
        }
        response = self.client.post('/api/attendence/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_attendance(self):
        """Test listing attendance records"""
        Attendence.objects.create(
            student=self.student,
            date=timezone.now().date(),
            is_present=True
        )
        
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/attendence/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PaymentAPITestCase(APITestCase):
    """Test Payment API endpoints"""
    
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='Admin123!')
        self.student = Student.objects.create(
            name='Payment Test Student',
            age=16,
            gender='F',
            dob=datetime(2008, 8, 20).date(),
            grade=11,
            relation='Test Parent'
        )
    
    def test_create_payment(self):
        """Test creating a payment record"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'student': self.student.id,
            'amount': '5000.00',
            'due_date': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'description': 'Tuition Fee',
            'status': 'PENDING'
        }
        response = self.client.post('/api/payments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExamGradeTestCase(TestCase):
    """Test Exam and Grade functionality"""
    
    def setUp(self):
        self.subject = Subject.objects.create(
            name='Mathematics',
            code='MATH101',
            credits=4
        )
        self.student = Student.objects.create(
            name='Exam Student',
            age=15,
            gender='M',
            dob=datetime(2009, 4, 15).date(),
            grade=10,
            relation='Test Parent'
        )
        self.exam = Exam.objects.create(
            name='Mid-Term Exam',
            exam_type='MIDTERM',
            subject=self.subject,
            grade_class='10',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date(),
            duration_minutes=180
        )
    
    def test_exam_creation(self):
        """Test creating an exam"""
        self.assertEqual(self.exam.name, 'Mid-Term Exam')
        self.assertEqual(self.exam.total_marks, 100)
    
    def test_grade_pass(self):
        """Test passing grade"""
        grade = Grade.objects.create(
            student=self.student,
            exam=self.exam,
            marks_obtained=Decimal('75.00')
        )
        self.assertEqual(grade.status, 'PASS')
        self.assertEqual(grade.percentage, 75.0)
    
    def test_grade_fail(self):
        """Test failing grade"""
        grade = Grade.objects.create(
            student=self.student,
            exam=self.exam,
            marks_obtained=Decimal('35.00')
        )
        self.assertEqual(grade.status, 'FAIL')


class LibraryTestCase(TestCase):
    """Test Library management"""
    
    def setUp(self):
        self.book = LibraryBook.objects.create(
            isbn='9781234567890',
            title='Introduction to Programming',
            author='John Developer',
            publisher='Tech Books Publishing',
            category='TEXTBOOK',
            published_year=2023,
            total_copies=5,
            available_copies=5,
            price=Decimal('599.00')
        )
        self.student = Student.objects.create(
            name='Library Student',
            age=17,
            gender='F',
            dob=datetime(2007, 9, 25).date(),
            grade=12,
            relation='Test Parent'
        )
    
    def test_book_creation(self):
        """Test creating a library book"""
        self.assertEqual(self.book.title, 'Introduction to Programming')
        self.assertTrue(self.book.is_available)
    
    def test_book_issue(self):
        """Test issuing a book"""
        issue = BookIssue.objects.create(
            book=self.book,
            student=self.student,
            due_date=timezone.now().date() + timedelta(days=14)
        )
        
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
        self.assertEqual(issue.status, 'ISSUED')
    
    def test_book_overdue(self):
        """Test overdue book detection"""
        past_date = timezone.now().date() - timedelta(days=5)
        issue = BookIssue.objects.create(
            book=self.book,
            student=self.student,
            due_date=past_date
        )
        issue.save()  # Trigger auto-update
        
        self.assertEqual(issue.status, 'OVERDUE')
        fine = issue.calculate_fine()
        self.assertGreater(fine, 0)


class UserProfileTestCase(TestCase):
    """Test User Profile and Roles"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            email='test@example.com'
        )
    
    def test_create_teacher_profile(self):
        """Test creating a teacher profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            role='TEACHER',
            phone='9876543210'
        )
        self.assertEqual(profile.role, 'TEACHER')
        self.assertEqual(str(profile), 'testuser - TEACHER')
    
    def test_create_parent_profile(self):
        """Test creating a parent profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            role='PARENT',
            phone='9876543210'
        )
        self.assertEqual(profile.role, 'PARENT')


class NotificationTestCase(TestCase):
    """Test Notification system"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='notifyuser', password='test123')
    
    def test_create_notification(self):
        """Test creating a notification"""
        notification = Notification.objects.create(
            recipient_type='STUDENT',
            recipient=self.user,
            title='Test Notification',
            message='This is a test notification'
        )
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.title, 'Test Notification')
    
    def test_mark_notification_read(self):
        """Test marking notification as read"""
        notification = Notification.objects.create(
            recipient_type='PARENT',
            recipient=self.user,
            title='Fee Reminder',
            message='Please pay your fees'
        )
        notification.is_read = True
        notification.save()
        self.assertTrue(notification.is_read)
