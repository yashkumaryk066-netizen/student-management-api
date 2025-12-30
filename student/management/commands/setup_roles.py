from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import Student, UserProfile, Payment, Notification
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Setup sample users with different roles and test data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Setting up role-based system...'))
        
        # Create Admin user
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            UserProfile.objects.create(user=admin_user, role='ADMIN', phone='9876543210')
            self.stdout.write(self.style.SUCCESS(f'✓ Created ADMIN: admin / admin123'))
        else:
            UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'ADMIN', 'phone': '9876543210'})
            self.stdout.write(self.style.WARNING(f'  Admin user already exists'))
        
        # Create Teacher user
        teacher_user, created = User.objects.get_or_create(username='teacher1')
        if created:
            teacher_user.set_password('teacher123')
            teacher_user.first_name = 'Rajesh'
            teacher_user.last_name = 'Kumar'
            teacher_user.email = 'teacher@school.com'
            teacher_user.save()
            UserProfile.objects.create(user=teacher_user, role='TEACHER', phone='9876543211')
            self.stdout.write(self.style.SUCCESS(f'✓ Created TEACHER: teacher1 / teacher123'))
        else:
            UserProfile.objects.get_or_create(user=teacher_user, defaults={'role': 'TEACHER', 'phone': '9876543211'})
            self.stdout.write(self.style.WARNING(f'  Teacher user already exists'))
        
        # Create Parent user
        parent_user, created = User.objects.get_or_create(username='parent1')
        if created:
            parent_user.set_password('parent123')
            parent_user.first_name = 'Sunita'
            parent_user.last_name = 'Sharma'
            parent_user.email = 'parent@email.com'
            parent_user.save()
            UserProfile.objects.create(user=parent_user, role='PARENT', phone='9876543212')
            self.stdout.write(self.style.SUCCESS(f'✓ Created PARENT: parent1 / parent123'))
        else:
            UserProfile.objects.get_or_create(user=parent_user, defaults={'role': 'PARENT', 'phone': '9876543212'})
            self.stdout.write(self.style.WARNING(f'  Parent user already exists'))
        
        # Create Student user
        student_user, created = User.objects.get_or_create(username='student1')
        if created:
            student_user.set_password('student123')
            student_user.first_name = 'Rahul'
            student_user.last_name = 'Sharma'
            student_user.email = 'rahul@student.com'
            student_user.save()
            UserProfile.objects.create(user=student_user, role='STUDENT', phone='9876543213')
            self.stdout.write(self.style.SUCCESS(f'✓ Created STUDENT: student1 / student123'))
        else:
            UserProfile.objects.get_or_create(user=student_user, defaults={'role': 'STUDENT', 'phone': '9876543213'})
            self.stdout.write(self.style.WARNING(f'  Student user already exists'))
        
        # Link existing students to parent if available
        students = Student.objects.all()[:2]
        for student in students:
            if not student.parent:
                student.parent = parent_user
                student.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Linked student "{student.name}" to parent'))
        
        # Link first student to student_user if available
        if students:
            first_student = students[0]
            if not first_student.user:
                first_student.user = student_user
                first_student.save()
                self.stdout.write(self.style.SUCCESS(f'✓ Linked user account to student "{first_student.name}"'))
        
        # Create sample payments
        if students:
            for i, student in enumerate(students):
                # Create a pending payment
                payment, created = Payment.objects.get_or_create(
                    student=student,
                    description='Quarterly Fee - Term 1',
                    defaults={
                        'amount': 5000.00,
                        'due_date': date.today() + timedelta(days=7),
                        'status': 'PENDING'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created payment for {student.name}: ₹5000'))
                    
                    # Create notification for parent
                    if student.parent:
                        Notification.objects.create(
                            recipient_type='PARENT',
                            recipient=student.parent,
                            title=f'Payment Due for {student.name}',
                            message=f'A payment of ₹5000 is due on {payment.due_date.strftime("%d-%b-%Y")}. Please pay before the due date.'
                        )
                        self.stdout.write(self.style.SUCCESS(f'✓ Created payment notification for parent'))
        
        #Create sample notification for teacher
        Notification.objects.get_or_create(
            recipient_type='TEACHER',
            title='Welcome to the System',
            message='You can now mark attendance and manage students through your dashboard.',
            defaults={'recipient': None}
        )
        
        # Create notification for all
        Notification.objects.get_or_create(
            recipient_type='ALL',
            title='System Update',
            message='Welcome to the new role-based management system! Please explore your personalized dashboard.',
            defaults={'recipient': None}
        )
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Setup Complete! Login credentials:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('ADMIN     : admin / admin123'))
        self.stdout.write(self.style.SUCCESS('TEACHER   : teacher1 / teacher123'))
        self.stdout.write(self.style.SUCCESS('PARENT    : parent1 / parent123'))
        self.stdout.write(self.style.SUCCESS('STUDENT   : student1 / student123'))
        self.stdout.write(self.style.SUCCESS('='*60))
