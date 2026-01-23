from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Grade, Student

class StudentMyResultView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "User is not linked to a student profile"}, status=403)
        
        student = request.user.student_profile
        grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-exam__exam_date')
        
        data = []
        for g in grades:
             data.append({
                 "exam": g.exam.name,
                 "subject": g.exam.subject.name if g.exam.subject else "General",
                 "date": g.exam.exam_date,
                 "marks_obtained": g.marks_obtained,
                 "total_marks": g.exam.total_marks,
                 "percentage": g.percentage,
                 "status": g.status
             })
             
        return Response(data)

class StudentDownloadReportCardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from .report_card_utils import generate_progress_report_pdf
        
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "User is not linked to a student profile"}, status=403)
            
        student = request.user.student_profile
        
        try:
            pdf_buffer = generate_progress_report_pdf(student)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Progress_Report_{student.name}.pdf"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class StudentDownloadAdmitCardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from .admit_card_utils import generate_admit_card_pdf
        
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "User is not linked to a student profile"}, status=403)
            
        student = request.user.student_profile
        
        try:
            pdf_buffer = generate_admit_card_pdf(student)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Admit_Card_{student.roll_number or student.name}.pdf"'
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=500)
