from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as PlatypusImage
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from django.utils import timezone

def generate_admission_letter_pdf(student):
    """
    Generate Premium A4 Admission/Welcome Letter
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    # Branding Source
    profile = getattr(student.created_by, 'profile', None)
    inst_name = profile.institution_name if profile and profile.institution_name else "Y.S.M ADVANCE"
    inst_sub = "Digital Education Management"
    logo_path = None
    if profile and profile.institution_logo and hasattr(profile.institution_logo, 'path'):
        import os
        if os.path.exists(profile.institution_logo.path):
            logo_path = profile.institution_logo.path

    # Custom Styles
    style_title = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor("#1a237e"), alignment=TA_CENTER)
    style_subtitle = ParagraphStyle('Subtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=12, textColor=colors.HexColor("#666666"), alignment=TA_CENTER)
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=18, alignment=TA_JUSTIFY, spaceAfter=12)
    style_bold = ParagraphStyle('BoldBody', parent=style_body, fontName='Helvetica-Bold')
    
    elements = []
    
    # --- HEADER ---
    if logo_path:
        elements.append(PlatypusImage(logo_path, width=inch, height=inch, preserveAspectRatio=True))
        elements.append(Spacer(1, 0.1*inch))
        
    elements.append(Paragraph(inst_name.upper(), style_title))
    elements.append(Paragraph(inst_sub, style_subtitle))
    elements.append(Spacer(1, 0.5*inch))
    
    # --- DATE & REF ---
    ref_no = f"REF: ADM/{timezone.now().year}/{student.id:04d}"
    date_str = timezone.now().strftime("%d %B, %Y")
    
    header_data = [
        [Paragraph(f"<b>{ref_no}</b>", style_body), Paragraph(f"<b>Date: {date_str}</b>", ParagraphStyle('Right', parent=style_body, alignment=TA_RIGHT))]
    ]
    t_head = Table(header_data, colWidths=[3.5*inch, 3*inch])
    elements.append(t_head)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- SALUTATION ---
    parent_name = student.parent.username if student.parent else "Parent/Guardian"
    elements.append(Paragraph(f"To,<br/><b>Mr./Mrs. {parent_name}</b>", style_body))
    if student.address:
        elements.append(Paragraph(student.address, style_body))
    elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph(f"<b>Subject: Admission Confirmation - {student.name}</b>", style_bold))
    elements.append(Spacer(1, 0.2*inch))
    
    # --- BODY CONTENT ---
    body_text = f"""
    Dear Parent,
    <br/><br/>
    We are delighted to confirm the admission of your ward, <b>{student.name}</b>, into <b>Class {student.grade}</b> at our institution for the academic session {timezone.now().year}-{timezone.now().year+1}.
    <br/><br/>
    We are committed to providing world-class education and holistic development. Your child's Roll Number is <b>{student.roll_number or 'Pending'}</b>.
    <br/><br/>
    Please find the following details recorded in our system:
    """
    elements.append(Paragraph(body_text, style_body))
    
    # --- STUDENT DETAILS TABLE ---
    data = [
        ["Student Name", student.name.upper()],
        ["Class / Grade", str(student.grade)],
        ["Date of Birth", str(student.dob)],
        ["Blood Group", student.blood_group or "N/A"],
        ["Institution Type", student.get_institution_type_display()],
    ]
    
    t_details = Table(data, colWidths=[2.5*inch, 3.5*inch])
    t_details.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f1f5f9")), # Light Grey Column
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elements.append(t_details)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- CLOSING ---
    closing_text = f"""
    We look forward to a successful academic journey with you. Please do not hesitate to contact the administrative office for any queries.
    <br/><br/>
    Warm Regards,
    <br/>
    <b>{inst_name} Management</b>
    """
    elements.append(Paragraph(closing_text, style_body))
    
    # --- SIGNATURES ---
    sig_path = None
    if profile and profile.digital_signature and hasattr(profile.digital_signature, 'path'):
        import os
        if os.path.exists(profile.digital_signature.path):
            sig_path = profile.digital_signature.path

    elements.append(Spacer(1, 0.3*inch))
    if sig_path:
        elements.append(PlatypusImage(sig_path, width=1.5*inch, height=0.6*inch, preserveAspectRatio=True))
        
    sig_data = [
        ["Authorized Signatory", "Admin Authority"]
    ]
    t_sig = Table(sig_data, colWidths=[3.5*inch, 3*inch])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
    ]))
    elements.append(t_sig)
    
    # --- FOOTER ---
    elements.append(Spacer(1, 1.0*inch))
    elements.append(Paragraph(f"Official Admission Letter | {inst_name}", ParagraphStyle('Footer1', parent=style_body, fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
    elements.append(Paragraph("Powered by Y.S.M Advance Education System", ParagraphStyle('Footer2', parent=style_body, fontSize=7, textColor=colors.lightgrey, alignment=TA_CENTER)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
