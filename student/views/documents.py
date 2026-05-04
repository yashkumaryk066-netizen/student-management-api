from .base import *
from student.models import Student, Grade, Exam
from django.http import HttpResponse
from student.report_utils import generate_admit_card_pdf, generate_report_card_pdf
from student.id_card_utils import generate_id_card_pdf
from student.admission_letter_utils import generate_admission_letter_pdf
from drf_spectacular.utils import extend_schema

class GenerateCertificateView(APIView):
    """Generate PDF Admission Letter/Certificate for a student"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id):
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return Response({"error": "Student not found"}, status=404)
        
        # Verify ownership
        owner = get_owner_user(request.user)
        if not request.user.is_superuser and student.created_by != owner:
            return Response({"error": "Access Denied"}, status=403)
        
        pdf_buffer = generate_admission_letter_pdf(student)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="AdmissionLetter_{student.name.replace(" ", "_")}.pdf"'
        return response

class GenerateIDCardView(APIView):
    """Generate ID card PDF"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id):
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return Response({"error": "Student not found"}, status=404)
        
        # Verify ownership
        owner = get_owner_user(request.user)
        if not request.user.is_superuser and student.created_by != owner:
            return Response({"error": "Access Denied"}, status=403)
        
        pdf_buffer = generate_id_card_pdf(student)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="IDCard_{student.name.replace(" ", "_")}.pdf"'
        return response

class GenerateAdmitCardView(APIView):
    """Generate admit card for exams"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id):
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return Response({"error": "Student not found"}, status=404)
        
        # Verify ownership
        owner = get_owner_user(request.user)
        if not request.user.is_superuser and student.created_by != owner:
            return Response({"error": "Access Denied"}, status=403)
        
        # Fetch exams for student's class
        exams = Exam.objects.filter(grade_class=student.grade, created_by=owner).order_by('exam_date')
        if not exams.exists() and student.batch:
             exams = Exam.objects.filter(batch=student.batch, created_by=owner).order_by('exam_date')

        pdf_buffer = generate_admit_card_pdf(student, exams)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="AdmitCard_{student.name.replace(" ", "_")}.pdf"'
        return response

class GenerateReportCardView(APIView):
    """Generate report card with grades"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, student_id):
        student = Student.objects.filter(id=student_id).first()
        if not student:
            return Response({"error": "Student not found"}, status=404)
        
        # Verify ownership
        owner = get_owner_user(request.user)
        if not request.user.is_superuser and student.created_by != owner:
            return Response({"error": "Access Denied"}, status=403)
        
        # Fetch grades
        grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('exam__exam_date')
        
        pdf_buffer = generate_report_card_pdf(student, grades)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ReportCard_{student.name.replace(" ", "_")}.pdf"'
        return response

class DocumentGenerationView(APIView):
    """Unified document generation endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        doc_type = request.data.get('type')  # certificate, id_card, admit_card, report_card
        student_id = request.data.get('student_id')
        
        if not doc_type or not student_id:
            return Response({"error": "Document type and student ID required"}, status=400)
        
        # Map to existing views
        view_map = {
            'certificate': GenerateCertificateView,
            'id_card': GenerateIDCardView,
            'admit_card': GenerateAdmitCardView,
            'report_card': GenerateReportCardView
        }
        
        if doc_type not in view_map:
            return Response({"error": "Invalid document type"}, status=400)
            
        view_instance = view_map[doc_type].as_view()
        return view_instance(request, student_id=student_id)

class GenerateBulkAdmitCardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        import zipfile
        import io
        from django.http import HttpResponse
        
        owner = get_owner_user(request.user)
        grade = request.query_params.get('grade')
        batch_id = request.query_params.get('batch_id')
        
        students = Student.objects.filter(created_by=owner)
        if grade:
            students = students.filter(grade=grade)
        if batch_id:
            students = students.filter(batch_id=batch_id)
            
        if not students.exists():
            return Response({"error": "No students found for given criteria"}, status=404)
            
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for student in students:
                exams = Exam.objects.filter(grade_class=student.grade, created_by=owner).order_by('exam_date')
                if not exams.exists() and student.batch:
                    exams = Exam.objects.filter(batch=student.batch, created_by=owner).order_by('exam_date')
                    
                pdf_buffer = generate_admit_card_pdf(student, exams)
                zf.writestr(f"AdmitCard_{student.roll_number}_{student.name.replace(' ', '_')}.pdf", pdf_buffer.getvalue())
                
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Bulk_Admit_Cards.zip"'
        return response

class GenerateBulkIDCardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        import zipfile
        import io
        from django.http import HttpResponse
        
        owner = get_owner_user(request.user)
        grade = request.query_params.get('grade')
        batch_id = request.query_params.get('batch_id')
        
        students = Student.objects.filter(created_by=owner)
        if grade:
            students = students.filter(grade=grade)
        if batch_id:
            students = students.filter(batch_id=batch_id)
            
        if not students.exists():
            return Response({"error": "No students found for given criteria"}, status=404)
            
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zf:
            for student in students:
                pdf_buffer = generate_id_card_pdf(student)
                zf.writestr(f"IDCard_{student.roll_number}_{student.name.replace(' ', '_')}.pdf", pdf_buffer.getvalue())
                
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Bulk_ID_Cards.zip"'
        return response
class MyReportCardView(APIView):
    """
    Compatibility endpoint for legacy student dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({"error": "Student profile not found"}, status=403)
        return GenerateReportCardView().get(request, student_id=student.id)


class MyResultsView(APIView):
    """
    Compatibility endpoint for legacy student dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({"error": "Student profile not found"}, status=403)

        grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-exam__exam_date')
        results = []
        for g in grades:
            exam = g.exam
            results.append({
                "exam": exam.name if exam else None,
                "subject": exam.subject.name if exam and exam.subject else "General",
                "marks_obtained": float(g.marks_obtained or 0),
                "total_marks": float(exam.total_marks if exam else 0),
                "percentage": float(g.percentage or 0),
                "status": g.status,
                "exam_date": exam.exam_date if exam else None,
            })
        return Response({"student": student.name, "results": results})


@extend_schema(exclude=True)
class LegacyGenerateIDCardView(GenerateIDCardView):
    pass


@extend_schema(exclude=True)
class LegacyGenerateAdmitCardView(GenerateAdmitCardView):
    pass


@extend_schema(exclude=True)
class LegacyGenerateReportCardView(GenerateReportCardView):
    pass


@extend_schema(exclude=True)
class LegacyGenerateCertificateView(GenerateCertificateView):
    pass


@extend_schema(exclude=True)
class LegacyGenerateBulkIDCardView(GenerateBulkIDCardView):
    pass


@extend_schema(exclude=True)
class LegacyGenerateBulkAdmitCardView(GenerateBulkAdmitCardView):
    pass
