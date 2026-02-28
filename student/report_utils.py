from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
import os

def generate_admit_card_pdf(student, exams, academic_year="2024-25"):
    """
    Generate Advanced Premium Admit Card (Hall Ticket)
    Dynamically lists real exams from the database.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # COLORS
    BLUE_DARK = colors.HexColor("#0f172a")
    BLUE_LIGHT = colors.HexColor("#3b82f6")
     
    # 1. Background Pattern (Light Watermark)
    c.saveState()
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.setFont("Helvetica-Bold", 60)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.setFillAlpha(0.1)
    c.drawCentredString(0, 0, "Y.S.M ADVANCE")
    c.restoreState()

    # Get Institution Branding
    owner = student.created_by
    inst_name = "Y.S.M ADVANCE EDUCATION"
    logo_path = None
    if hasattr(owner, 'profile'):
        if owner.profile.institution_name:
            inst_name = owner.profile.institution_name.upper()
        if owner.profile.institution_logo and hasattr(owner.profile.institution_logo, 'path'):
            if os.path.exists(owner.profile.institution_logo.path):
                logo_path = owner.profile.institution_logo.path

    # 2. Header (Formal & Premium)
    c.setFillColor(BLUE_DARK)
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    # Draw Logo in Header
    if logo_path:
        try:
            from reportlab.lib.utils import ImageReader
            logo = ImageReader(logo_path)
            c.drawImage(logo, 40, height - 100, width=80, height=80, mask='auto', preserveAspectRatio=True)
        except: pass

    c.setFillColor(colors.white)
    font_size = 24 if len(inst_name) < 30 else 18
    c.setFont("Helvetica-Bold", font_size)
    c.drawCentredString(width/2 + 20, height - 45, inst_name)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2 + 20, height - 68, "EXAMINATION HALL TICKET")
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width/2 + 20, height - 85, f"Academic Year {academic_year}")

    # 3. Candidate Info Section
    box_top = height - 140
    c.setStrokeColor(BLUE_LIGHT)
    c.setLineWidth(1)
    c.rect(40, box_top - 160, width - 80, 150, stroke=1, fill=0)
    
    # Photo Frame
    c.rect(60, box_top - 145, 90, 110, stroke=1, fill=0)
    if student.photo and hasattr(student.photo, 'path'):
         try:
             from reportlab.lib.utils import ImageReader
             if os.path.exists(student.photo.path):
                img = ImageReader(student.photo.path)
                c.drawImage(img, 62, box_top - 143, width=86, height=106, preserveAspectRatio=True, anchor='c')
         except:
             c.setFont("Helvetica", 8)
             c.drawCentredString(105, box_top - 90, "Photo Error")
    else:
         c.setFont("Helvetica", 8)
         c.drawCentredString(105, box_top - 90, "No Photo")
    
    # Details Text
    text_x = 170
    line_start = box_top - 40
    line_h = 22
    
    c.setFillColor(colors.black)
    def draw_row(label, value, y):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(text_x, y, label)
        c.setFont("Helvetica", 11)
        c.drawString(text_x + 110, y, ": " + str(value))
        
    draw_row("Candidate Name", student.name.upper(), line_start)
    draw_row("Roll Number", student.roll_number or "N/A", line_start - line_h)
    draw_row("Class / Grade", student.grade, line_start - line_h*2)
    draw_row("Institution Type", student.get_institution_type_display(), line_start - line_h*3)
    draw_row("Center Type", "Main Campus", line_start - line_h*4)
    
    # 4. Timetable (Dynamic)
    table_y = box_top - 180
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(BLUE_DARK)
    c.drawString(40, table_y, "EXAMINATION SCHEDULE")
    
    table_data = [['Date', 'Subject', 'Exam Type', 'Max Marks', 'Time']]
    if not exams:
        table_data.append(['N/A', 'No exams scheduled', '-', '-', '-'])
    else:
        for ex in exams:
            table_data.append([
                ex.exam_date.strftime('%d %b, %y'),
                ex.subject.name if ex.subject else ex.name[:18],
                ex.get_exam_type_display(),
                str(ex.total_marks),
                "10:00 AM"
            ])
    
    t = Table(table_data, colWidths=[80, 150, 100, 80, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BLUE_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    
    t_height = len(table_data) * 26
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, table_y - t_height - 10)
    
    # 5. Instructions & Security
    curr_y = table_y - t_height - 50
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, curr_y, "INSTRUCTIONS TO CANDIDATES")
    c.setFont("Helvetica", 9)
    instructions = [
        "1. Carrying a physical copy of this Admit Card is mandatory.",
        "2. Candidates must reach the examination hall 30 minutes prior.",
        "3. Any form of cheating or electronic equipment is strictly prohibited.",
        "4. This ticket is digitally verified and valid for the 2024-25 session."
    ]
    for i in instructions:
        curr_y -= 15
        c.drawString(40, curr_y, i)
        
    # 6. Signatures
    sig_y = 60
    c.setLineWidth(0.5)
    c.line(50, sig_y + 30, 160, sig_y + 30)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(105, sig_y + 15, "Candidate Signature")
    
    if hasattr(owner, 'profile') and owner.profile.digital_signature:
        try:
            sig_path = owner.profile.digital_signature.path
            if os.path.exists(sig_path):
                c.drawImage(sig_path, width - 170, sig_y + 35, width=90, height=40, preserveAspectRatio=True, mask='auto')
        except: pass

    c.line(width - 180, sig_y + 30, width - 60, sig_y + 30)
    c.drawCentredString(width - 120, sig_y + 15, "Controller of Exams")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_report_card_pdf(student, grades):
    """
    Generate Detailed, Branded Report Card with real-time performance analytics.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # THEME COLORS
    PRIMARY = colors.HexColor("#1e3a8a")
    SECONDARY = colors.HexColor("#dbeafe")
    TEXT = colors.HexColor("#1e293b")
    
    # Watermark
    c.saveState()
    c.translate(width/2, height/2)
    c.rotate(45)
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.setFont("Helvetica-Bold", 80)
    c.drawCentredString(0, 0, "Y.S.M ADVANCE")
    c.restoreState()
    
    # Header Banner
    c.setFillColor(PRIMARY)
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    # Branding
    owner = student.created_by
    inst_name = "ACADEMIC PORTAL"
    logo_path = None
    if hasattr(owner, 'profile'):
        if owner.profile.institution_name:
            inst_name = owner.profile.institution_name.upper()
        if owner.profile.institution_logo and hasattr(owner.profile.institution_logo, 'path'):
            if os.path.exists(owner.profile.institution_logo.path):
                logo_path = owner.profile.institution_logo.path

    # Draw Logo in Header
    if logo_path:
        try:
            from reportlab.lib.utils import ImageReader
            logo = ImageReader(logo_path)
            c.drawImage(logo, 50, height - 100, width=80, height=80, mask='auto', preserveAspectRatio=True)
        except: pass

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2 + 20, height - 50, "PROGRESS REPORT")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2 + 20, height - 80, inst_name)
    
    # Student Info Strip
    c.setFillColor(SECONDARY)
    c.rect(40, height - 200, width - 80, 60, fill=1, stroke=0)
    
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, height - 165, "STUDENT:")
    c.drawString(60, height - 185, "CLASS:")
    c.drawString(320, height - 165, "ROLL NO:")
    c.drawString(320, height - 185, "SESSION:")
    
    c.setFont("Helvetica", 11)
    c.drawString(130, height - 165, student.name.upper())
    c.drawString(130, height - 185, str(student.grade))
    c.drawString(390, height - 165, student.roll_number or "N/A")
    c.drawString(390, height - 185, "2024 - 2025")
    
    # Grades Table
    table_y = height - 230
    header = ['SUBJECT','EXAM','MAX','OBTAINED','GRADE','STATUS']
    data = [header]
    
    total_max = 0
    total_obt = 0
    
    if not grades:
        data.append(['N/A','No records found','-','-','-','-'])
    else:
        for g in grades:
            subj = g.exam.subject.name if g.exam.subject else "General"
            marks = float(g.marks_obtained)
            total = g.exam.total_marks
            pct = (marks/total)*100
            
            # Grade Calculation
            grade = 'A+' if pct >= 90 else 'A' if pct >= 80 else 'B' if pct >= 60 else 'C' if pct >= 40 else 'F'
            
            data.append([subj, g.exam.name[:12], total, marks, grade, g.status])
            total_max += total
            total_obt += marks
    
    # Grand Total
    overall_pct = (total_obt/total_max * 100) if total_max > 0 else 0
    data.append(['GRAND TOTAL', '', total_max, total_obt, f"{overall_pct:.1f}%", ''])

    t = Table(data, colWidths=[120, 100, 70, 70, 70, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#f8fafc")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#b9f6ca")), # Success Row
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    
    t_h = len(data) * 30
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, table_y - t_h)
    
    # Analysis Chart (Visual Feedback)
    chart_y = table_y - t_h - 100
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, chart_y + 70, "PERFORMANCE ANALYTICS")
    
    # Draw Progress Bar
    bar_w = width - 200
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.rect(40, chart_y + 40, bar_w, 20, fill=1, stroke=0)
    
    progress_w = bar_w * (overall_pct/100)
    c.setFillColor(colors.HexColor("#10b981")) # Success Green
    c.rect(40, chart_y + 40, progress_w, 20, fill=1, stroke=0)
    
    c.setFillColor(TEXT)
    c.setFont("Helvetica", 10)
    c.drawString(40 + bar_w + 10, chart_y + 45, f"{overall_pct:.1f}% Complete")
    
    # Remarks Block
    c.setStrokeColor(PRIMARY)
    c.rect(40, chart_y - 60, width - 80, 80, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, chart_y + 5, "Principal's Remarks:")
    
    remark = "Outstanding" if overall_pct >= 90 else "Great effort, keep it up!" if overall_pct >= 75 else "Good progress."
    c.setFont("Helvetica-Oblique", 11)
    c.drawString(60, chart_y - 15, remark)
    
    # Signatures
    sig_y = 60
    if hasattr(owner, 'profile') and owner.profile.digital_signature:
        try:
            if os.path.exists(owner.profile.digital_signature.path):
                c.drawImage(owner.profile.digital_signature.path, width - 150, sig_y + 35, width=80, height=35, preserveAspectRatio=True, mask='auto')
        except: pass
        
    c.line(40, sig_y + 30, 150, sig_y + 30)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(55, sig_y + 15, "Class Teacher")
    
    c.line(width - 150, sig_y + 30, width - 40, sig_y + 30)
    c.drawString(width - 120, sig_y + 15, "Principal")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
