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
    
    # --- HEADER BACKGROUND ---
    canvas.setFillColorRGB(0.1, 0.1, 0.25) # Dark Premium Navy
    canvas.rect(0, A4[1] - 120, A4[0], 120, fill=1, stroke=0)
    
    # --- LOGO EMOJI ---
    canvas.setFont("Helvetica", 36)
    canvas.setFillColorRGB(0.4, 0.6, 1.0) # Blue glow
    canvas.drawString(40, A4[1] - 55, "🎓")
    
    # --- BRANDING TEXT ---
    canvas.setFillColorRGB(1, 1, 1) # White text
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawString(100, A4[1] - 50, "NEXTGEN ERP")
    
    canvas.setFont("Helvetica", 12)
    canvas.setFillColorRGB(0.8, 0.8, 0.9)
    canvas.drawString(100, A4[1] - 70, "Advanced Institute Management System")
    
    # --- INVOICE BADGE ---
    canvas.setFillColorRGB(0.3, 0.8, 0.4) # Accent Green
    canvas.roundRect(A4[0] - 150, A4[1] - 60, 110, 30, 6, fill=1, stroke=0)
    
    canvas.setFillColorRGB(1, 1, 1)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(A4[0] - 95, A4[1] - 53, "PAID")


    # --- ACCENT FOOTER BAR ---
    canvas.setFillColorRGB(0.1, 0.1, 0.25)
    canvas.rect(0, 0, A4[0], 50, fill=1, stroke=0)

    # --- FOOTER TEXT ---
    canvas.setFont("Helvetica", 9)
    canvas.setFillColorRGB(1, 1, 1)
    # Left side
    canvas.drawString(40, 20, "Generated via NextGen ERP System")
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
    elements.append(Paragraph("Thank you for choosing NextGen ERP!", ParagraphStyle('ThankYou', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Oblique')))

    # Build PDF with Header/Footer
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    buffer.seek(0)
    return buffer
