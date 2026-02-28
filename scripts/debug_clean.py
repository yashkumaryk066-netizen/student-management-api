import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()
from student.models import Student
from django.db.models import Count

print("--- Cleaning Duplicates ---")
dupes = Student.objects.values('roll_number', 'institution_type').annotate(count=Count('id')).filter(count__gt=1)
for d in dupes:
    print(f"Found Duplicate: Roll={d['roll_number']}, Type={d['institution_type']}")
    # Keep one, delete others
    students = Student.objects.filter(roll_number=d['roll_number'], institution_type=d['institution_type'])
    first = students.first()
    students.exclude(id=first.id).delete()
    print("Cleaned.")

print("Cleaning Test Data...")
Student.objects.filter(name__startswith="Test Student V").delete()
print("Done.")
