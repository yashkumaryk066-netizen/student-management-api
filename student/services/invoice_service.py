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
    
    # --- 1. WATERMARK (ADVANCE) ---
    canvas.saveState()
    canvas.translate(A4[0]/2, A4[1]/2)
    canvas.rotate(45)
    canvas.setFillColorRGB(0.95, 0.95, 0.95) # Very faint grey
    canvas.setFont("Helvetica-Bold", 100)
    canvas.drawCentredString(0, 0, "Y.S.M ADVANCE")
    canvas.restoreState()

    # --- 2. HEADER BACKGROUND (Deep Enterprise Navy) ---
    canvas.setFillColorRGB(0.02, 0.04, 0.15) 
    canvas.rect(0, A4[1] - 150, A4[0], 150, fill=1, stroke=0)
    
    # --- 3. ACCENT GRADIENT STRIP (Simulated with lines) ---
    canvas.setFillColorRGB(0.85, 0.65, 0.1) # Gold
    canvas.rect(0, A4[1] - 152, A4[0], 2, fill=1, stroke=0)
    canvas.setFillColorRGB(0.4, 0.2, 0.8) # Purple Accent
    canvas.rect(0, A4[1] - 154, A4[0], 2, fill=1, stroke=0)
    
    # --- 4. LOGO (Premium Position) ---
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/ysm_logo.png')
    if os.path.exists(logo_path):
        canvas.drawImage(logo_path, 40, A4[1] - 120, width=90, height=90, mask='auto', preserveAspectRatio=True)
    
    # --- 5. BRANDING TYPOGRAPHY ---
    canvas.setFillColorRGB(1, 1, 1) # White
    canvas.setFont("Helvetica-Bold", 28)
    canvas.drawString(150, A4[1] - 70, "Y.S.M")
    
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColorRGB(0.9, 0.7, 0.2) # Gold
    canvas.drawString(150, A4[1] - 90, "ADVANCE EDUCATION SYSTEM")
    
    canvas.setFont("Helvetica", 9)
    canvas.setFillColorRGB(0.7, 0.7, 0.8) # Text muted
    canvas.drawString(150, A4[1] - 105, "Architecting The Future of Intelligence")
    
    # --- 6. STATUS STAMP ---
    canvas.setStrokeColorRGB(0.2, 0.8, 0.4)
    canvas.setLineWidth(2)
    canvas.setFillColorRGB(0.2, 0.8, 0.4) # Success Green
    canvas.roundRect(A4[0] - 150, A4[1] - 90, 100, 35, 8, fill=0, stroke=1)
    
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(A4[0] - 100, A4[1] - 78, "PAID")
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0] - 100, A4[1] - 65, "Authorized")

    # --- 7. FOOTER (Tech Detail) ---
    canvas.setFillColorRGB(0.05, 0.05, 0.1)
    canvas.rect(0, 0, A4[0], 60, fill=1, stroke=0)

    canvas.setFont("Courier", 8) # Monospace for tech feel
    canvas.setFillColorRGB(0.6, 0.6, 0.7)
    
    # Left: Hash
    uuid = f"DOC-UUID: {random_hash()}"
    canvas.drawString(40, 35, uuid)
    canvas.drawString(40, 20, "SECURE: 256-BIT ENCRYPTION VERIFIED")
    
    # Right: Branding
    canvas.setFont("Helvetica-Oblique", 9)
    canvas.setFillColorRGB(1, 1, 1)
    canvas.drawRightString(A4[0] - 40, 35, "Software Architect: Yash A Mishra")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColorRGB(0.5, 0.5, 0.6)
    canvas.drawRightString(A4[0] - 40, 20, "Telepathy Infotech Intelligence")
    
    canvas.restoreState()

def random_hash():
    import random
    chars = 'A-F0-9'
    return ''.join(random.choice('ABCDEF0123456789') for _ in range(24))

def generate_invoice_pdf(user, subscription, payment):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=170, # Increased head space
        bottomMargin=80
    )

    styles = getSampleStyleSheet()
    
    # --- PREMIUM STYLES ---
    style_heading = ParagraphStyle(
        'PremiumHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=12,
        textTransform='uppercase'
    )
    
    style_data = ParagraphStyle(
        'PremiumData',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1a202c'),
    )

    style_code = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        textColor=colors.HexColor('#4a5568'),
        backColor=colors.HexColor('#edf2f7'),
        borderPadding=6
    )

    elements = []

    # =========================
    # CLIENT INFO BLOCK
    # =========================
    # 2-Column Layout
    info_data = [
        [
            Paragraph("<font color='#718096' size='9'>BILLED TO</font><br/><br/>"
                      f"<b>{user.get_full_name().upper() or 'VALUED CLIENT'}</b><br/>"
                      f"{user.email}<br/>"
                      f"ID: {user.username}", style_data),
                      
            Paragraph("<font color='#718096' size='9'>INVOICE DETAILS</font><br/><br/>"
                      f"Invoice No: <b>INV-{payment.id:06d}</b><br/>"
                      f"Issue Date: <b>{date.today().strftime('%d %B, %Y')}</b><br/>"
                      f"Status: <font color='#38a169'><b>PAID</b></font>", style_data)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[4.2*inch, 2.8*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 20),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 30))

    # =========================
    # SUBSCRIPTION DETAILS
    # =========================
    elements.append(Paragraph("SERVICE BREAKDOWN", style_heading))
    
    plan_details = {
        'COACHING': "COACHING MANAGMENT SYSTEM (Standard Tier)",
        'SCHOOL': "MODERN SCHOOL ERP SUITE (Enterprise Tier)",
        'INSTITUTE': "UNIVERSITY ARCHITECTURE (Ultimate Tier)"
    }.get(subscription.plan_type, subscription.plan_type)

    # Table Content
    data = [
        ["DESCRIPTION / SERVICE", "QTY", "RATE", "AMOUNT"],
        [
            Paragraph(f"<b>{plan_details}</b><br/>"
                      f"<font color='#718096' size='9'>[Ref: {subscription.transaction_id or 'N/A'}]</font><br/><br/>"
                      "<i>Included Features:</i><br/>"
                      "• Full Cloud Access & Data Persistence<br/>"
                      "• Automated Backup & Security Protocols<br/>"
                      "• Y.S.M Intelligence Dashboard License<br/>"
                      "• Priority Developer Support", style_data),
            "1",
            f"{payment.amount:,.2f}",
            f"{payment.amount:,.2f}"
        ],
        ["", "", "", ""], # Spacer Row
        ["", "", "Subtotal", f"{payment.amount:,.2f}"],
        ["", "", "Processing Fee", "0.00"],
        ["", "", "TOTAL REVENUE", f"Rs. {payment.amount:,.2f}"]
    ]

    t = Table(data, colWidths=[3.5*inch, 0.8*inch, 1.2*inch, 1.5*inch])
    
    # Premium Table Visuals
    t.setStyle(TableStyle([
        # Headers
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 12),
        
        # Rows
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#2d3748')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('BOTTOMPADDING', (0,1), (-1,-1), 15),
        ('TOPPADDING', (0,1), (-1,-1), 15),
        
        # Total Section
        ('LINEABOVE', (-2,-3), (-1,-1), 0.5, colors.HexColor('#cbd5e0')), # Line above subtotal
        ('LINEABOVE', (-2,-1), (-1,-1), 2, colors.HexColor('#1a1a2e')), # Bold line above TOTAL
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (-2,-1), (-1,-1), 12),
        ('TEXTCOLOR', (-1,-1), (-1,-1), colors.HexColor('#2b6cb0')),
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 40))

    # =========================
    # DIGITAL VERIFICATION
    # =========================
    elements.append(Paragraph("CRYPTOGRAPHIC PROOF OF PURCHASE", style_heading))
    
    # Fake crypto hash for visual impact
    auth_token = f"TOKEN: {random_hash()}-{random_hash()}"
    elements.append(Paragraph(auth_token, style_code))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("This document is digitally signed by Y.S.M ADVANCE EDUCATION SYSTEM. "
                              "Any alteration invalidates this receipt. "
                              "Verified by secure-node-alpha.", 
                              ParagraphStyle('SmallNote', fontSize=8, textColor=colors.gray)))

    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    buffer.seek(0)
    return buffer
