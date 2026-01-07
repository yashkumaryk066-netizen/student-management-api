from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as PlatypusImage
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from django.utils import timezone

def draw_header_footer(canvas, doc):
    canvas.saveState()
    
    # --- HEADER BACKGROUND ---
    # Premium Blue Header Strip
    canvas.setFillColor(colors.HexColor("#1a237e")) # Deep Royal Blue
    canvas.rect(0, 10.5*inch, 8.5*inch, 1.5*inch, fill=1, stroke=0)
    
    # --- LOGO & BRANDING ---
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawString(0.5*inch, 11*inch, "Y.S.M")
    canvas.setFont("Helvetica", 12)
    canvas.drawString(0.5*inch, 10.75*inch, "ADVANCE EDUCATION SYSTEM")
    
    # --- INVOICE LABEL ---
    canvas.setFont("Helvetica-Bold", 36)
    canvas.setFillColor(colors.HexColor("#ffd700")) # Gold Color
    canvas.drawRightString(7.8*inch, 11*inch, "INVOICE")
    
    # --- FOOTER ---
    # Bottom Blue Strip
    canvas.setFillColor(colors.HexColor("#1a237e"))
    canvas.rect(0, 0, 8.5*inch, 0.8*inch, fill=1, stroke=0)
    
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 9)
    canvas.drawCentredString(4.125*inch, 0.45*inch, "Thank you for doing business with us!")
    canvas.drawCentredString(4.125*inch, 0.3*inch, "Need Help? support@ysm.education | +91-9876543210 | www.ysm.education")
    
    canvas.restoreState()

def generate_invoice_pdf(payment):
    """
    Generate Ultra-Premium Professional Invoice PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=120, bottomMargin=60)
    styles = getSampleStyleSheet()
    
    # --- PREMIUM COLORS ---
    ROYAL_BLUE = colors.HexColor("#1a237e")
    GOLD = colors.HexColor("#ffd700")
    LIGHT_GREY = colors.HexColor("#f8f9fa")
    TEXT_GREY = colors.HexColor("#4a5568")
    
    elements = []
    
    # --- INVOICE META DATA (Right Aligned) ---
    user = payment.user
    profile = getattr(user, 'profile', None)
    inv_date = timezone.now().strftime('%d %b, %Y')
    inv_no = f"INV-{payment.id:06d}"
    
    # --- BILLING DETAILS ---
    # Two Columns: Billed To (Left) & Invoice Details (Right)
    
    # User Details Style
    p_style = ParagraphStyle('Normal', fontSize=10, leading=14, textColor=TEXT_GREY)
    h_style = ParagraphStyle('Heading', fontSize=12, leading=16, textColor=ROYAL_BLUE, fontName='Helvetica-Bold')
    
    billed_to_html = f"""
    <b>BILLED TO:</b><br/>
    <font size="12" color="#1a237e"><b>{user.get_full_name() or user.username}</b></font><br/>
    {profile.institution_name if profile and profile.institution_name else user.username}<br/>
    {profile.address if profile and profile.address else 'N/A'}<br/>
    {user.email}<br/>
    {profile.phone if profile else ''}
    """
    
    invoice_data_html = f"""
    <b>PAYMENT DETAILS:</b><br/>
    Invoice No: <b>{inv_no}</b><br/>
    Date: <b>{inv_date}</b><br/>
    Mode: <b>{payment.get_payment_mode_display()}</b><br/>
    Txn ID: {payment.transaction_id or 'N/A'}<br/>
    Status: <font color="green"><b>PAID</b></font>
    """
    
    meta_table_data = [
        [Paragraph(billed_to_html, p_style), Paragraph(invoice_data_html, p_style)]
    ]
    
    t_meta = Table(meta_table_data, colWidths=[4*inch, 3*inch])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 0.5*inch))
    
    # --- INVOICE ITEMS TABLE ---
    plan_name = profile.institution_type if profile else 'Standard'
    item_desc = f"<b>{plan_name} Plan Subscription</b><br/><font size=9 color='#666'>Access to premium education management modules (30 Days Validity)</font>"
    
    # Header
    table_data = [
        ["DESCRIPTION", "QTY", "PRICE", "TOTAL"], # Header
        [Paragraph(item_desc, p_style), "1", f"Rs. {payment.amount}", f"Rs. {payment.amount}"], # Item
        ["", "", "", ""], # Spacer
        ["", "", "Grand Total:", f"Rs. {payment.amount}"], # Total
    ]
    
    col_widths = [4*inch, 0.8*inch, 1.2*inch, 1.2*inch]
    t_items = Table(table_data, colWidths=col_widths)
    
    # Premium Table Style
    t_items.setStyle(TableStyle([
        # Header Styling
        ('BACKGROUND', (0,0), (-1,0), ROYAL_BLUE),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 12),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'), # Numbers Right Aligned
        ('ALIGN', (0,0), (0,-1), 'LEFT'),   # Desc Left Aligned
        
        # Item Row Styling
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('TEXTCOLOR', (0,1), (-1,1), TEXT_GREY),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,1), 10),
        ('BOTTOMPADDING', (0,1), (-1,1), 15),
        ('TOPPADDING', (0,1), (-1,1), 15),
        ('LINEBELOW', (0,1), (-1,1), 1, colors.HexColor("#e2e8f0")), # Light border
        
        # Total Row Styling
        ('LINEABOVE', (0,-1), (-1,-1), 2, ROYAL_BLUE),
        ('FONTNAME', (2,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (2,-1), (-1,-1), 14),
        ('TEXTCOLOR', (2,-1), (-1,-1), ROYAL_BLUE),
        ('TOPPADDING', (0,-1), (-1,-1), 15),
    ]))
    
    elements.append(t_items)
    elements.append(Spacer(1, 0.8*inch))
    
    # --- TERMS & CONDITIONS (Boxed) ---
    terms_html = """
    <b>TERMS AND CONDITIONS:</b><br/>
    1. This invoice is computer generated and does not require a signature.<br/>
    2. Payment once made is non-refundable.<br/>
    3. Services are valid for 30 days from the date of activation.<br/>
    4. For any billing queries, please contact support within 3 days.
    """
    
    t_terms = Table([[Paragraph(terms_html, ParagraphStyle('Terms', fontSize=8, leading=12, textColor=TEXT_GREY))]], colWidths=[7.2*inch])
    t_terms.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREY),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t_terms)
    
    # --- BUILD ---
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    buffer.seek(0)
    return buffer
