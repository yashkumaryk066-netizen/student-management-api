from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_invoice_pdf(payment):
    """
    Generate a simple PDF invoice for a payment instance.
    Returns: BytesIO object containing the PDF.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # --- Header ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "INVOICE")
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "NextGen ERP Solutions")
    p.drawString(50, 720, "123 Tech Park, Bangalore, India")
    p.drawString(50, 705, "GSTIN: 29ABCDE1234F1Z5")
    
    # --- Invoice Details ---
    p.drawString(400, 750, f"Invoice #: INV-{payment.id:06d}")
    p.drawString(400, 735, f"Date: {payment.created_at.strftime('%Y-%m-%d')}")
    p.drawString(400, 720, f"Status: {payment.status}")
    
    # --- Bill To ---
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 670, "Bill To:")
    p.setFont("Helvetica", 10)
    
    user_name = "N/A"
    if payment.user:
        user_name = payment.user.username
        if hasattr(payment.user, 'profile') and payment.user.profile.phone:
            p.drawString(50, 640, f"Phone: {payment.user.profile.phone}")
            
    elif payment.student:
        user_name = payment.student.name
        
    p.drawString(50, 655, f"Client/Student: {user_name}")
    
    # --- Line Items ---
    p.line(50, 600, 550, 600)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, 585, "Description")
    p.drawString(450, 585, "Amount (INR)")
    p.line(50, 575, 550, 575)
    
    p.setFont("Helvetica", 10)
    desc = payment.description or f"{payment.get_payment_type_display()} Payment"
    p.drawString(50, 555, desc)
    p.drawString(450, 555, f"{payment.amount}")
    
    # --- Total ---
    p.line(50, 530, 550, 530)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, 510, "Total:")
    p.drawString(450, 510, f"INR {payment.amount}")
    
    # --- Footer ---
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(50, 50, "This is a computer-generated invoice and requires no signature.")
    p.drawString(50, 40, "Thank you for your business!")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
