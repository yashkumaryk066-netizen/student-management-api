from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from student.models import Student
from student.permissions import IsTeacherOrAdmin
from .base import get_owner_user

# Mock imports or assume existence of report_utils/id_card_utils in same package or sibling
from student.report_utils import generate_admit_card_pdf, generate_report_card_pdf
from student.id_card_utils import generate_id_card_pdf

class GenerateAdmitCardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    required_feature = 'exams'

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            # Ensure owner isolation
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Permission Denied"}, status=403)
                
            exam_name = request.query_params.get('exam', 'Final Examination 2024')
            
            pdf = generate_admit_card_pdf(student, exam_name, '2025-03-15', 'Main Hall, Block A')
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="AdmitCard_{student.name}.pdf"'
            return response
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

class GenerateReportCardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    required_feature = 'exams'

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            # Ensure owner isolation
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Permission Denied"}, status=403)
            
            # Mock Data for now (In real app, fetch from ExamResult model)
            results = [
                {'subject': 'Mathematics', 'total': 100, 'marks': 95},
                {'subject': 'Physics', 'total': 100, 'marks': 88},
                {'subject': 'Chemistry', 'total': 100, 'marks': 92},
                {'subject': 'English', 'total': 100, 'marks': 85},
                {'subject': 'Computer Science', 'total': 100, 'marks': 98},
            ]
            
            pdf = generate_report_card_pdf(student, results)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ReportCard_{student.name}.pdf"'
            return response
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

class GenerateIDCardView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    required_feature = 'id_cards'

    def get(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            # Ensure owner isolation
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Permission Denied"}, status=403)

            pdf = generate_id_card_pdf(student)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="IDCard_{student.name}.pdf"'
            return response
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)
