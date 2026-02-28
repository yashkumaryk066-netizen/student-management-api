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
