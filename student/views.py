from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework.response import Response
from .models import Student, Attendence
from .Serializer import StudentSerializer, AttendenceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    get=extend_schema(
        tags=['Student'],
        operation_id='listStudents',
        summary='List all students',
        description='Retrieve a list of all students with optional search by name or gender',
        responses={200: StudentSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search students by name or gender',
                required=False,
            ),
        ],
    ),
    post=extend_schema(
        tags=['Student'],
        operation_id='createStudent',
        summary='Create a new student',
        description='Create a new student record',
        request=StudentSerializer,
        responses={201: StudentSerializer},
    ),
)
class StudentListCreateView(APIView):
    def get(self, request):
        search = request.query_params.get("search","").strip()
        students = Student.objects.all()
        if search:
            students= students.filter(
                Q(name__icontains=search)|
                Q(gender__icontains=search)
            )
        if not students.exists():
            return Response(
                {"message": "Student does not exist"}, 
                status=status.HTTP_404_NOT_FOUND
            )
 
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=['Student'],
        operation_id='getStudent',
        summary='Get student details',
        description='Retrieve details of a specific student by ID',
        responses={200: StudentSerializer},
    ),
    put=extend_schema(
        tags=['Student'],
        operation_id='updateStudent',
        summary='Update student',
        description='Update an existing student record',
        request=StudentSerializer,
        responses={200: StudentSerializer},
    ),
    delete=extend_schema(
        tags=['Student'],
        operation_id='deleteStudent',
        summary='Delete student',
        description='Delete a student record',
        responses={204: None},
    ),
)
class StudentDetailsView(APIView):
    def get(self, request, id):
        student = Student.objects.filter(id=id).first()
        if not student:
            return Response(
                {"error": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentSerializer(student)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        student = Student.objects.filter(id=id).first()
        if not student:
            return Response(
                {"error": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        student = Student.objects.filter(id=id).first()
        if not student:
            return Response(
                {"error": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(
            {"message": "Student deleted"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
@extend_schema_view(
    get=extend_schema(
        tags=['Student'],
        operation_id='getTodayAttendance',
        summary="Get today's attendance summary",
        description="Get attendance summary for today including present and absent students",
    ),
)
class StudentTodayView(APIView):
    
    def get(self, request):
        today = timezone.now().date()

        total_students = Student.objects.count()

        today_attendance = Attendence.objects.filter(date=today).select_related('student')

        present_students = today_attendance.filter(is_present=True)
        absent_students = today_attendance.filter(is_present=False)

        present_serializer = StudentSerializer(
            [a.student for a in present_students], many=True
        )

        absent_serializer = StudentSerializer(
            [a.student for a in absent_students], many=True
        )

        return Response({
            "date": str(today),
            "total_students": total_students,
            "present_count": present_students.count(),
            "absent_count": absent_students.count(),
            "present_students": present_serializer.data,
            "absent_students": absent_serializer.data
        }, status=status.HTTP_200_OK)
        
@extend_schema_view(
    get=extend_schema(
        tags=['Attendance'],
        operation_id='listAttendance',
        summary='List all attendance records',
        description='Retrieve all attendance records',
        responses={200: AttendenceSerializer(many=True)},
    ),
    post=extend_schema(
        tags=['Attendance'],
        operation_id='markAttendance',
        summary='Mark attendance',
        description='Mark attendance for a student. Prevents duplicate entries for the same date.',
        request=AttendenceSerializer,
        responses={201: AttendenceSerializer},
    ),
)
class AttendenceCreateView(APIView):
    def get(self, request):
        attendence = Attendence.objects.all()
        serializer = AttendenceSerializer(attendence, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        student_id = request.data.get("student")
        date = request.data.get("date")
        if not date:
            date = timezone.now().date()
        if Attendence.objects.filter(student_id=student_id, date=date).exists():
            return Response(
                {"message": "Attendance already marked"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = AttendenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        tags=['Attendance'],
        operation_id='getAttendance',
        summary='Get attendance details',
        description='Retrieve details of a specific attendance record by ID',
        responses={200: AttendenceSerializer},
    ),
    put=extend_schema(
        tags=['Attendance'],
        operation_id='updateAttendance',
        summary='Update attendance',
        description='Update an existing attendance record',
        request=AttendenceSerializer,
        responses={200: AttendenceSerializer},
    ),
    delete=extend_schema(
        tags=['Attendance'],
        operation_id='deleteAttendance',
        summary='Delete attendance',
        description='Delete an attendance record',
        responses={204: None},
    ),
)
class AttendenceDetailsView(APIView):
    def get(self, request, id):
        attendence = Attendence.objects.filter(id=id).first()
        if not attendence:
            return Response(
                {"error": "Attendence not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendenceSerializer(attendence)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        attendence = Attendence.objects.filter(id=id).first()
        if not attendence:
            return Response(
                {"error": "Attendence not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AttendenceSerializer(attendence, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        attendence = Attendence.objects.filter(id=id).first()
        if not attendence:
            return Response(
                {"error": "Attendence not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        attendence.delete()
        return Response(
            {"message": "Attendence deleted"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    

@extend_schema_view(
    get=extend_schema(
        tags=['Profile'],
        operation_id='getProfile',
        summary='Get user profile',
        description='Get the authenticated user profile information',
    ),
    post=extend_schema(
        tags=['Profile'],
        operation_id='getProfilePost',
        summary='Get user profile (POST)',
        description='Get the authenticated user profile information via POST',
    ),
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "username": request.user.username
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        return self.get(request)

