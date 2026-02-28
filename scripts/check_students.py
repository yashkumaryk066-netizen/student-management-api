import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()
from student.models import Student
s = Student.objects.first()
if s:
    print(f"ID: {s.id}, Name: {s.name}")
else:
    print("No students found")
