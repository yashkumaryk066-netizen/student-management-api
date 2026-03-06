import io
import os
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_online_exam_certificate_pdf(attempt):
    """Generates an aesthetic Online Exam Certificate PDF using ReportLab"""
    buffer = io.BytesIO()
    
    # 11 x 8.5 inches (landscape)
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Background Colors & Border
    c.setFillColor(colors.HexColor('#111827')) # Very dark blue
    c.rect(0, 0, width, height, stroke=False, fill=True)
    
    # Inner border
    c.setStrokeColor(colors.HexColor('#3b82f6')) # Blue accent
    c.setLineWidth(3)
    c.rect(20, 20, width-40, height-40, stroke=True, fill=False)
    
    # Secondary inner border
    c.setStrokeColor(colors.HexColor('#eab308')) # Gold/Yellow accent
    c.setLineWidth(1)
    c.rect(25, 25, width-50, height-50, stroke=True, fill=False)

    # Logo / Header
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, width/2.0 - 50, height - 120, width=100, height=100, preserveAspectRatio=True, mask='auto')
        except:
            pass
            
    # Title
    c.setFillColor(colors.HexColor('#f3f4f6'))
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(width/2.0, height - 180, "CERTIFICATE OF EXCELLENCE")
    
    c.setFillColor(colors.HexColor('#9ca3af'))
    c.setFont("Helvetica-Oblique", 16)
    c.drawCentredString(width/2.0, height - 210, "THIS IS PROUDLY PRESENTED TO")
    
    # Student Name
    c.setFillColor(colors.HexColor('#eab308'))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2.0, height - 260, attempt.student.name.upper())
    
    # Divider line
    c.setStrokeColor(colors.HexColor('#374151'))
    c.line(width/2.0 - 200, height - 280, width/2.0 + 200, height - 280)
    
    # Description
    c.setFillColor(colors.HexColor('#f3f4f6'))
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2.0, height - 320, f"For successfully completing the rigorous online examination:")
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2.0, height - 360, f"{attempt.exam.title}")

    # Sub details
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2.0, height - 400, f"Subject: {attempt.exam.subject.name if attempt.exam.subject else 'General'}")
    
    # Score details
    c.setFillColor(colors.HexColor('#10b981')) # Green
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2.0, height - 440, f"Score Achieved: {attempt.score_obtained} / {attempt.exam.total_marks}")
    
    # AI Graded badge logic
    if attempt.is_ai_graded:
         c.setFillColor(colors.HexColor('#8b5cf6')) # Purple
         c.setFont("Helvetica-Bold", 12)
         c.drawCentredString(width/2.0, height - 470, f"★ Certified via Y.S.M Sovereign AI Evaluation ★")

    # Bottom Signatures
    c.setFillColor(colors.HexColor('#9ca3af'))
    c.setFont("Helvetica", 12)
    
    c.line(100, 80, 250, 80)
    c.drawCentredString(175, 60, "Date Evaluated")
    c.drawCentredString(175, 45, str(attempt.submitted_at.strftime('%B %d, %Y') if attempt.submitted_at else "N/A"))
    
    c.line(width - 250, 80, width - 100, 80)
    c.drawCentredString(width - 175, 60, "Authorized Signature")
    c.drawCentredString(width - 175, 45, "Y.S.M AI Platform")
    
    # Tracking ID
    c.setFillColor(colors.HexColor('#4b5563'))
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2.0, 30, f"Certificate ID: CERT-{attempt.id}-{attempt.exam.id} | Verifiable via Y.S.M Systems")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.getvalue()
