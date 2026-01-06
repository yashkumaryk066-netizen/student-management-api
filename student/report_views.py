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
        from .views import get_owner_user
        owner = get_owner_user(request.user)
        
        reports = (
            GeneratedReport.objects
            .filter(created_by=owner)
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
        from .views import get_owner_user
        owner = get_owner_user(request.user)
        
        report = GeneratedReport.objects.create(
            user=request.user,
            created_by=owner,
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
            from .views import get_owner_user
            owner = get_owner_user(request.user)
            report = GeneratedReport.objects.get(pk=pk, created_by=owner)

            if report.status != REPORT_READY:
                return Response(
                    {"error": "Report is still generating"},
                    status=409
                )

            buffer = io.BytesIO()
            # letter size is 612 x 792 points
            p = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter

            # ==========================================
            # PAGE 1: CINEMATIC COVER PAGE
            # ==========================================
            # Deep Galaxy/Navy Background
            p.setFillColorRGB(0.02, 0.02, 0.1) 
            p.rect(0, 0, width, height, fill=1, stroke=0)
            
            # Sublte Glow/Gradient pattern (simulated with rects)
            p.setFillColorRGB(0.04, 0.04, 0.15)
            p.rect(0, height*0.4, width, height*0.6, fill=1, stroke=0)

            # Central Branding Circle
            p.setFillColorRGB(0.85, 0.65, 0.1) # Gold
            p.setStrokeColorRGB(0.85, 0.65, 0.1)
            p.setLineWidth(1)
            p.circle(width/2, height/2 + 100, 70, fill=0, stroke=1)
            
            # Official Logo
            logo_path = os.path.join(settings.BASE_DIR, 'static/img/ysm_logo.png')
            if os.path.exists(logo_path):
                p.drawImage(logo_path, width/2 - 50, height/2 + 50, width=100, height=100, mask='auto', preserveAspectRatio=True)

            # Main Title - Cover
            p.setFillColorRGB(1, 1, 1)
            p.setFont("Helvetica-Bold", 32)
            p.drawCentredString(width/2, height/2 - 30, "Y.S.M")
            
            p.setFont("Helvetica-Bold", 18)
            p.setFillColorRGB(0.9, 0.7, 0.2) # Gold
            p.drawCentredString(width/2, height/2 - 60, "ADVANCE EDUCATION SYSTEM")
            
            # Report Category
            p.setStrokeColorRGB(1, 1, 1)
            p.setLineWidth(0.5)
            p.line(width/2 - 100, height/2 - 100, width/2 + 100, height/2 - 100)
            
            p.setFillColorRGB(0.8, 0.8, 0.9)
            p.setFont("Helvetica", 16)
            p.drawCentredString(width/2, height/2 - 130, f"{report.report_type.replace('_', ' ').upper()}")
            
            # Footer Branding - Cover
            p.setFont("Helvetica-Oblique", 10)
            p.setFillColorRGB(0.6, 0.6, 0.7)
            p.drawCentredString(width/2, 80, f"Generated on: {timezone.now().strftime('%d %B, %Y')}")
            p.drawCentredString(width/2, 60, "Confidential • Proprietary Intelligence")
            
            p.showPage() # End Cover Page

            # ==========================================
            # PAGE 2: ANALYTICS DASHBOARD PAGE
            # ==========================================
            # Premium Header (Dark Navy)
            header_h = 100
            p.setFillColorRGB(0.02, 0.02, 0.12)
            p.rect(0, height - header_h, width, header_h, fill=1, stroke=0)
            
            # Logo in Header
            if os.path.exists(logo_path):
                p.drawImage(logo_path, 30, height - 85, width=60, height=60, mask='auto', preserveAspectRatio=True)
            
            # Brand Text in Header
            p.setFillColorRGB(1, 1, 1)
            p.setFont("Helvetica-Bold", 18)
            p.drawString(100, height - 55, "Y.S.M ADVANCE")
            p.setFont("Helvetica", 10)
            p.setFillColorRGB(0.9, 0.7, 0.2)
            p.drawString(100, height - 70, "EDUCATION MANAGEMENT SYSTEM")

            # Report Meta (Right Side)
            p.setFillColorRGB(1, 1, 1)
            p.setFont("Helvetica-Bold", 10)
            p.drawRightString(width - 30, height - 45, report.name)
            p.setFont("Helvetica", 9)
            p.drawRightString(width - 30, height - 60, f"Issued To: {request.user.email}")
            
            # Data Visual Section Header
            y = height - 160
            p.setFillColorRGB(0.1, 0.1, 0.3)
            p.setFont("Helvetica-Bold", 16)
            p.drawString(30, y, "Performance Insights")
            
            # Horizontal Divider with gold accents
            p.setStrokeColorRGB(0.85, 0.65, 0.1)
            p.setLineWidth(2)
            p.line(30, y - 10, 80, y - 10)
            p.setStrokeColorRGB(0.9, 0.9, 0.9)
            p.setLineWidth(0.5)
            p.line(80, y - 10, width - 30, y - 10)

            # --- KPI CARDS GRID ---
            y -= 60
            data_points = self._get_report_data(report.report_type)
            
            # Grid config: 2 columns
            col_width = (width - 90) / 2
            card_h = 80
            
            for i, (label, value) in enumerate(data_points):
                # Calculate pos
                row = i // 2
                col = i % 2
                card_x = 30 + (col * (col_width + 30))
                card_y = y - (row * (card_h + 20))
                
                # Card Background (Soft Slate Gradient feel)
                p.setFillColorRGB(0.96, 0.97, 1.0)
                p.roundRect(card_x, card_y, col_width, card_h, 8, fill=1, stroke=1)
                
                # Card Decorative Left Border (Vibrant)
                colors_grad = [ (0.2, 0.4, 0.8), (0.1, 0.6, 0.4), (0.8, 0.3, 0.2), (0.4, 0.2, 0.7) ]
                p.setFillColorRGB(*colors_grad[i % len(colors_grad)])
                p.roundRect(card_x, card_y, 5, card_h, 4, fill=1, stroke=0)
                
                # Label
                p.setFillColorRGB(0.4, 0.4, 0.5)
                p.setFont("Helvetica-Bold", 9)
                p.drawString(card_x + 20, card_y + card_h - 25, label.upper())
                
                # Value
                p.setFillColorRGB(0.1, 0.1, 0.2)
                p.setFont("Helvetica-Bold", 18)
                p.drawString(card_x + 20, card_y + 20, value)

            # Footer
            p.setFillColorRGB(0.05, 0.05, 0.15)
            p.rect(0, 0, width, 40, fill=1, stroke=0)
            p.setFillColorRGB(1, 1, 1)
            p.setFont("Helvetica-Oblique", 8)
            p.drawCentredString(width/2, 15, "Official Y.S.M Intelligence Document • Visionary Architect: Yash A Mishra")

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
