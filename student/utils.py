from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from django.utils import timezone

def generate_invoice_pdf(payment):
    """
    Generate professional invoice PDF for subscription payment
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Premium Colors
    PRIMARY_COLOR = colors.HexColor("#3b82f6")
    SECONDARY_COLOR = colors.HexColor("#1e293b")
    
    # --- HEADING ---
    elements = []
    
    # Brand Name
    brand_style = ParagraphStyle('Brand', parent=styles['Heading1'], fontSize=24, textColor=PRIMARY_COLOR, spaceAfter=20)
    elements.append(Paragraph("Y.S.M ADVANCE EDUCATION SYSTEM", brand_style))
    
    elements.append(Paragraph("<b>TAX INVOICE</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # --- CLIENT & INVOICE INFO ---
    user = payment.user
    profile = getattr(user, 'profile', None)
    
    client_data = [
        ["Billed To:", "Invoice Details:"],
        [f"Name: {user.get_full_name() or user.username}", f"Invoice No: INV-{payment.id:06d}"],
        [f"Institution: {profile.institution_name if profile else 'N/A'}", f"Date: {timezone.now().strftime('%Y-%m-%d')}"],
        [f"Email: {user.email}", f"Transaction ID: {payment.transaction_id or 'N/A'}"],
        [f"Phone: {profile.phone if profile else 'N/A'}", f"Payment Mode: {payment.get_payment_mode_display()}"],
    ]
    
    t_info = Table(client_data, colWidths=[3.5*inch, 3.5*inch])
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (0,0), PRIMARY_COLOR), # Header color
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.4*inch))
    
    # --- ITEM TABLE ---
    plan_name = profile.institution_type if profile else 'Standard'
    description = f"Subscription Charges ({plan_name} Plan) - 30 Days Validity"
    
    data = [
        ["Description", "Amount (INR)"],
        [description, f"Rs. {payment.amount}"],
        ["", ""],
        ["Total", f"Rs. {payment.amount}"],
    ]
    
    t_items = Table(data, colWidths=[5*inch, 2*inch])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,-1), (-1,-1), colors.whitesmoke), # Total Row
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-2), 1, colors.black),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 0.5*inch))
    
    # --- FOOTER ---
    footer_text = """
    <font size="9" color="grey">
    Terms & Conditions:<br/>
    1. This is a system-generated invoice.<br/>
    2. Payment once made is non-refundable.<br/>
    3. For support, contact support@ysm.education
    </font>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
