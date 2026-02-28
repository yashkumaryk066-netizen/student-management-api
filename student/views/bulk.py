from .base import *
import csv
import io
import random
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from student.models import Student, LibraryBook, Employee, UserProfile
from student.security_utils import generate_secure_password

class BulkImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'CLIENT']:
            return Response({"error": "Permission Denied: Only institution admins can perform bulk imports."}, status=403)

        file_obj = request.FILES.get('file')
        import_type = request.data.get('type') # STUDENT, BOOK, STAFF
        
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        # Basic CSV Parsing
        try:
            decoded_file = file_obj.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            count = 0
            errors = []
            owner = get_owner_user(request.user)
            
            for index, row in enumerate(reader):
                try:
                    self._process_row(row, import_type, owner)
                    count += 1
                except Exception as e:
                    errors.append(f"Row {index+2}: {str(e)}")
            
            # Invalidate Caches (Generic approach for now)
            # invalidate_cache('student_list*')
            
            return Response({
                "message": f"Successfully imported {count} {import_type.lower()}(s).",
                "count": count,
                "errors": errors if errors else None
            }, status=201 if count > 0 else 400)
            
        except Exception as e:
            return Response({"error": f"Import system failed: {str(e)}"}, status=500)

    def _process_row(self, row, type, owner):
        if type == 'STUDENT':
            # 1. Create User for Student
            email = row.get('Email', row.get('email', f"s{random.randint(100000, 999999)}@system.local"))
            username = row.get('Username', row.get('username', email.split('@')[0]))
            
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            student_user = User.objects.create_user(
                username=username,
                email=email,
                password=generate_secure_password(),
                first_name=row.get('Name', row.get('name', 'Bulk Student')).split(' ')[0]
            )
            
            UserProfile.objects.create(
                user=student_user,
                role='STUDENT',
                institution_type=owner.profile.institution_type,
                subscription_expiry=owner.profile.subscription_expiry
            )

            # 2. Create Student Profile
            Student.objects.create(
                created_by=owner,
                user=student_user,
                name=row.get('Name', row.get('name', 'Bulk Student')),
                dob=row.get('DOB', row.get('dob', '2010-01-01')),
                gender=row.get('Gender', row.get('gender', 'MALE')).upper(),
                grade=int(row.get('Grade', row.get('grade', 1))),
                relation=row.get('Relation', row.get('relation', 'Parent')),
                email=email,
                roll_number=row.get('RollNumber', row.get('roll_number')),
                institution_type=owner.profile.institution_type
            )
            
        elif type == 'BOOK':
             LibraryBook.objects.create(
                created_by=owner,
                title=row.get('Title', row.get('title', 'Unknown Book')),
                author=row.get('Author', row.get('author', 'Unknown Author')),
                isbn=row.get('ISBN', row.get('isbn', f"BOK-{random.randint(1000, 9999)}")),
                total_copies=int(row.get('Copies', row.get('copies', 1)))
             )
             
        elif type == 'STAFF':
            # Create Staff User
            email = row.get('Email', row.get('email', f"staff{random.randint(1000, 9999)}@system.local"))
            username = row.get('Username', row.get('username', email.split('@')[0]))
            
            # Ensure unique
            while User.objects.filter(username=username).exists():
                username = f"{username}{random.randint(1, 9)}"

            staff_user = User.objects.create_user(
                username=username,
                email=email,
                password=generate_secure_password(),
                first_name=row.get('Name', row.get('name', 'Bulk Staff'))
            )
            
            UserProfile.objects.create(
                user=staff_user,
                role=row.get('Role', row.get('role', 'TEACHER')).upper(),
                institution_type=owner.profile.institution_type
            )

            Employee.objects.create(
                created_by=owner,
                user=staff_user,
                joining_date=row.get('JoiningDate', row.get('joining_date', timezone.now().date())),
                basic_salary=float(row.get('Salary', row.get('salary', 0))),
                contract_type='PERMANENT'
            )
        else:
            raise ValueError(f"Invalid Import Type: {type}")
