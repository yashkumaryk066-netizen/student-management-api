from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
from datetime import date

def generate_invoice_pdf(user, subscription, payment):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    # ===== HEADER =====
    elements.append(Paragraph("<b>NextGen Institute ERP</b>", styles['Title']))
    elements.append(Paragraph("Telepathy Infotech", styles['Normal'])) # Adapted name
    elements.append(Paragraph("Email: support@telepathy.co", styles['Normal'])) # Adapted email
    elements.append(Spacer(1, 20))

    # ===== INVOICE META =====
    elements.append(Paragraph(f"<b>Invoice Date:</b> {date.today()}", styles['Normal']))
    elements.append(Paragraph(f"<b>Invoice No:</b> INV-{payment.id}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ===== CLIENT =====
    elements.append(Paragraph("<b>Billed To:</b>", styles['Heading2']))
    elements.append(Paragraph(f"Email: {user.email}", styles['Normal']))
    if user.first_name:
        elements.append(Paragraph(f"Name: {user.get_full_name()}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ===== TABLE =====
    # Ensure amount matches the payment object type (Decimal)
    amount_str = f"Rs. {payment.amount}"
    
    data = [
        ["Plan", "Amount", "Validity"],
        [subscription.plan_type, amount_str, "30 Days"]
    ]

    table = Table(data, colWidths=[2.5*inch, 2*inch, 2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # Footer
    elements.append(Paragraph("This is a system generated invoice.", styles['Italic']))
    elements.append(Paragraph("Thank you for your business!", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
