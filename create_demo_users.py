import os
import django
import sys

# Add the project directory to the sys.path
sys.path.append('/home/yashamishra/student-management-api')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.pythonanywhere_settings')
django.setup()

from django.contrib.auth.models import User
from student.models import UserProfile, Student
from django.utils import timezone
from datetime import date

def create_users():
    print("Creating demo users...")

    # --- 1. ADMIN USER ---
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser('admin', 'admin@school.com', 'Admin123!')
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'ADMIN'})
        print("✅ Admin created: admin / Admin123!")
    else:
        u = User.objects.get(username='admin')
        u.set_password('Admin123!')
        u.save()
        UserProfile.objects.get_or_create(user=u, defaults={'role': 'ADMIN'})
        print("✅ Admin password reset: admin / Admin123!")

    # --- 2. TEACHER USER ---
    if not User.objects.filter(username='teacher').exists():
        user = User.objects.create_user('teacher', 'teacher@school.com', 'Teacher123!')
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'TEACHER'})
        print("✅ Teacher created: teacher / Teacher123!")
    else:
        u = User.objects.get(username='teacher')
        u.set_password('Teacher123!')
        u.save()
        UserProfile.objects.get_or_create(user=u, defaults={'role': 'TEACHER'})
        print("✅ Teacher password reset: teacher / Teacher123!")

    # --- 3. STUDENT USER ---
    if not User.objects.filter(username='student').exists():
        # Create User
        user = User.objects.create_user('student', 'student@school.com', 'Student123!')
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'STUDENT'})
        
        # Create Linked Student Profile
        if not hasattr(user, 'student_profile'):
            Student.objects.create(
                user=user,
                name="Rahul Sharma",
                age=20,
                gender="Male",
                dob=date(2004, 5, 15),
                grade=12,
                relation="Father" # Required field in model
            )
        print("✅ Student created: student / Student123!")
    else:
        u = User.objects.get(username='student')
        u.set_password('Student123!')
        u.save()
        UserProfile.objects.get_or_create(user=u, defaults={'role': 'STUDENT'})
        # Ensure student profile exists
        if not hasattr(u, 'student_profile'):
             Student.objects.create(
                user=u,
                name="Rahul Sharma",
                age=20,
                gender="Male",
                dob=date(2004, 5, 15),
                grade=12,
                relation="Father"
            )
        print("✅ Student password reset: student / Student123!")

    # --- 4. PARENT USER ---
    if not User.objects.filter(username='parent').exists():
        user = User.objects.create_user('parent', 'parent@school.com', 'Parent123!')
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'PARENT'})
        
        # Link to student
        student_user = User.objects.get(username='student')
        if hasattr(student_user, 'student_profile'):
            student = student_user.student_profile
            student.parent = user
            student.save()
            
        print("✅ Parent created: parent / Parent123!")
    else:
        u = User.objects.get(username='parent')
        u.set_password('Parent123!')
        u.save()
        UserProfile.objects.get_or_create(user=u, defaults={'role': 'PARENT'})
        print("✅ Parent password reset: parent / Parent123!")

if __name__ == '__main__':
    try:
        create_users()
        print("\n🎉 All demo users ready!")
    except Exception as e:
        print(f"\n❌ Error creating users: {e}")
