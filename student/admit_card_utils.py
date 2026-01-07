from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as PlatypusImage
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from django.utils import timezone
from .models import Exam
try:
    from reportlab.lib.utils import ImageReader
except ImportError:
    ImageReader = None

def generate_admit_card_pdf(student):
    """
    Generate Exam Hall Ticket / Admit Card
    Lists all upcoming exams for the student's grade/batch.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    elements = []
    
    # --- HEADER ---
    # Institute Name
    header_style = ParagraphStyle('Header', parent=styles['Heading1'], fontSize=20, alignment=TA_CENTER, textColor=colors.HexColor("#002366"))
    elements.append(Paragraph("Y.S.M ADVANCE EDUCATION SYSTEM", header_style))
    elements.append(Paragraph("EXAMINATION HALL TICKET", ParagraphStyle('SubHeader', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=14)))
    elements.append(Spacer(1, 0.3*inch))
    
    # --- STUDENT & PHOTO SECTION ---
    # Layout: Photo on Right, Details on Left
    
    # Student Details
    det_style = ParagraphStyle('Details', fontSize=10, leading=14)
    details_text = f"""
    <b>Name:</b> {student.name}<br/>
    <b>Roll Number:</b> {student.roll_number or 'N/A'}<br/>
    <b>Class/Grade:</b> {student.grade}<br/>
    <b>Parent:</b> {student.parent.username if student.parent else 'N/A'}
    """
    
    # Photo Handling
    photo_img = None
    if student.photo and hasattr(student.photo, 'path'):
        try:
            img = ImageReader(student.photo.path)
            photo_img = PlatypusImage(student.photo.path, width=1.2*inch, height=1.5*inch)
        except:
            pass
            
    if not photo_img:
        # Placeholder Box
        photo_text = "PHOTO"
        # We can't easily draw a box in Flowable without CustomFlowable, so we leave it or use text
        photo_img = Paragraph("[ PHOTO ]", ParagraphStyle('PhotoPlace', alignment=TA_CENTER))

    # Table for Layout
    info_data = [[Paragraph(details_text, det_style), photo_img]]
    t_info = Table(info_data, colWidths=[4*inch, 2*inch])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('BOX', (1,0), (1,0), 1, colors.black), # Box around photo
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- EXAM SCHEDULE ---
    # Fetch Exams matching student's grade (simple integer match usually works if data is clean)
    # Since exam.grade_class is Char, we try to match string representation
    grade_str = str(student.grade) 
    upcoming_exams = Exam.objects.filter(grade_class__icontains=grade_str).order_by('exam_date')
    
    if not upcoming_exams.exists():
        # Fallback: Try batch match if enrolled
        # This is a basic implementation, can be expanded
        pass

    exam_data = [["Subject", "Exam Type", "Date", "Duration", "Invigilator Sign"]]
    
    for exam in upcoming_exams:
        exam_data.append([
            exam.subject.name if exam.subject else exam.name,
            exam.get_exam_type_display(),
            exam.exam_date.strftime('%d-%m-%Y'),
            f"{exam.duration_minutes} Mins",
            "" # For signature
        ])
        
    if len(exam_data) == 1:
         exam_data.append(["No upcoming exams found for this class.", "", "", "", ""])

    t_exams = Table(exam_data, colWidths=[2*inch, 1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch])
    t_exams.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_exams)
    elements.append(Spacer(1, 0.5*inch))
    
    # --- INSTRUCTIONS ---
    instructions = """
    <b>INSTRUCTIONS FOR CANDIDATES:</b><br/>
    1. Candidate must carry this Admit Card to the examination hall.<br/>
    2. Reach the center 30 minutes before exam time.<br/>
    3. Electronic gadgets are strictly prohibited.<br/>
    4. Maintain silence in the exam hall.
    """
    elements.append(Paragraph(instructions, ParagraphStyle('Instr', fontSize=9, leading=14)))
    elements.append(Spacer(1, 0.6*inch))
    
    # --- SIGNATURES ---
    sig_data = [
        ["_______________________", "_______________________"],
        ["Student Signature", "Controller of Examinations"]
    ]
    t_sig = Table(sig_data, colWidths=[3.5*inch, 3.5*inch])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t_sig)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
