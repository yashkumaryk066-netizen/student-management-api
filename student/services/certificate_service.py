from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import os
from django.conf import settings

def generate_certificate_pdf(student, cert_type):
    """
    Generate Transfer or Character Certificate.
    """
    buffer = BytesIO()
    # Landscape A4 for classic certificate look
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # --- BORDER ---
    # Double border
    c.setStrokeColor(colors.HexColor('#1e3a8a')) # Deep Blue
    c.setLineWidth(5)
    c.rect(20, 20, width-40, height-40)
    
    c.setStrokeColor(colors.HexColor('#fbbf24')) # Gold
    c.setLineWidth(2)
    c.rect(30, 30, width-60, height-60)
    
    # --- WATERMARK ---
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(30)
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.setFont("Helvetica-Bold", 100)
    c.drawCentredString(0, 0, "Y.S.M OFFICIAL")
    c.restoreState()
    
    # --- HEADER / BRANDING ---
    # Get Institution Details from Creator
    owner = student.created_by
    inst_name = "Y.S.M ADVANCE EDUCATION"
    inst_addr = "Knowledge Campus, India"
    logo_path = None
    
    if hasattr(owner, 'profile'):
        if owner.profile.institution_name:
            inst_name = owner.profile.institution_name.upper()
        if owner.profile.address:
            inst_addr = owner.profile.address
        if owner.profile.institution_logo and hasattr(owner.profile.institution_logo, 'path'):
             if os.path.exists(owner.profile.institution_logo.path):
                 logo_path = owner.profile.institution_logo.path

    # Logo
    if logo_path:
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, width/2 - 40, height - 130, width=80, height=80, mask='auto', preserveAspectRatio=True)
        except:
            pass
            
    # Title
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height - 160, inst_name)
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 185, inst_addr)
    
    # Certificate Title
    title_map = {
        'TC': 'TRANSFER CERTIFICATE',
        'CC': 'CHARACTER CERTIFICATE',
        'BONAFIDE': 'BONAFIDE STUDENT CERTIFICATE'
    }
    cert_title = title_map.get(cert_type, 'CERTIFICATE OF ACHIEVEMENT')
    
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor('#b45309')) # Bronze/Gold
    c.drawCentredString(width/2, height - 250, cert_title)
    
    # --- BODY TEXT ---
    c.setFillColor(colors.black)
    c.setFont("Times-Roman", 18)
    
    text_y = height - 320
    spacing = 35
    
    # Dynamic Text construction
    c.drawCentredString(width/2, text_y, "This is to certify that")
    text_y -= spacing
    
    c.setFont("Times-BoldItalic", 24)
    c.drawCentredString(width/2, text_y, student.name)
    c.line(width/2 - 150, text_y - 5, width/2 + 150, text_y - 5) # Underline
    text_y -= spacing
    
    c.setFont("Times-Roman", 18)
    parent_name = student.parent.get_full_name() if student.parent else (student.relation or "Parent/Guardian")
    c.drawCentredString(width/2, text_y, f"Son/Daughter of {parent_name}")
    text_y -= spacing
    
    if cert_type == 'TC':
        c.drawCentredString(width/2, text_y, f"was a student of Class {student.grade} in this institution.")
        text_y -= spacing
        c.drawCentredString(width/2, text_y, "He/She has paid all dues and bears a good moral character.")
    elif cert_type == 'CC':
        c.drawCentredString(width/2, text_y, f"is a bonafide student of Class {student.grade}.")
        text_y -= spacing
        c.drawCentredString(width/2, text_y, "To the best of our knowledge, he/she bears a good moral character.")
    else:
        c.drawCentredString(width/2, text_y, f"is a student of Class {student.grade} (Roll: {student.roll_number or 'N/A'}).")
        
    text_y -= (spacing * 2)
    
    # --- SIGNATURES ---
    from datetime import date
    c.setFont("Helvetica-Bold", 12)
    
    # Date
    c.drawString(100, 100, f"Date: {date.today().strftime('%d-%b-%Y')}")
    
    # Principal Sig
    c.drawRightString(width - 100, 100, "Principal / Authorized Signatory")
    c.line(width - 300, 115, width - 80, 115)
    
    # Digital Sig Image if available
    sig_path = None
    if hasattr(owner, 'profile') and owner.profile.digital_signature:
         if hasattr(owner.profile.digital_signature, 'path') and os.path.exists(owner.profile.digital_signature.path):
             sig_path = owner.profile.digital_signature.path
             
    if sig_path:
        try:
            sig = ImageReader(sig_path)
            c.drawImage(sig, width - 250, 120, width=100, height=50, mask='auto', preserveAspectRatio=True)
        except:
            pass

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_exam_certificate_pdf(attempt):
    """
    Generate an Achievement Certificate for a specific Online Exam attempt.
    """
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    import os
    from datetime import date
    
    student = attempt.student
    exam = attempt.exam
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # --- PREMIUM BORDER ---
    c.setStrokeColor(colors.HexColor('#0f172a')) # Slate 900
    c.setLineWidth(12)
    c.rect(10, 10, width-20, height-20)
    
    c.setStrokeColor(colors.HexColor('#3b82f6')) # Blue 500
    c.setLineWidth(3)
    c.rect(25, 25, width-50, height-50)
    
    # --- SOVEREIGN SEAL WATERMARK ---
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(35)
    c.setFillColorRGB(0.95, 0.95, 1.0) # Very light blue
    c.setFont("Helvetica-Bold", 80)
    c.drawCentredString(0, 0, "SOVEREIGN AI VERIFIED")
    c.restoreState()
    
    # --- INSTITUTION HEADER ---
    owner = exam.created_by
    inst_name = "Y.S.M ADVANCE EDUCATION"
    if hasattr(owner, 'profile') and owner.profile.institution_name:
        inst_name = owner.profile.institution_name.upper()
        
    c.setFillColor(colors.HexColor('#1e293b'))
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width/2, height - 120, inst_name)
    
    # --- TITLE ---
    c.setFillColor(colors.HexColor('#2563eb'))
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(width/2, height - 200, "CERTIFICATE OF ACHIEVEMENT")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height - 250, "This is to certify that")
    
    # --- STUDENT NAME ---
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.HexColor('#0f172a'))
    c.drawCentredString(width/2, height - 300, student.name.upper())
    c.line(width/2 - 200, height - 310, width/2 + 200, height - 310)
    
    # --- BODY ---
    c.setFont("Helvetica", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height - 360, "has successfully completed the online proctored examination")
    
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height - 400, f"'{exam.title}'")
    
    # --- PERFORMANCE ---
    c.setFont("Helvetica", 18)
    score_percent = (attempt.score_obtained / exam.total_marks) * 100
    c.drawCentredString(width/2, height - 440, f"Score Obtained: {attempt.score_obtained} / {exam.total_marks} ({score_percent:.1f}%)")
    
    # --- FOOTER & SIGNATURES ---
    c.setFont("Helvetica", 12)
    c.drawString(80, 100, f"Issue Date: {date.today().strftime('%d %b, %Y')}")
    c.drawString(80, 80, f"Certificate ID: YSM-{attempt.id}-{timezone.now().strftime('%Y%m%d')}")
    
    c.drawRightString(width - 80, 100, "Examination Controller")
    c.line(width - 250, 115, width - 80, 115)
    
    # AI Verify Seal Placeholder
    c.setFillColor(colors.HexColor('#10b981')) # Emerald 500
    c.rect(width/2 - 50, 50, 100, 30, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, 60, "AI PROCTOR VERIFIED")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_exam_admit_card_pdf(student, exam):
    """
    Generate a Premium Online Exam Admit Card for a student.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader
    import os
    from datetime import date
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- SCANLINE BG EFFECT ---
    c.setStrokeColor(colors.HexColor('#e2e8f0'))
    for i in range(0, int(height), 20):
        c.setLineWidth(0.5)
        c.line(0, i, width, i)

    # --- BORDER ---
    c.setStrokeColor(colors.HexColor('#1e40af'))
    c.setLineWidth(2)
    c.rect(40, 40, width-80, height-80)
    
    # --- HEADER ---
    owner = exam.created_by
    inst_name = "Y.S.M ADVANCE EDUCATION"
    if hasattr(owner, 'profile') and owner.profile.institution_name:
        inst_name = owner.profile.institution_name.upper()

    c.setFillColor(colors.HexColor('#1e3a8a'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 80, inst_name)
    
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height - 110, "OFFICIAL EXAMINATION ADMIT CARD")
    
    # --- STUDENT PHOTO PLACEHOLDER ---
    c.rect(width - 150, height - 250, 100, 120)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width - 100, height - 265, "PASSPORT PHOTO")
    
    # --- EXAM DETAILS ---
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, height - 160, f"EXAMINATION: {exam.title.upper()}")
    c.drawString(60, height - 180, f"SUBJECT: {exam.subject.name.upper()}")
    
    # --- CORE VERIFICATION DATA ---
    c.setLineWidth(1)
    c.line(60, height - 200, width - 180, height - 200)
    
    c.setFont("Helvetica", 12)
    y = height - 230
    details = [
        ("STUDENT NAME", student.name.upper()),
        ("ROLL NUMBER", student.roll_number or "N/A"),
        ("ROLL CODE", exam.roll_code),
        ("EXAM DATE", exam.start_window.strftime("%d %b, %Y") if exam.start_window else "N/A"),
        ("EXAM TIME", exam.start_window.strftime("%H:%M %p") if exam.start_window else "N/A"),
        ("DURATION", f"{exam.duration_minutes} Minutes"),
    ]
    
    for label, val in details:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, f"{label}:")
        c.setFont("Helvetica", 11)
        c.drawString(200, y, str(val))
        y -= 25

    # --- IMPORTANT INSTRUCTIONS ---
    y -= 20
    c.setFillColor(colors.HexColor('#ef4444'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, y, "MANDATORY INSTRUCTIONS:")
    c.setFillColor(colors.black)
    y -= 20
    
    instructions = [
        "1. Entry to the exam terminal requires both Roll Number and Roll Code.",
        "2. Any attempt to switch tabs or minimize the browser will trigger a security violation.",
        "3. System will auto-submit exam after 3 violations.",
        "4. Stable internet connection is mandatory for AI proctoring services.",
        "5. Result will be securely released 5 hours after the examination window ends."
    ]
    
    c.setFont("Helvetica", 10)
    for inst in instructions:
        c.drawString(60, y, inst)
        y -= 18

    # --- QR CODE PLACEHOLDER / SEAL ---
    c.setStrokeColor(colors.black)
    c.rect(width - 150, 60, 100, 100)
    c.setFont("Helvetica", 7)
    c.drawCentredString(width - 100, 70, "SECURE VERIFICATION QR")
    
    # Footer
    c.saveState()
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 50, "This is an AI-Generated document. Physical signature is not required.")
    c.restoreState()

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_merit_list_pdf(exam, ranked_attempts):
    """
    Generate a Premium Merit List / Hall of Fame PDF for an exam.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle
    
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- HEADER SECTION ---
    c.setFillColor(colors.HexColor('#1e3a8a'))
    c.rect(0, height - 150, width, 150, fill=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 60, "OFFICIAL MERIT LIST")
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 90, f"Examination: {exam.title}")
    c.setFont("Helvetica-Oblique", 12)
    c.drawCentredString(width/2, height - 120, f"Subject: {exam.subject.name} | Batch: {', '.join([b.name for b in exam.assigned_batches.all()])}")

    # --- TOP 3 HIGHLIGHTS (The Podium) ---
    y = height - 250
    if len(ranked_attempts) >= 1:
        # GOLD
        c.setFillColor(colors.HexColor('#fbbf24')) # Gold
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, y, "RANK 1 (GOLD)")
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.black)
        c.drawCentredString(width/2, y - 30, ranked_attempts[0]['student_name'].upper())
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, y - 50, f"Score: {ranked_attempts[0]['score']} / {exam.total_marks}")
        
    # Silver & Bronze
    y -= 100
    if len(ranked_attempts) >= 2:
        c.setFillColor(colors.HexColor('#94a3b8')) # Silver
        c.drawString(100, y, "RANK 2 (SILVER)")
        c.setFillColor(colors.black)
        c.drawString(100, y - 20, ranked_attempts[1]['student_name'])
        
    if len(ranked_attempts) >= 3:
        c.setFillColor(colors.HexColor('#b45309')) # Bronze
        c.drawRightString(width - 100, y, "RANK 3 (BRONZE)")
        c.setFillColor(colors.black)
        c.drawRightString(width - 100, y - 20, ranked_attempts[2]['student_name'])

    # --- FULL MERIT TABLE ---
    y -= 80
    data = [["Rank", "Roll No", "Student Name", "Score", "Percent", "Status"]]
    for i, att in enumerate(ranked_attempts):
        percent = (float(att['score']) / float(exam.total_marks)) * 100
        data.append([
            str(i+1),
            att['roll_number'],
            att['student_name'],
            str(att['score']),
            f"{percent:.1f}%",
            "PASSED" if percent >= exam.passing_percentage else "FAILED"
        ])
    
    table_height = len(data) * 20
    table = Table(data, colWidths=[50, 80, 200, 60, 60, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')])
    ]))
    
    table.wrapOn(c, width, height)
    table.drawOn(c, 40, y - table_height)

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 30, "AI-Generated Merit List | Verified by Y.S.M ERP Digital Proctoring")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
