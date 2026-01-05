import os
from django.conf import settings
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import date

def draw_header_footer(canvas, doc):
    canvas.saveState()
    
    # --- HEADER BACKGROUND (Deep Professional Navy) ---
    canvas.setFillColorRGB(0.05, 0.05, 0.15) # Very Dark Navy
    canvas.rect(0, A4[1] - 140, A4[0], 140, fill=1, stroke=0)
    
    # Accent Gold Strip
    canvas.setFillColorRGB(0.85, 0.65, 0.1) # Gold
    canvas.rect(0, A4[1] - 142, A4[0], 2, fill=1, stroke=0)
    
    # --- LOGO IMAGE (Official Y.S.M Logo) ---
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/ysm_logo.png')
    if os.path.exists(logo_path):
        # Larger logo, better placement
        canvas.drawImage(logo_path, 40, A4[1] - 110, width=80, height=80, mask='auto', preserveAspectRatio=True)
    
    # --- BRANDING TEXT ---
    canvas.setFillColorRGB(1, 1, 1) # White text
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawString(140, A4[1] - 65, "Y.S.M")
    
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColorRGB(0.9, 0.7, 0.2) # Golden Subtitle
    canvas.drawString(140, A4[1] - 85, "ADVANCE EDUCATION SYSTEM")
    
    canvas.setFont("Helvetica", 10)
    canvas.setFillColorRGB(0.7, 0.7, 0.85)
    canvas.drawString(140, A4[1] - 115, "Advanced Institute Management System")
    
    # --- INVOICE BADGE (Top Right) ---
    canvas.setFillColorRGB(0.3, 0.8, 0.4) # Accent Green
    canvas.roundRect(A4[0] - 120, A4[1] - 70, 80, 28, 6, fill=1, stroke=0)
    
    canvas.setFillColorRGB(1, 1, 1)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawCentredString(A4[0] - 80, A4[1] - 59, "PAID")


    # --- ACCENT FOOTER BAR ---
    canvas.setFillColorRGB(0.1, 0.1, 0.25)
    canvas.rect(0, 0, A4[0], 50, fill=1, stroke=0)

    # --- FOOTER TEXT ---
    canvas.setFont("Helvetica", 9)
    canvas.setFillColorRGB(1, 1, 1)
    # Left side
    canvas.drawString(40, 20, "Generated via Y.S.M Advance Education System")
    # Right Side (Branding)
    branding_text = "Visionary Architect & Developed by: Yash A Mishra"
    canvas.drawRightString(A4[0] - 40, 20, branding_text)
    
    canvas.restoreState()

def generate_invoice_pdf(user, subscription, payment):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=150, # Space for custom header
        bottomMargin=60
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    style_heading = ParagraphStyle(
        'PremiumHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=10
    )
    
    style_label = ParagraphStyle(
        'PremiumLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.gray
    )
    
    style_data = ParagraphStyle(
        'PremiumData',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8
    )

    elements = []

    # =========================
    # 1. INVOICE META & DATES
    # =========================
    # We use a table for layout (Invisible borders)
    
    meta_data = [
        [
            Paragraph("BILLED TO:", style_label),
            Paragraph("INVOICE DETAILS:", style_label)
        ],
        [
            Paragraph(f"<b>{user.get_full_name() or 'Valued Client'}</b><br/>{user.email}", style_data),
            Paragraph(f"Invoice #: <b>INV-{payment.id:05d}</b><br/>Date: <b>{date.today().strftime('%d %b, %Y')}</b>", style_data)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[4*inch, 2.5*inch])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 20))


    # =========================
    # 2. PAYMENT TABLE
    # =========================
    
    elements.append(Paragraph("Subscription Summary", style_heading))
    
    amount_str = f"Rs. {payment.amount:,.2f}"
    
    # Table Header & Rows
    table_data = [
        ["DESCRIPTION", "TYPE / PLAN", "VALIDITY", "AMOUNT"],
        [
            "Premium Access License\nNextGen ERP Cloud Subscription", 
            subscription.plan_type, 
            "30 Days", 
            amount_str
        ],
        ["", "", "Total:", amount_str] # Total Row
    ]

    t = Table(table_data, colWidths=[3.2*inch, 1.5*inch, 1*inch, 1.5*inch])
    
    # Premium Table Style
    t.setStyle(TableStyle([
        # Header Styling
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d3436')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 12),
        
        # Row Styling
        ('BACKGROUND', (0,1), (-1,-2), colors.HexColor('#f9f9f9')),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 10),
        ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey),
        
        # Total Row Styling
        ('LINEABOVE', (0,-1), (-1,-1), 2, colors.HexColor('#1a1a2e')),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2,-1), (-1,-1), 12),
        ('TEXTCOLOR', (-1,-1), (-1,-1), colors.HexColor('#27ae60')), # Green amount
        ('ALIGN', (-1,0), (-1,-1), 'RIGHT'), # Align amounts right
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 40))

    # =========================
    # 3. TERMS & NOTES
    # =========================
    elements.append(Paragraph("Terms & Conditions:", style_label))
    elements.append(Paragraph("1. This is a computer-generated invoice and requires no signature.<br/>2. Payment is non-refundable once the license is activated.<br/>3. For support, contact support@nextgen-erp.com.", ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.gray)))
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Thank you for choosing Y.S.M Advance Education System!", ParagraphStyle('ThankYou', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Oblique')))

    # Build PDF with Header/Footer
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    buffer.seek(0)
    return buffer
