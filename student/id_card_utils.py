from io import BytesIO
import qrcode
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.utils import timezone
import os

def generate_id_card_pdf(student):
    """
    Dispatcher for Premium ID Cards based on Institution Type.
    """
    inst_type = 'SCHOOL' # Default
    if hasattr(student.created_by, 'profile'):
        inst_type = student.created_by.profile.institution_type
    elif student.institution_type:
        inst_type = student.institution_type
        
    if inst_type == 'COACHING':
        return generate_coaching_card(student)
    elif inst_type == 'INSTITUTE':
        return generate_institute_card(student)
    else:
        return generate_school_card(student)

def get_common_dimensions():
    # ISO ID-1 (CR80)
    width_mm, height_mm = 53.98, 85.60
    width_pt, height_pt = width_mm * 2.83465, height_mm * 2.83465 
    return width_pt, height_pt

def draw_fit_text(c, text, x, y, max_width, initial_font_size, font_name="Helvetica-Bold", color=None):
    """
    Draws text centered at (x,y). 
    Automatically reduces font size to fit within max_width.
    """
    if not text: return
    
    current_size = initial_font_size
    c.setFont(font_name, current_size)
    if color:
        c.setFillColor(color)
        
    while c.stringWidth(text, font_name, current_size) > max_width and current_size > 4:
        current_size -= 0.5
        c.setFont(font_name, current_size)
        
    c.drawCentredString(x, y, text)


# =========================================================
# 1. SCHOOL DESIGN (Formal, Structured, Classic)
# =========================================================
def generate_school_card(student):
    width_pt, height_pt = get_common_dimensions()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width_pt, height_pt))
    
    # Colors (Classic Blue & White)
    PRIMARY = colors.HexColor("#1e3a8a") # Dark Blue
    ACCENT = colors.HexColor("#facc15")  # Yellow
    BG = colors.HexColor("#ffffff")
    TEXT = colors.HexColor("#1e293b")
    
    # 1. Background
    c.setFillColor(BG)
    c.rect(0, 0, width_pt, height_pt, fill=1, stroke=0)
    
    # 2. Header (Curved)
    c.setFillColor(PRIMARY)
    p = c.beginPath()
    p.moveTo(0, height_pt)
    p.lineTo(width_pt, height_pt)
    p.lineTo(width_pt, height_pt - 60)
    p.curveTo(width_pt*0.5, height_pt - 80, width_pt*0.5, height_pt - 80, 0, height_pt - 60)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # 3. Logo & School Name
    owner = student.created_by
    inst_name = "SCHOOL NAME"
    logo_path = None
    if hasattr(owner, 'profile'):
        inst_name = owner.profile.institution_name or "ACADEMIC SCHOOL"
        if owner.profile.institution_logo and hasattr(owner.profile.institution_logo, 'path'):
            if os.path.exists(owner.profile.institution_logo.path):
                logo_path = owner.profile.institution_logo.path
                
    # Draw Logo
    text_y = height_pt - 30 # Default if no logo
    if logo_path:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, width_pt/2 - 15, height_pt - 45, width=30, height=30, mask='auto', preserveAspectRatio=True)
            text_y = height_pt - 55
        except:
             text_y = height_pt - 30
             
    c.setFillColor(colors.white)
    # Use Dynamic Scaling
    draw_fit_text(c, inst_name.upper(), width_pt/2, text_y, width_pt - 10, 9, "Helvetica-Bold", colors.white)

    
    c.setFont("Helvetica", 5)
    c.drawCentredString(width_pt/2, text_y - 6, "EXCELLENCE IN EDUCATION")
    
    # 4. Photo with Frame
    photo_y = height_pt - 130
    photo_x = (width_pt - 60) / 2
    
    # Border
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(1.5)
    c.rect(photo_x, photo_y, 60, 60, fill=0, stroke=1)
    
    # Photo Image
    if student.photo and os.path.exists(student.photo.path):
        try:
            img = ImageReader(student.photo.path)
            c.drawImage(img, photo_x + 1, photo_y + 1, width=58, height=58, preserveAspectRatio=True, anchor='c')
        except:
            c.drawCentredString(width_pt/2, photo_y + 30, "No Photo")
    else:
         c.setFont("Helvetica", 6)
         c.drawCentredString(width_pt/2, photo_y + 30, "No Photo")

    # 5. Student Details Section
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width_pt/2, photo_y - 15, student.name.upper())
    
    c.setFillColor(ACCENT)
    c.rect(width_pt/2 - 25, photo_y - 25, 50, 8, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(width_pt/2, photo_y - 22, f"CLASS: {student.grade}")
    
    # Attributes Grid
    start_y = photo_y - 40
    c.setFillColor(TEXT)
    
    # Format Roll Number (Strip Owner ID prefix if present)
    roll_disp = student.roll_number or "N/A"
    if roll_disp != "N/A" and '-' in roll_disp:
        parts = roll_disp.split('-')
        # Expecting Owner-Grade-Seq. If parts > 1, show last part (Seq)
        # Or showing Grade-Seq? User said "Class ... roll number". 
        # If I show "10-001", it's implicit.
        # But if School Card already has "CLASS: 10" above, then just "001" is better.
        # But usually Roll No is just "1".
        roll_disp = parts[-1]
    
    attrs = [
        ("Roll No:", roll_disp),
        ("DOB:", str(student.dob)),
        ("Blood Grp:", student.blood_group or "N/A"),
        ("Phone:", student.contact_number or "N/A")
    ]

    
    c.setFont("Helvetica", 7)
    for label, val in attrs:
        c.drawString(20, start_y, label)
        c.drawRightString(width_pt - 20, start_y, str(val))
        # Divider
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(20, start_y - 2, width_pt - 20, start_y - 2)
        start_y -= 12
        
    # 6. Footer (Signature & Address)
    # QR Code for Attendance (Bottom Left)
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(str(student.id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    c.drawInlineImage(qr_img, 15, 20, width=30, height=30)
    c.setFont("Helvetica", 4)
    c.drawCentredString(30, 18, "SCAN ME")

    # Principal Sig
    if hasattr(owner, 'profile') and owner.profile.digital_signature:
        sig_path = owner.profile.digital_signature.path
        if os.path.exists(sig_path):
            try:
                sig = ImageReader(sig_path)
                c.drawImage(sig, width_pt - 45, 25, width=30, height=20, mask='auto', preserveAspectRatio=True)
            except: pass
            
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 5)
    c.drawRightString(width_pt - 15, 20, "Principal Signature")
    
    # Address Bar
    c.setFillColor(PRIMARY)
    c.rect(0, 0, width_pt, 15, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 4)
    addr = owner.profile.address if hasattr(owner, 'profile') else "Campus Address"
    c.drawCentredString(width_pt/2, 6, str(addr)[:60])
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# =========================================================
# 2. COACHING DESIGN (Modern, Dynamic, Edgy)
# =========================================================
def generate_coaching_card(student):
    width_pt, height_pt = get_common_dimensions()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width_pt, height_pt))
    
    # Colors (Vibrant Orange/Black)
    PRIMARY = colors.HexColor("#111827") # Almost Black
    ACCENT = colors.HexColor("#ff6b00")  # Vivid Orange
    BG = colors.HexColor("#f3f4f6")
    
    # 1. Header (Slant)
    c.setFillColor(PRIMARY)
    p = c.beginPath()
    p.moveTo(0, height_pt)
    p.lineTo(width_pt, height_pt)
    p.lineTo(width_pt, height_pt - 60)
    p.lineTo(0, height_pt - 80)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Orange Accent Line
    c.setStrokeColor(ACCENT)
    c.setLineWidth(4)
    c.line(0, height_pt - 82, width_pt, height_pt - 62)
    
    # 2. Institution Logo/Name
    owner = student.created_by
    inst_name = "COACHING HUB"
    logo_path = None
    if hasattr(owner, 'profile'):
        inst_name = owner.profile.institution_name or "COACHING INSTITUTE"
        if owner.profile.institution_logo and hasattr(owner.profile.institution_logo, 'path'):
             if os.path.exists(owner.profile.institution_logo.path):
                logo_path = owner.profile.institution_logo.path

    if logo_path:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 10, height_pt - 45, width=30, height=30, mask='auto', preserveAspectRatio=True)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(45, height_pt - 30, inst_name.upper()[:15])
            c.setFont("Helvetica", 6)
            c.drawString(45, height_pt - 38, "PREMIUM LEARNING")
        except:
            c.setFillColor(colors.white)
            draw_fit_text(c, inst_name.upper(), width_pt/2, height_pt - 30, width_pt - 10, 10, "Helvetica-Bold", colors.white)

    if not logo_path:
         c.setFillColor(colors.white)
         draw_fit_text(c, inst_name.upper(), width_pt/2, height_pt - 30, width_pt - 10, 10, "Helvetica-Bold", colors.white)
         c.setFont("Helvetica", 6)
         c.drawCentredString(width_pt/2, height_pt - 40, "PREMIUM LEARNING")


    # 3. Photo (Circular)
    photo_y = height_pt - 140
    photo_r = 30
    photo_cx = width_pt / 2
    
    # Outline
    c.setFillColor(colors.white)
    c.circle(photo_cx, photo_y + photo_r, photo_r + 2, stroke=0, fill=1)
    
    if student.photo and os.path.exists(student.photo.path):
        try:
            img = ImageReader(student.photo.path)
            c.saveState()
            p = c.beginPath()
            p.circle(photo_cx, photo_y + photo_r, photo_r)
            c.clipPath(p, stroke=0, fill=0)
            c.drawImage(img, photo_cx - photo_r, photo_y, width=photo_r*2, height=photo_r*2, preserveAspectRatio=True, anchor='c')
            c.restoreState()
        except: pass
    else:
        c.setFillColor(colors.lightgrey)
        c.circle(photo_cx, photo_y + photo_r, photo_r, stroke=0, fill=1)

    # 4. Details
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width_pt/2, photo_y - 15, student.name.upper())
    
    # Batch Badge
    batch_name = "GENERAL"
    course_name = "N/A"
    # Try to fetch batch from enrollments
    enrollment = student.enrollments.filter(status='ACTIVE').first()
    if enrollment:
        batch_name = enrollment.batch.name
        course_name = enrollment.batch.course.name
        
    c.setFillColor(ACCENT)
    c.roundRect(width_pt/2 - 40, photo_y - 28, 80, 10, 3, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(width_pt/2, photo_y - 25, f"BATCH: {batch_name}".upper())
    
    # Info Grid
    start_y = photo_y - 45
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 7)
    
    c.drawString(20, start_y, "Course:")
    c.drawRightString(width_pt - 20, start_y, course_name)
    
    c.drawString(20, start_y - 12, "Student ID:")
    c.drawRightString(width_pt - 20, start_y - 12, f"ST-{student.id}")
    
    c.drawString(20, start_y - 24, "Valid Till:")
    c.drawRightString(width_pt - 20, start_y - 24, "Dec 2025")
    
    # 5. Big QR Code at Bottom
    qr_y = 10
    qr_size = 40
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(str(student.id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    c.drawInlineImage(qr_img, width_pt/2 - 20, qr_y + 10, width=40, height=40)
    
    c.setFont("Helvetica", 5)
    c.drawCentredString(width_pt/2, qr_y + 2, "Scan for Attendance / Entry")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# =========================================================
# 3. INSTITUTE/UNIVERSITY DESIGN (Professional, Minimalist)
# =========================================================
def generate_institute_card(student):
    width_pt, height_pt = get_common_dimensions()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width_pt, height_pt))
    
    # Colors (Deep Maroon & Grey)
    PRIMARY = colors.HexColor("#800000") # Maroon
    SECONDARY = colors.HexColor("#7f1d1d")
    TEXT = colors.HexColor("#333333")
    BG = colors.HexColor("#fafafa")
    
    c.setFillColor(BG)
    c.rect(0, 0, width_pt, height_pt, fill=1, stroke=0)
    
    # 1. Background Watermark (Logo Light)
    owner = student.created_by
    logo_path = None
    if hasattr(owner, 'profile') and owner.profile.institution_logo:
        try:
            logo_path = owner.profile.institution_logo.path
            c.saveState()
            c.setFillAlpha(0.05)
            logo = ImageReader(logo_path)
            c.drawImage(logo, width_pt/2 - 40, height_pt/2 - 40, width=80, height=80, mask='auto', preserveAspectRatio=True)
            c.restoreState()
        except: pass
        
    # 2. Header (Clean Blocks)
    c.setFillColor(PRIMARY)
    c.rect(0, height_pt - 40, width_pt, 40, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Times-Bold", 10)
    inst_name = owner.profile.institution_name if hasattr(owner, 'profile') else "UNIVERSITY"
    # Use Dynamic Scaling
    draw_fit_text(c, inst_name.upper(), width_pt/2, height_pt - 20, width_pt - 10, 10, "Times-Bold", colors.white)

    c.setFont("Times-Roman", 6)
    c.drawCentredString(width_pt/2, height_pt - 30, "ESTD. 2024")
    
    # 3. Photo (Square with shadow)
    photo_y = height_pt - 110
    photo_x = (width_pt - 55) / 2
    
    c.setFillColor(colors.lightgrey)
    c.rect(photo_x + 2, photo_y - 2, 55, 55, fill=1, stroke=0) # Shadow
    c.setFillColor(colors.white)
    c.rect(photo_x, photo_y, 55, 55, fill=1, stroke=0) # Border
    
    if student.photo and os.path.exists(student.photo.path):
        try:
            img = ImageReader(student.photo.path)
            c.drawImage(img, photo_x+2, photo_y+2, width=51, height=51, preserveAspectRatio=True)
        except: pass
    else:
        c.setFillColor(colors.grey)
        c.drawCentredString(width_pt/2, photo_y + 25, "Photo")
        
    # Department Strip
    dept_name = student.department.name if student.department else "GENERAL"
    c.setFillColor(colors.black)
    c.setFont("Times-Bold", 8)
    c.drawCentredString(width_pt/2, photo_y - 12, dept_name.upper())
    
    # 4. Details (Clean Left-aligned)
    c.setFillColor(PRIMARY)
    c.setFont("Times-Bold", 12)
    c.drawCentredString(width_pt/2, photo_y - 28, student.name.upper())
    
    start_y = photo_y - 45
    c.setFillColor(TEXT)
    c.setFont("Times-Roman", 8)
    
    # Reg No formatted
    reg_no = student.admission_number or f"REG{student.id}"
    c.drawCentredString(width_pt/2, start_y, f"Reg No: {reg_no}")
    
    c.setFont("Times-Roman", 7)
    
    # Course / Program
    if student.student_class:
         c.drawCentredString(width_pt/2, start_y - 12, f"Program: {student.student_class}")
    
    # 5. QR Code & Barcode (Bottom)
    qr_y = 20
    qr = qrcode.QRCode(box_size=5)
    qr.add_data(str(student.id))
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    c.drawInlineImage(qr_img, 15, qr_y, width=35, height=35)
    
    # Simple fake barcode representation
    import random
    x = 55
    c.setLineWidth(1)
    for i in range(25):
        w = random.choice([0.5, 1, 2])
        c.setLineWidth(w)
        c.line(x, qr_y + 5, x, qr_y + 25)
        x += w + 1.5
        
    c.setFont("Courier", 6)
    c.drawCentredString(width_pt/2 + 20, qr_y - 2, reg_no)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
