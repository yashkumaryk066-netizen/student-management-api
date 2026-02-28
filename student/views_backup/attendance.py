from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from datetime import date
from django.utils import timezone

from student.models import Attendence, Student
from student.serializers import AttendenceSerializer, StudentSerializer
from student.permissions import IsTeacherOrAdmin
from .base import filter_by_owner, get_owner_user

class StudentTodayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        students = filter_by_owner(Student.objects.all(), request.user)

        attendance = Attendence.objects.filter(student__in=students, date=today)

        present = attendance.filter(is_present=True)
        absent = attendance.filter(is_present=False)

        return Response({
            "date": str(today),
            "total_students": students.count(),
            "present_count": present.count(),
            "absent_count": absent.count(),
            "present_students": StudentSerializer(
                [a.student for a in present], many=True
            ).data,
            "absent_students": StudentSerializer(
                [a.student for a in absent], many=True
            ).data
        })

class AttendenceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        qs = Attendence.objects.all()
        qs = filter_by_owner(qs, request.user)
        serializer = AttendenceSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttendenceSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
            if not filter_by_owner(Student.objects.filter(id=student.id), request.user).exists():
                return Response({"error": "Permission denied"}, status=403)

            if Attendence.objects.filter(
                student=student,
                date=serializer.validated_data.get('date', date.today())
            ).exists():
                return Response({"error": "Already marked"}, status=400)

            owner = get_owner_user(request.user)
            serializer.save(created_by=owner)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class AttendenceDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_object(self, user, id):
        qs = Attendence.objects.filter(id=id)
        return filter_by_owner(qs, user).first()

    def get(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        return Response(AttendenceSerializer(attendance).data)
    
    def put(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        serializer = AttendenceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def delete(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
            return Response({"error": "Not found"}, status=404)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
