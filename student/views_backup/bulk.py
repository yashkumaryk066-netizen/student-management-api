from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import csv
import io

class BulkImportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'CLIENT']:
            return Response({"error": "Permission Denied"}, status=403)

        file_obj = request.FILES.get('file')
        import_type = request.data.get('type')
        
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=400)

        # Basic CSV Parsing
        try:
            decoded_file = file_obj.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            count = 0
            errors = []
            
            for row in reader:
                try:
                    self._process_row(row, import_type, request.user)
                    count += 1
                except Exception as e:
                    errors.append(f"Row {count+1}: {str(e)}")
            
            return Response({
                "message": f"Successfully imported {count} records.",
                "errors": errors
            })
            
        except Exception as e:
            return Response({"error": f"Import failed: {str(e)}"}, status=500)

    def _process_row(self, row, type, user):
        # Helper to route to specific logic
        from student.models import Student, LibraryBook, Employee
        
        if type == 'STUDENT':
            Student.objects.create(
                user=user, # Link to owner (Assuming placeholder logic from original view)
                name=row.get('name'),
                # phone=row.get('phone', ''), # Field might need adding to model if not generic
                # email=row.get('email', ''),
                address=row.get('address', '')
                # Add more fields as per CSV headers
            )
        elif type == 'BOOK':
             LibraryBook.objects.create(
                created_by=user,
                title=row.get('title'),
                author=row.get('author'),
                isbn=row.get('isbn', '0000000000'),
                total_copies=int(row.get('copies', 1)),
                price=0
             )
        elif type == 'STAFF':
            Employee.objects.create(
                user=user, # Temporarily link user as placeholder
                # basic_salary, joining_date etc needed
                joining_date='2024-01-01',
                basic_salary=0,
                contract_type='PERMANENT'
            )
        else:
            raise ValueError("Invalid Import Type")
