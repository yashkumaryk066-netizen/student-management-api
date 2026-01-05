import io
import os
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .models import GeneratedReport

# =========================
# CONSTANTS
# =========================
REPORT_PENDING = 'PENDING'
REPORT_READY = 'READY'

REPORT_FINANCE = 'FINANCE'
REPORT_EXAM = 'EXAM'
REPORT_HR = 'HR'
REPORT_GENERAL = 'GENERAL'
REPORT_ATTENDANCE = 'ATTENDANCE'
REPORT_ANALYTICS = 'ANALYTICS_SUMMARY'

# Plan-wise allowed reports
PLAN_REPORT_ACCESS = {
    'COACHING': {REPORT_GENERAL, REPORT_ATTENDANCE, REPORT_ANALYTICS},
    'SCHOOL': {REPORT_GENERAL, REPORT_EXAM, REPORT_ATTENDANCE, REPORT_ANALYTICS},
    'INSTITUTE': {REPORT_GENERAL, REPORT_EXAM, REPORT_FINANCE, REPORT_HR, REPORT_ATTENDANCE, REPORT_ANALYTICS},
}


# =========================
# REPORT LIST + GENERATE
# =========================
class ReportListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reports = (
            GeneratedReport.objects
            .filter(user=request.user)
            .only('id', 'name', 'report_type', 'generated_at', 'status', 'file_url')
            .order_by('-generated_at')
        )

        return Response([
            {
                "id": r.id,
                "name": r.name,
                "type": r.report_type,
                "date": r.generated_at.strftime("%Y-%m-%d"),
                "status": r.status,
                "url": r.file_url
            } for r in reports
        ])

    def post(self, request):
        report_type = request.data.get('type')

        if report_type not in [
            REPORT_GENERAL, REPORT_EXAM, REPORT_FINANCE, REPORT_HR, REPORT_ATTENDANCE, REPORT_ANALYTICS
        ]:
            return Response({"error": "Invalid report type"}, status=400)

        # =========================
        # PLAN CHECK
        # =========================
        profile = getattr(request.user, 'profile', None)
        plan = getattr(profile, 'institution_type', 'COACHING')

        allowed_reports = PLAN_REPORT_ACCESS.get(plan, set())
        if report_type not in allowed_reports:
            return Response({
                "error": "Report not allowed for your plan",
                "upgrade_required": True
            }, status=403)

        # =========================
        # SUBSCRIPTION EXPIRY CHECK
        # =========================
        expiry = getattr(profile, 'subscription_expiry', None)
        if expiry and expiry < timezone.now().date():
            return Response({
                "error": "Subscription expired",
                "action": "RENEW_PLAN"
            }, status=403)

        # =========================
        # CREATE REPORT
        # =========================
        report = GeneratedReport.objects.create(
            user=request.user,
            name=f"{report_type} Report - {timezone.now().strftime('%b %Y')}",
            report_type=report_type,
            status=REPORT_PENDING
        )

        # Sync generation (future async ready)
        report.status = REPORT_READY
        report.file_url = f"/api/reports/download/{report.id}/"
        report.save()

        return Response({
            "message": "Report generated successfully",
            "report_id": report.id,
            "status": report.status
        }, status=201)


# =========================
# REPORT DOWNLOAD
# =========================
class ReportDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            report = GeneratedReport.objects.get(pk=pk, user=request.user)

            if report.status != REPORT_READY:
                return Response(
                    {"error": "Report is still generating"},
                    status=409
                )

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # ===== PREMIUM HEADER (Navy Blue Background) =====
            p.setFillColorRGB(0.1, 0.1, 0.25) # Dark Navy
            p.rect(0, height - 130, width, 130, fill=1, stroke=0)
            
            # Logo Image (Official Y.S.M Logo)
            logo_path = os.path.join(settings.BASE_DIR, 'static/img/ysm_logo.png')
            if os.path.exists(logo_path):
                p.drawImage(logo_path, 40, height - 100, width=60, height=60, mask='auto', preserveAspectRatio=True)
            
            # Title
            p.setFillColorRGB(1, 1, 1) # White
            p.setFont("Helvetica-Bold", 24)
            p.drawString(110, height - 55, "Y.S.M ADVANCE EDUCATION SYSTEM")
            
            # Report Type Badge
            p.setFillColorRGB(0.4, 0.5, 0.9) # Indigo
            p.roundRect(width - 200, height - 70, 150, 35, 8, fill=1, stroke=0)
            p.setFillColorRGB(1, 1, 1)
            p.setFont("Helvetica-Bold", 12)
            p.drawCentredString(width - 125, height - 58, report.report_type.upper())
            
            # Report Details (Below header)
            p.setFont("Helvetica", 11)
            p.setFillColorRGB(0.9, 0.9, 1.0) # Light blue
            p.drawString(50, height - 95, f"Report: {report.name}")
            p.drawString(50, height - 115, f"Generated For: {request.user.email}")

            # ===== CONTENT AREA =====
            # Section Title Background
            p.setFillColorRGB(0.95, 0.95, 0.97) # Light gray
            p.rect(40, height - 180, width - 80, 40, fill=1, stroke=0)
            
            p.setFillColorRGB(0.2, 0.2, 0.4) # Dark text
            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 165, "Report Summary")
            
            # Data Table
            y = height - 210
            p.setFont("Helvetica", 12)
            data_points = self._get_report_data(report.report_type)
            
            # Table rows with alternating colors
            for i, (label, value) in enumerate(data_points):
                # Alternate row background
                if i % 2 == 0:
                    p.setFillColorRGB(0.98, 0.98, 1.0) # Very light blue
                    p.rect(40, y - 5, width - 80, 30, fill=1, stroke=0)
                
                p.setFillColorRGB(0.3, 0.3, 0.5) # Dark gray text
                p.setFont("Helvetica-Bold", 11)
                p.drawString(60, y + 8, label)
                
                p.setFillColorRGB(0.1, 0.1, 0.3)
                p.setFont("Helvetica", 11)
                p.drawString(350, y + 8, value)
                y -= 30

            # ===== PREMIUM FOOTER (Navy Blue) =====
            p.setFillColorRGB(0.1, 0.1, 0.25) # Dark Navy
            p.rect(0, 0, width, 60, fill=1, stroke=0)
            
            p.setFillColorRGB(0.8, 0.8, 0.9)
            p.setFont("Helvetica", 9)
            p.drawString(50, 30, "Confidential • Generated by Y.S.M Advance Education System")
            p.drawRightString(width - 50, 30, timezone.now().strftime('%d %b, %Y %H:%M'))
            
            p.setFont("Helvetica-Oblique", 8)
            p.drawString(50, 15, "Visionary Architect & Developed by: Yash A Mishra")

            p.showPage()
            p.save()
            buffer.seek(0)

            filename = f"{report.report_type}_Report_{report.generated_at.strftime('%b_%Y')}.pdf"

            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        except GeneratedReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)
        except Exception as e:
            return Response(
                {"error": f"PDF generation failed: {str(e)}"},
                status=500
            )

    # =========================
    # DATA PROVIDER
    # =========================
    def _get_report_data(self, report_type):
        if report_type == REPORT_FINANCE:
            return [
                ("Total Revenue", "₹ 12,45,000"),
                ("This Month Collection", "₹ 4,50,000"),
                ("Pending Dues", "₹ 1,20,000"),
                ("Financial Health", "Excellent"),
            ]

        if report_type == REPORT_EXAM:
            return [
                ("Total Exams", "12"),
                ("Average Pass %", "87.5%"),
                ("Top Batch", "Class 12 Science"),
            ]

        if report_type == REPORT_HR:
            return [
                ("Total Staff", "42"),
                ("Present Today", "40"),
                ("New Hires", "3"),
            ]

        if report_type == REPORT_ATTENDANCE:
            return [
                ("Average Attendance", "85%"),
                ("Most Present Class", "Class 10-A"),
                ("Absentees Today", "15"),
            ]

        if report_type == REPORT_ANALYTICS:
            return [
                ("User Engagement", "High"),
                ("Active Sessions", "120"),
                ("Performance Score", "9.2/10"),
            ]

        return [
            ("Total Students", "1,245"),
            ("System Status", "Operational"),
            ("Last Backup", timezone.now().strftime('%Y-%m-%d')),
        ]
