from io import BytesIO
import qrcode
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
import os

def generate_id_card_pdf(student):
    """
    Generate Advanced Smart ID Card with QR Code
    Detailed and Premium Design
    Size: Standard ID Card (85.60mm x 53.98mm) but scaled up for PDF quality
    """
    width, height = 85.60 * 2.83465, 53.98 * 2.83465  # Convert mm to points (approx 242x153 points)
    buffer = BytesIO()
    
    # Premium Colors
    PRIMARY_BLUE = "#002366"  # Royal Navy
    ACCENT_GOLD = "#D4AF37"   # Metallic Gold
    
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # --- BACKGROUND DESIGN ---
    # Gradient/Shape effect
    c.setFillColor(colors.HexColor(PRIMARY_BLUE))
    c.rect(0, 0, width, height, fill=1)
    
    # Header Curve
    path = c.beginPath()
    path.moveTo(0, height - 40)
    path.curveTo(width/3, height - 60, 2*width/3, height - 20, width, height - 40)
    path.lineTo(width, height)
    path.lineTo(0, height)
    path.close()
    c.setFillColor(colors.HexColor("#003399")) # Lighter Blue
    c.drawPath(path, fill=1, stroke=0)
    
    # --- INSTITUTE BRANDING ---
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width / 2, height - 15, "Y.S.M ADVANCE EDUCATION SYSTEM")
    c.setFont("Helvetica", 6)
    c.drawCentredString(width / 2, height - 23, "Excellence in Education")
    
    # --- STUDENT PHOTO ---
    # White border box for photo
    photo_x = 10
    photo_y = 50
    photo_w = 60
    photo_h = 70
    
    c.setStrokeColor(colors.white)
    c.setLineWidth(1)
    c.rect(photo_x, photo_y, photo_w, photo_h, stroke=1, fill=0)
    
    if student.photo and os.path.exists(student.photo.path):
        try:
            img = ImageReader(student.photo.path)
            c.drawImage(img, photo_x + 1, photo_y + 1, photo_w - 2, photo_h - 2)
        except:
            c.setFont("Helvetica", 6)
            c.drawCentredString(photo_x + 30, photo_y + 35, "No Photo")
    else:
        # Placeholder
        c.setFont("Helvetica", 6)
        c.drawCentredString(photo_x + 30, photo_y + 35, "No Photo")
        
    # --- STUDENT DETAILS ---
    text_x = 80
    start_y = 110
    line_h = 10
    
    c.setFillColor(colors.white)
    
    # Name (Bold & Large)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(text_x, start_y, student.name.upper())
    
    # Standard Details
    c.setFont("Helvetica", 7)
    c.drawString(text_x, start_y - 12, f"Roll No: {student.roll_number or 'N/A'}")
    c.drawString(text_x, start_y - 22, f"Class: {student.grade}")
    c.drawString(text_x, start_y - 32, f"DOB: {student.dob}")
    c.drawString(text_x, start_y - 42, f"Blood Group: {student.blood_group or '-'}")
    c.drawString(text_x, start_y - 52, f"Parent: {student.parent.username if student.parent else 'N/A'}")
    
    # --- QR CODE FOR ATTENDANCE ---
    qr = qrcode.QRCode(box_size=2, border=1)
    # The QR contains a JSON with ID, Name, and unique signature logic (simple ID for now)
    qr_data = f"STUDENT_ID:{student.id}||ROLL:{student.roll_number}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_size = 35
    c.drawInlineImage(qr_img, width - qr_size - 5, 5, width=qr_size, height=qr_size)
    
    # --- FOOTER ---
    c.setFillColor(colors.HexColor(ACCENT_GOLD))
    c.rect(0, 0, width, 3, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(10, 5, f"Issued: {timezone.now().date()}")
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
