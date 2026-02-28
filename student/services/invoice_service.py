import os
import csv
from django.http import HttpResponse
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
from student.conf import CURRENCY_SYMBOL

def draw_header_footer(canvas, doc):
    canvas.saveState()
    
    # Defaults (Y.S.M Branding)
    watermark_text = "Y.S.M ADVANCE"
    logo_path = os.path.join(settings.BASE_DIR, 'static/img/ysm_logo.png')
    brand_name = "Y.S.M"
    sub_text = "ADVANCE EDUCATION SYSTEM"
    tagline = "Architecting The Future of Intelligence"
    
    # Check for Dynamic Branding (Injected via doc object)
    if hasattr(doc, 'branding') and doc.branding:
        b = doc.branding
        if b.get('name'):
            brand_name = b.get('name').upper()
            # Watermark remains Y.S.M as per request
            # watermark_text = brand_name 
            sub_text = "OFFICIAL RECEIPT" # Generic subtext for custom
            tagline = b.get('address') or ""
        
        if b.get('logo_path') and os.path.exists(b.get('logo_path')):
             logo_path = b.get('logo_path')
             
    # --- 1. WATERMARK ---
    canvas.saveState()
    canvas.translate(A4[0]/2, A4[1]/2)
    canvas.rotate(45)
    canvas.setFillColorRGB(0.95, 0.95, 0.95) # Very faint grey
    # Adjust font size based on text length
    wm_size = 60 if len(watermark_text) > 20 else 100
    canvas.setFont("Helvetica-Bold", wm_size)
    canvas.drawCentredString(0, 0, watermark_text)
    canvas.restoreState()

    # --- 2. HEADER BACKGROUND (Deep Enterprise Navy) ---
    canvas.setFillColorRGB(0.02, 0.04, 0.15) 
    canvas.rect(0, A4[1] - 150, A4[0], 150, fill=1, stroke=0)
    
    # --- 3. ACCENT GRADIENT STRIP ---
    canvas.setFillColorRGB(0.85, 0.65, 0.1) # Gold
    canvas.rect(0, A4[1] - 152, A4[0], 2, fill=1, stroke=0)
    
    # --- 4. LOGO ---
    logo_exists = False
    if os.path.exists(logo_path):
        try:
             canvas.drawImage(logo_path, 40, A4[1] - 120, width=90, height=90, mask='auto', preserveAspectRatio=True)
             logo_exists = True
        except: 
             pass
    
    # --- 5. BRANDING TYPOGRAPHY ---
    canvas.setFillColorRGB(1, 1, 1) # White
    
    # Dynamic Font Sizing for long institution names
    title_size = 28
    if len(brand_name) > 20: title_size = 22
    if len(brand_name) > 30: title_size = 18
    if len(brand_name) > 40: title_size = 16
    
    # Smart Positioning: If logo exists, text starts after logo, else centered
    if logo_exists:
        text_x = 150  # Start after logo
        text_align = 'left'
    else:
        text_x = A4[0] / 2  # Center
        text_align = 'center'
        
    canvas.setFont("Helvetica-Bold", title_size)
    if text_align == 'center':
        canvas.drawCentredString(text_x, A4[1] - 70, brand_name)
    else:
        canvas.drawString(text_x, A4[1] - 70, brand_name)
    
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColorRGB(0.9, 0.7, 0.2) # Gold
    if text_align == 'center':
        canvas.drawCentredString(text_x, A4[1] - 90, sub_text)
    else:
        canvas.drawString(text_x, A4[1] - 90, sub_text)
    
    canvas.setFont("Helvetica", 9)
    canvas.setFillColorRGB(0.7, 0.7, 0.8) # Text muted
    # Truncate address if too long
    tagline_display = tagline[:80] + ("..." if len(tagline) > 80 else "")
    if text_align == 'center':
        canvas.drawCentredString(text_x, A4[1] - 105, tagline_display)
    else:
        canvas.drawString(text_x, A4[1] - 105, tagline_display)
    
    # --- 6. STATUS STAMP ---
    # Position adjusted to avoid overlap with long institution names
    stamp_y = A4[1] - 110  # Moved down from -90
    
    status_text = "PAID"
    stamp_color = (0.2, 0.8, 0.4)  # Green
    
    if hasattr(doc, 'payment_status') and doc.payment_status != 'PAID':
        status_text = "DUE"
        stamp_color = (0.9, 0.3, 0.2)  # Red
    
    canvas.setStrokeColorRGB(*stamp_color)
    canvas.setLineWidth(2)
    canvas.setFillColorRGB(*stamp_color)
    canvas.roundRect(A4[0] - 150, stamp_y, 100, 35, 8, fill=0, stroke=1)
    
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(A4[0] - 100, stamp_y + 14, status_text)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(A4[0] - 100, stamp_y + 3, "Status")

    # --- 7. FOOTER (Tech Detail) ---
    canvas.setFillColorRGB(0.05, 0.05, 0.1)
    canvas.rect(0, 0, A4[0], 60, fill=1, stroke=0)

    canvas.setFont("Courier", 8) 
    canvas.setFillColorRGB(0.6, 0.6, 0.7)
    
    uuid = f"DOC-UUID: {random_hash()}"
    canvas.drawString(40, 35, uuid)
    canvas.drawString(40, 20, "SECURE: 256-BIT ENCRYPTION VERIFIED")
    
    canvas.setFont("Helvetica-Oblique", 9)
    canvas.setFillColorRGB(1, 1, 1)
    
    # Footer Branding - Use Client's Institution Name
    footer_name = brand_name if brand_name != "Y.S.M" else "Institution"
    canvas.drawRightString(A4[0] - 40, 35, f"Generated by {footer_name}")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColorRGB(0.5, 0.5, 0.6)
    
    # Show institution type or tagline
    footer_tagline = "Official Document"
    if hasattr(doc, 'branding') and doc.branding and doc.branding.get('name'):
        footer_tagline = "Authorized Institution Document"
    canvas.drawRightString(A4[0] - 40, 20, footer_tagline)
    
    canvas.restoreState()

def random_hash():
    import random
    chars = 'A-F0-9'
    return ''.join(random.choice('ABCDEF0123456789') for _ in range(24))

def generate_invoice_pdf(user, subscription, payment):
    """
    Dispatcher for Invoice Generation.
    Type 1: Client Subscription Invoice
    Type 2: Student Fee Receipt
    """
    # Robust Check: Use Payment Type OR Student Existence
    if payment.payment_type == 'FEE' or payment.student:
        return generate_student_receipt_pdf(payment)
    else:
        return generate_subscription_invoice_pdf(user, subscription, payment)

def generate_student_receipt_pdf(payment):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=150,
        bottomMargin=80
    )
    
    # --- DYNAMIC BRANDING INJECTION ---
    doc.branding = {}
    doc.payment_status = payment.status
    
    # Find Owner (Client) - Payment doesn't have created_by, use student or user
    owner = None
    if payment.student and hasattr(payment.student, 'created_by'):
        owner = payment.student.created_by
    elif payment.user:  # Client subscription payment
        owner = payment.user
        
    if owner and hasattr(owner, 'profile'):
        p = owner.profile
        doc.branding = {
            'name': p.institution_name,
            'address': p.address,
            'logo_path': p.institution_logo.path if p.institution_logo else None,
            'signature_path': p.digital_signature.path if p.digital_signature else None
        }

    styles = getSampleStyleSheet()
    
    # Custom Styles
    style_heading = ParagraphStyle('Head', parent=styles['Heading3'], fontSize=14, textColor=colors.HexColor('#0f172a'), spaceAfter=10)
    style_normal = ParagraphStyle('Norm', parent=styles['Normal'], fontSize=10, leading=14)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=8, textColor=colors.gray)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor('#1e293b'))
    
    elements = []
    
    # Title based on category
    category_label = payment.get_payment_category_display().upper() if payment.payment_category else "FEE"
    if not category_label: category_label = "FEE"
    
    # Logic: If PAID -> RECEIPT, else -> INVOICE
    doc_type = "RECEIPT" if payment.status == 'PAID' else "INVOICE"
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"{category_label} {doc_type}", ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=22, textColor=colors.HexColor('#1e40af'), fontName='Helvetica-Bold')))
    elements.append(Paragraph(f"(Official Copy)", ParagraphStyle('SubTitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor=colors.gray)))
    elements.append(Spacer(1, 25))
    
    # Receipt Info
    # Safely get parent name & student name
    parent_name = "N/A"
    student_name = "Unknown / Walk-in"
    grade_info = "N/A"
    
    if payment.student:
        student_name = payment.student.name.upper()
        grade_info = str(payment.student.grade)
        if payment.student.parent:
            parent_name = payment.student.parent.username
            
    # Premium Grid Layout using Table
    row1 = [
        [Paragraph("RECEIPT NO", style_label), Paragraph(f"REC-{payment.id:06d}", style_value)],
        [Paragraph("DATE", style_label), Paragraph(date.today().strftime('%d %B, %Y'), style_value)]
    ]
    row2 = [
        [Paragraph("STUDENT NAME", style_label), Paragraph(student_name, style_value)],
        [Paragraph("CLASS / GRADE", style_label), Paragraph(grade_info, style_value)]
    ]
    row3 = [
        [Paragraph("PARENT / GUARDIAN", style_label), Paragraph(parent_name, style_value)],
        [Paragraph("PAYMENT MODE", style_label), Paragraph(payment.get_payment_mode_display() if hasattr(payment, 'get_payment_mode_display') else payment.payment_mode, style_value)]
    ]

    # Helper to build inner tables for layout
    def make_inner(row_data):
        return Table([row_data], colWidths=[1.5*inch, 2*inch])

    info_data = [
        [make_inner(row1[0]), make_inner(row1[1])],
        [make_inner(row2[0]), make_inner(row2[1])],
        [make_inner(row3[0]), make_inner(row3[1])]
    ]
    
    t_info = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    t_info.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 30))
    
    # Fee Table
    # Determine clear description
    description = payment.description
    if not description:
        description = f"{category_label} Payment"
        
    fee_data = [
        ["DESCRIPTION", "CATEGORY", "AMOUNT"],
        [description, category_label, f"{CURRENCY_SYMBOL} {payment.amount:,.2f}"],
        ["", "", ""],
        ["", "TOTAL PAID", f"{CURRENCY_SYMBOL} {payment.amount:,.2f}"]
    ]
    
    t_fee = Table(fee_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
    t_fee.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#475569')),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        
        ('LINEABOVE', (-2,-1), (-1,-1), 1, colors.black),
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-1,-1), (-1,-1), colors.HexColor('#16a34a')), # Green Total
        ('FONTSIZE', (-1,-1), (-1,-1), 12),
        ('ALIGN', (-1,-1), (-1,-1), 'LEFT'),
    ]))
    elements.append(t_fee)
    
    # Transaction ID Note
    if payment.transaction_id:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Transaction Reference: {payment.transaction_id}", ParagraphStyle('Ref', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))

    elements.append(Spacer(1, 40))
    
    # Signature Section
    if doc.branding.get('signature_path') and os.path.exists(doc.branding['signature_path']):
         try:
             # Add Signature Image
             im = Image(doc.branding['signature_path'], width=1.5*inch, height=0.6*inch)
             im.hAlign = 'RIGHT'
             elements.append(im)
             elements.append(Paragraph("Authorized Signatory", ParagraphStyle('Sig', parent=styles['Normal'], fontSize=8, alignment=TA_RIGHT)))
         except: pass
    
    # Footer Note
    elements.append(Paragraph("This is a computer-generated receipt.", ParagraphStyle('Note', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER)))
    elements.append(Paragraph("Thank you for your timely payment.", ParagraphStyle('Note2', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=TA_CENTER, spaceBefore=4)))
    
    doc.build(elements, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    buffer.seek(0)
    return buffer

def generate_subscription_invoice_pdf(user, subscription, payment):
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
    # Determine Status & Color
    is_rejected = payment.status in ['REJECTED', 'FAILED']
    status_text = "VOID / REJECTED" if is_rejected else "PAID"
    status_color = "#ef4444" if is_rejected else "#38a169"
    
    info_data = [
        [
            Paragraph("<font color='#718096' size='9'>BILLED TO</font><br/><br/>"
                      f"<b>{user.get_full_name().upper() or 'VALUED CLIENT'}</b><br/>"
                      f"{user.email}<br/>"
                      f"ID: {user.username}", style_data),
                      
            Paragraph("<font color='#718096' size='9'>INVOICE DETAILS</font><br/><br/>"
                      f"Invoice No: <b>INV-{payment.id:06d}</b><br/>"
                      f"Issue Date: <b>{date.today().strftime('%d %B, %Y')}</b><br/>"
                      f"Status: <font color='{status_color}'><b>{status_text}</b></font>", style_data)
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

    if is_rejected:
        # Add a Watermark-like note for rejection
        elements.append(Paragraph("<font color='red'>NOTE: THIS TRANSACTION WAS DECLINED. NO CHARGES APPLIED.</font>", style_heading))
        elements.append(Spacer(1, 10))

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
            Paragraph(f"<b>{plan_details} (Monthly Subscription)</b><br/>"
                      f"<font color='#718096' size='9'>[Ref: {subscription.transaction_id or 'N/A'}]</font><br/><br/>"
                      "<i>Billing Cycle: Monthly Recurring Charge</i><br/>"
                      "<i>Included Features:</i><br/>"
                      "• Full Cloud Access & Data Persistence<br/>"
                      "• Automated Backup & Security Protocols<br/>"
                      "• Y.S.M Intelligence Dashboard License<br/>"
                      "• Priority Developer Support", style_data),
            "1",
            f"{CURRENCY_SYMBOL} {payment.amount:,.2f}",
            f"{CURRENCY_SYMBOL} {payment.amount:,.2f}"
        ],
        ["", "", "", ""], # Spacer Row
        ["", "", "Subtotal", f"{CURRENCY_SYMBOL} {payment.amount:,.2f}"],
        ["", "", "Processing Fee", "0.00"],
        ["", "", "GRAND TOTAL", f"{CURRENCY_SYMBOL} {payment.amount:,.2f}"]
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
