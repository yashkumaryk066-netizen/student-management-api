from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, mm
from django.utils import timezone
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle

def generate_admit_card_pdf(student, exam_name, exam_date, center):
    """
    Generate Advanced Premium Admit Card (Hall Ticket)
    Professional Exam Controller Style
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # COLORS
    BLUE_DARK = colors.HexColor("#0f172a")
    BLUE_LIGHT = colors.HexColor("#3b82f6")
    GRAY_BG = colors.HexColor("#f8fafc")
    
    # 1. Background Pattern (Light Watermark)
    c.saveState()
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.setFont("Helvetica-Bold", 60)
    c.translate(width/2, height/2)
    c.rotate(45)
    c.setFillAlpha(0.1)
    c.drawCentredString(0, 0, "OFFICIAL COPY")
    c.restoreState()

    # Get Institution Name
    owner = student.created_by
    inst_name = "Y.S.M ADVANCE EDUCATION" # Default
    if hasattr(owner, 'profile') and owner.profile.institution_name:
        inst_name = owner.profile.institution_name.upper()

    # 2. Header (Formal)
    c.setFillColor(BLUE_DARK)
    c.rect(0, height - 140, width, 140, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFillColor(colors.white)
    
    # Dynamic Sizing
    font_size = 26
    if len(inst_name) > 25: font_size = 18
    if len(inst_name) > 40: font_size = 14
    
    c.setFont("Helvetica-Bold", font_size)
    c.drawCentredString(width/2, height - 50, inst_name)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 75, "HALL TICKET / ADMIT CARD")
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, height - 95, "Academic Year 2024-2025")

    # 3. Candidate & Exam Info Box
    box_top = height - 160
    c.setStrokeColor(BLUE_LIGHT)
    c.setLineWidth(1.5)
    c.rect(40, box_top - 180, width - 80, 180, stroke=1, fill=0)
    
    # Left Side: Photo placeholder
    c.rect(60, box_top - 160, 100, 120, stroke=1, fill=0)
    
    if student.photo:
         try:
             # Draw the actual uploaded photo
             from reportlab.lib.utils import ImageReader
             img = ImageReader(student.photo.path)
             c.drawImage(img, 60, box_top - 160, width=100, height=120, preserveAspectRatio=True, anchor='c')
         except Exception as e:
             # Fallback if image fails
             c.setFont("Helvetica", 8)
             c.drawCentredString(110, box_top - 100, "Photo Error")
    else:
         c.setFont("Helvetica", 8)
         c.drawCentredString(110, box_top - 100, "Affix Photo Here")
    
    # Right Side: Details
    text_x = 180
    line_start = box_top - 40
    line_h = 25
    
    c.setFillColor(colors.black)
    
    def draw_row(label, value, y):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(text_x, y, label)
        c.setFont("Helvetica", 12)
        c.drawString(text_x + 120, y, ": " + str(value))
        
    draw_row("Candidate Name", student.name.upper(), line_start)
    draw_row("Roll Number", student.roll_number or "N/A", line_start - line_h)
    draw_row("Class / Grade", student.grade, line_start - line_h*2)
    draw_row("Examination", exam_name, line_start - line_h*3)
    draw_row("Exam Center", center, line_start - line_h*4)
    
    # 4. Timetable Table
    table_y = box_top - 220
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, table_y, "EXAMINATION SCHEDULE")
    
    data = [
        ['Date', 'Time', 'Subject', 'Sup. Sign'],
        ['15/03/2025', '10:00 AM - 01:00 PM', 'Mathematics', ''],
        ['17/03/2025', '10:00 AM - 01:00 PM', 'Physics', ''],
        ['19/03/2025', '10:00 AM - 01:00 PM', 'Chemistry', ''],
        ['21/03/2025', '10:00 AM - 01:00 PM', 'English', ''],
    ]
    
    t = Table(data, colWidths=[100, 140, 150, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BLUE_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    t.wrapOn(c, width, height)
    t.drawOn(c, 40, table_y - 120)
    
    # 5. Instructions
    inst_y = table_y - 160
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, inst_y, "IMPORTANT INSTRUCTIONS TO CANDIDATES")
    
    instructions = [
        "1. Candidates must carry this Admit Card to the examination hall.",
        "2. Candidates should reach the center at least 30 minutes before commencement.",
        "3. Electronic gadgets including mobile phones are strictly prohibited.",
        "4. Any malice or cheating will lead to immediate disqualification."
    ]
    
    c.setFont("Helvetica", 10)
    curr_y = inst_y - 20
    for i in instructions:
        c.drawString(40, curr_y, i)
        curr_y -= 15
        
    # 6. Signatures
    sig_y = 60
    c.line(50, sig_y + 30, 150, sig_y + 30)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(100, sig_y + 15, "Student Signature")
    
    c.line(width - 150, sig_y + 30, width - 50, sig_y + 30)
    c.drawCentredString(width - 100, sig_y + 15, "Controller of Exams")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_report_card_pdf(student, exam_results):
    """
    Generate Detailed, Graphics-Rich Report Card
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # --- HEADER SECTION (Color Block) ---
    c.setFillColor(colors.HexColor("#1e3a8a")) # Royal Blue
    c.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    # Title
    c.setFillColor(colors.white)
    # Get Institution Name
    owner = student.created_by
    inst_name = "REPORT CARD" # Default Title
    sub_title = "Y.S.M ADVANCE EDUCATION"
    
    if hasattr(owner, 'profile') and owner.profile.institution_name:
        sub_title = owner.profile.institution_name.upper()

    # Title
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 40, "REPORT CARD") # Keep Report Card as main title
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 65, sub_title) # Inst Name as Subtitle for Report Card
    c.drawCentredString(width/2, height - 75, "SESSION: 2024 - 2025")
    
    # --- STUDENT PROFILE STRIP ---
    c.setFillColor(colors.HexColor("#f1f5f9"))
    c.rect(0, height - 200, width, 80, fill=1, stroke=0)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    
    # Column 1
    c.drawString(50, height - 150, "NAME:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, student.name.upper())
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 175, "CLASS:")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 175, student.grade)
    
    # Column 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, height - 150, "ROLL NO:")
    c.setFont("Helvetica", 12)
    c.drawString(430, height - 150, str(student.roll_number))
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, height - 175, "DOB:")
    c.setFont("Helvetica", 12)
    c.drawString(430, height - 175, str(student.dob))
    
    # --- ACADEMIC PERFORMANCE TABLE ---
    table_top = height - 250
    
    data = [['SUBJECT', 'MAX MARKS', 'OBTAINED', 'GRADE', 'REMARKS']]
    total_max = 0
    total_obt = 0
    
    for res in exam_results:
        pct = (res['marks'] / res['total']) * 100
        grade = 'A+' if pct >= 90 else 'A' if pct >= 80 else 'B' if pct >= 60 else 'C' if pct >= 40 else 'F'
        remark = "Excellent" if grade.startswith('A') else "Good" if grade == 'B' else "Needs Imp."
        
        data.append([
            res['subject'], 
            res['total'], 
            res['marks'], 
            grade,
            remark
        ])
        total_max += res['total']
        total_obt += res['marks']
        
    # Grand Total
    overall_pct = (total_obt / total_max * 100) if total_max > 0 else 0
    overall_grade = 'A+' if overall_pct >= 90 else 'A' if overall_pct >= 80 else 'B'
    data.append(['GRAND TOTAL', total_max, total_obt, overall_grade, f"{overall_pct:.1f}%"])
    
    t = Table(data, colWidths=[150, 80, 80, 80, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#f8fafc")]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#dbeafe")), # Total Row
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    
    t.wrapOn(c, width, height)
    t.drawOn(c, (width - 490)/2, table_top - (len(data)*20))
    
    # --- PERFORMANCE GRAPH (Simulated) ---
    graph_y = 200
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, graph_y + 100, "PERFORMANCE ANALYSIS")
    
    # Draw simple bar chart bars
    bar_x = 50
    c.setLineWidth(0)
    for res in exam_results:
        pct = (res['marks'] / res['total']) * 100
        bar_height = pct * 0.8 # Scale
        
        # Bar Label
        c.setFont("Helvetica", 8)
        c.drawCentredString(bar_x + 15, graph_y, res['subject'][:3])
        
        # Bar Rect
        c.setFillColor(colors.HexColor("#3b82f6"))
        c.rect(bar_x, graph_y + 10, 30, bar_height, fill=1, stroke=0)
        
        c.setFillColor(colors.black)
        c.drawCentredString(bar_x + 15, graph_y + 10 + bar_height + 2, str(int(pct)) + "%")
        
        bar_x += 50
        
    # --- FOOTER / SIGNATURES ---
    sig_y = 80
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    
    c.line(50, sig_y, 150, sig_y)
    c.drawString(60, sig_y - 15, "Class Teacher")
    
    c.line(220, sig_y, 320, sig_y)
    c.drawString(245, sig_y - 15, "Exam Cell")
    
    c.line(400, sig_y, 500, sig_y)
    c.drawString(425, sig_y - 15, "Principal")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 20, "This is a computer-generated document. No signature required.")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
