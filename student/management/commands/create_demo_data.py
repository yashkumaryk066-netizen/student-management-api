"""
Enhanced Demo Data Creation Script for NextGen ERP
Creates realistic demo data for presentations and client demonstrations
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from student.models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Subject, Classroom, Exam, Grade, LibraryBook, BookIssue,
    DemoRequest
)


class Command(BaseCommand):
    help = 'Create comprehensive demo data for NextGen ERP'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating demo data...'))
        
        # Create users
        self.create_users()
        
        # Create academic data
        self.create_subjects()
        self.create_classrooms()
        
        # Create students
        self.create_students()
        
        # Create attendance records
        self.create_attendance()
        
        # Create payments
        self.create_payments()
        
        # Create exams and grades
        self.create_exams_and_grades()
        
        # Create library books
        self.create_library_books()
        
        # Create notifications
        self.create_notifications()
        
        self.stdout.write(self.style.SUCCESS('✅ Demo data created successfully!'))
    
    def create_users(self):
        """Create demo users for all roles"""
        
        # Admin
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@school.com', 'Admin123!')
            UserProfile.objects.create(user=admin, role='ADMIN', phone='8356926231')
            self.stdout.write('Created admin user')
        
        # Teachers
        teachers_data = [
            ('teacher1', 'Rajesh Kumar', '9876543210'),
            ('teacher2', 'Priya Sharma', '9876543211'),
            ('teacher3', 'Amit Verma', '9876543212'),
        ]
        
        for username, name, phone in teachers_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'{username}@school.com', 'Teacher123!')
                user.first_name = name.split()[0]
                user.last_name = ' '.join(name.split()[1:])
                user.save()
                UserProfile.objects.create(user=user, role='TEACHER', phone=phone)
        
        self.stdout.write('Created teacher users')
        
        # Parents
        parents_data = [
            ('parent1', 'Suresh Singh', '9876543220'),
            ('parent2', 'Meena Patel', '9876543221'),
            ('parent3', 'Ramesh Gupta', '9876543222'),
        ]
        
        for username, name, phone in parents_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, f'{username}@school.com', 'Parent123!')
                user.first_name = name.split()[0]
                user.last_name = ' '.join(name.split()[1:])
                user.save()
                UserProfile.objects.create(user=user, role='PARENT', phone=phone)
        
        self.stdout.write('Created parent users')
    
    def create_subjects(self):
        """Create subjects"""
        subjects_data = [
            ('MATH101', 'Mathematics', 4),
            ('PHY101', 'Physics', 4),
            ('CHEM101', 'Chemistry', 4),
            ('ENG101', 'English', 3),
            ('HIST101', 'History', 3),
            ('CS101', 'Computer Science', 4),
        ]
        
        for code, name, credits in subjects_data:
            Subject.objects.get_or_create(
                code=code,
                defaults={'name': name, 'credits': credits}
            )
        
        self.stdout.write('Created subjects')
    
    def create_classrooms(self):
        """Create classrooms"""
        classrooms_data = [
            ('101', 'CLASSROOM', 40, 1),
            ('102', 'CLASSROOM', 40, 1),
            ('LAB-1', 'LAB', 30, 2),
            ('LAB-2', 'LAB', 30, 2),
        ]
        
        for room_no, room_type, capacity, floor in classrooms_data:
            Classroom.objects.get_or_create(
                room_number=room_no,
                defaults={'room_type': room_type, 'capacity': capacity, 'floor': floor}
            )
        
        self.stdout.write('Created classrooms')
    
    def create_students(self):
        """Create realistic student data"""
        
        students_data = [
            ('Rahul Sharma', 15, 'M', '2009-05-15', 10),
            ('Priya Singh', 16, 'F', '2008-08-20', 11),
            ('Amit Kumar', 14, 'M', '2010-02-10', 9),
            ('Sneha Patel', 15, 'F', '2009-11-05', 10),
            ('Vikram Gupta', 16, 'M', '2008-07-18', 11),
            ('Anjali Verma', 14, 'F', '2010-04-22', 9),
            ('Rohit Mehta', 15, 'M', '2009-09-30', 10),
            ('Kavita Reddy', 16, 'F', '2008-12-12', 11),
            ('Arjun Nair', 14, 'M', '2010-06-08', 9),
            ('Divya Joshi', 15, 'F', '2009-03-25', 10),
            ('Karan Yadav', 16, 'M', '2008-10-14', 11),
            ('Pooja Desai', 14, 'F', '2010-01-19', 9),
            ('Sanjay Mishra', 15, 'M', '2009-07-07', 10),
            ('Ritu Agarwal', 16, 'F', '2008-05-30', 11),
            ('Manish Chauhan', 14, 'M', '2010-09-16', 9),
            ('Neha Bansal', 15, 'F', '2009-12-03', 10),
            ('Deepak Tiwari', 16, 'M', '2008-04-11', 11),
            ('Sakshi Khanna', 14, 'F', '2010-08-28', 9),
            ('Vishal Pandey', 15, 'M', '2009-06-21', 10),
            ('Simran Kapoor', 16, 'F', '2008-11-09', 11),
        ]
        
        parents = list(User.objects.filter(profile__role='PARENT'))
        
        for name, age, gender, dob, grade in students_data:
            if not Student.objects.filter(name=name).exists():
                parent = random.choice(parents) if parents else None
                Student.objects.create(
                    name=name,
                    age=age,
                    gender=gender,
                    dob=datetime.strptime(dob, '%Y-%m-%d').date(),
                    grade=grade,
                    relation=f'Parent: {parent.get_full_name()}' if parent else 'Guardian',
                    parent=parent
                )
        
        self.stdout.write(f'Created {len(students_data)} students')
    
    def create_attendance(self):
        """Create attendance records for last 30 days"""
        students = Student.objects.all()
        
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            
            for student in students:
                # 85% attendance rate (realistic)
                is_present = random.random() < 0.85
                
                Attendence.objects.get_or_create(
                    student=student,
                    date=date,
                    defaults={'is_present': is_present}
                )
        
        self.stdout.write('Created 30 days of attendance records')
    
    def create_payments(self):
        """Create payment records"""
        students = Student.objects.all()
        
        for student in students:
            # Create 3 fee records per student
            for month in range(3):
                due_date = timezone.now().date() + timedelta(days=30*month)
                
                # 70% paid, 20% pending, 10% overdue
                rand = random.random()
                if rand < 0.7:
                    status = 'PAID'
                    paid_date = due_date - timedelta(days=random.randint(1, 5))
                elif rand < 0.9:
                    status = 'PENDING'
                    paid_date = None
                else:
                    status = 'OVERDUE'
                    paid_date = None
                    due_date = timezone.now().date() - timedelta(days=random.randint(5, 15))
                
                Payment.objects.get_or_create(
                    student=student,
                    due_date=due_date,
                    defaults={
                        'amount': Decimal(random.choice(['5000.00', '6000.00', '7500.00'])),
                        'status': status,
                        'paid_date': paid_date,
                        'description': f'Tuition Fee - Month {month+1}'
                    }
                )
        
        self.stdout.write('Created payment records')
    
    def create_exams_and_grades(self):
        """Create exams and grades"""
        subjects = Subject.objects.all()[:3]  # Use first 3 subjects
        students = Student.objects.all()
        
        for subject in subjects:
            # Create exam
            exam, created = Exam.objects.get_or_create(
                name=f'{subject.name} Mid-Term',
                subject=subject,
                defaults={
                    'exam_type': 'MIDTERM',
                    'grade_class': '10',
                    'total_marks': 100,
                    'passing_marks': 40,
                    'exam_date': timezone.now().date() - timedelta(days=10),
                    'duration_minutes': 180
                }
            )
            
            # Create grades for students
            for student in students[:10]:  # Grade 10 students only
                if student.grade == 10:
                    marks = Decimal(random.randint(45, 95))
                    Grade.objects.get_or_create(
                        student=student,
                        exam=exam,
                        defaults={'marks_obtained': marks}
                    )
        
        self.stdout.write('Created exams and grades')
    
    def create_library_books(self):
        """Create library books"""
        books_data = [
            ('9781234567890', 'Introduction to Python Programming', 'John Smith', 'Tech Books', 'TEXTBOOK', 2023, Decimal('599.00')),
            ('9781234567891', 'Advanced Mathematics', 'Dr. Sharma', 'Academic Press', 'TEXTBOOK', 2022, Decimal('799.00')),
            ('9781234567892', 'Physics Fundamentals', 'Prof. Kumar', 'Science Publishers', 'TEXTBOOK', 2023, Decimal('699.00')),
            ('9781234567893', 'Chemistry Essentials', 'Dr. Patel', 'Education House', 'TEXTBOOK', 2022, Decimal('649.00')),
            ('9781234567894', 'World History', 'R.K. Singh', 'History Books', 'TEXTBOOK', 2021, Decimal('499.00')),
        ]
        
        for isbn, title, author, publisher, category, year, price in books_data:
            LibraryBook.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'category': category,
                    'published_year': year,
                    'total_copies': 5,
                    'available_copies': random.randint(2, 5),
                    'price': price
                }
            )
        
        self.stdout.write('Created library books')
        
        # Issue some books
        students = list(Student.objects.all()[:5])
        books = list(LibraryBook.objects.all()[:3])
        
        for student, book in zip(students, books):
            BookIssue.objects.get_or_create(
                student=student,
                book=book,
                defaults={
                    'due_date': timezone.now().date() + timedelta(days=14),
                    'status': 'ISSUED'
                }
            )
    
    def create_notifications(self):
        """Create sample notifications"""
        users = User.objects.filter(profile__role__in=['PARENT', 'STUDENT'])[:5]
        
        notifications_data = [
            ('Fee Reminder', 'Your fee payment is due in 5 days. Please pay to avoid late charges.', 'PARENT'),
            ('Exam Schedule', 'Mid-term exams will begin from next week. Please prepare well.', 'STUDENT'),
            ('Attendance Alert', 'Your attendance is below 75%. Please attend regularly.', 'STUDENT'),
            ('Holiday Notice', 'School will remain closed on upcoming festival. Happy holidays!', 'ALL'),
        ]
        
        for title, message, recipient_type in notifications_data:
            if recipient_type == 'ALL':
                Notification.objects.get_or_create(
                    title=title,
                    message=message,
                    recipient_type=recipient_type
                )
            else:
                for user in users:
                    Notification.objects.get_or_create(
                        title=title,
                        message=message,
                        recipient_type=recipient_type,
                        recipient=user
                    )
        
        self.stdout.write('Created notifications')
