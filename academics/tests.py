from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from student.models import Student, Subject, Exam, Grade, Classroom, ClassSchedule


class AcademicsTestCase(TestCase):
    """Test Academic module functionality"""
    
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher1', password='teach123')
        self.subject = Subject.objects.create(
            name='Physics',
            code='PHY101',
            credits=4,
            description='Introduction to Physics'
        )
        self.student = Student.objects.create(
            name='Academic Student',
            age=16,
            gender='M',
            dob=datetime(2008, 6, 15).date(),
            grade=11,
            relation='Test Parent'
        )
    
    def test_subject_creation(self):
        """Test creating a subject"""
        self.assertEqual(self.subject.name, 'Physics')
        self.assertEqual(self.subject.code, 'PHY101')
        self.assertEqual(str(self.subject), 'PHY101 - Physics')
    
    def test_classroom_creation(self):
        """Test creating a classroom"""
        classroom = Classroom.objects.create(
            room_number='101',
            room_type='CLASSROOM',
            capacity=40,
            floor=1,
            building='Main Building'
        )
        self.assertEqual(classroom.room_number, '101')
        self.assertEqual(classroom.capacity, 40)
    
    def test_class_schedule_creation(self):
        """Test creating a class schedule"""
        classroom = Classroom.objects.create(
            room_number='102',
            room_type='CLASSROOM',
            capacity=35,
            floor=1
        )
        
        schedule = ClassSchedule.objects.create(
            subject=self.subject,
            teacher=self.teacher,
            classroom=classroom,
            day_of_week='MONDAY',
            start_time='09:00:00',
            end_time='10:00:00',
            section='11-A',
            academic_year='2024-25'
        )
        
        self.assertEqual(schedule.day_of_week, 'MONDAY')
        self.assertEqual(schedule.section, '11-A')
    
    def test_exam_creation(self):
        """Test creating an exam"""
        exam = Exam.objects.create(
            name='Physics Mid-Term',
            exam_type='MIDTERM',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date() + timedelta(days=7),
            duration_minutes=180
        )
        
        self.assertEqual(exam.name, 'Physics Mid-Term')
        self.assertEqual(exam.total_marks, 100)
        self.assertEqual(exam.passing_marks, 40)
    
    def test_grade_auto_status_pass(self):
        """Test automatic pass status based on marks"""
        exam = Exam.objects.create(
            name='Test Exam',
            exam_type='UNIT',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date()
        )
        
        grade = Grade.objects.create(
            student=self.student,
            exam=exam,
            marks_obtained=Decimal('65.00')
        )
        
        self.assertEqual(grade.status, 'PASS')
        self.assertEqual(grade.percentage, 65.0)
    
    def test_grade_auto_status_fail(self):
        """Test automatic fail status based on marks"""
        exam = Exam.objects.create(
            name='Test Exam 2',
            exam_type='UNIT',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date()
        )
        
        grade = Grade.objects.create(
            student=self.student,
            exam=exam,
            marks_obtained=Decimal('30.00')
        )
        
        self.assertEqual(grade.status, 'FAIL')
        self.assertEqual(grade.percentage, 30.0)
    
    def test_multiple_exams_per_subject(self):
        """Test that a subject can have multiple exams"""
        Exam.objects.create(
            name='Unit Test 1',
            exam_type='UNIT',
            subject=self.subject,
            grade_class='11',
            total_marks=50,
            passing_marks=20,
            exam_date=timezone.now().date()
        )
        Exam.objects.create(
            name='Mid-Term',
            exam_type='MIDTERM',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date() + timedelta(days=30)
        )
        Exam.objects.create(
            name='Final Exam',
            exam_type='FINAL',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date() + timedelta(days=60)
        )
        
        self.assertEqual(self.subject.exams.count(), 3)
    
    def test_student_grade_history(self):
        """Test that student can have grades for multiple exams"""
        exam1 = Exam.objects.create(
            name='Exam 1',
            exam_type='UNIT',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date()
        )
        exam2 = Exam.objects.create(
            name='Exam 2',
            exam_type='MIDTERM',
            subject=self.subject,
            grade_class='11',
            total_marks=100,
            passing_marks=40,
            exam_date=timezone.now().date() + timedelta(days=30)
        )
        
        Grade.objects.create(
            student=self.student,
            exam=exam1,
            marks_obtained=Decimal('75.00')
        )
        Grade.objects.create(
            student=self.student,
            exam=exam2,
            marks_obtained=Decimal('85.00')
        )
        
        self.assertEqual(self.student.grades.count(), 2)
