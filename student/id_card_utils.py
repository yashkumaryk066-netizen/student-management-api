from io import BytesIO
import qrcode
from reportlab.lib.pagesizes import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from django.conf import settings
from django.utils import timezone
import os

def generate_id_card_pdf(student):
    """
    Generate Advanced "Big School" Level ID Card
    Vertical Premium Design (54mm x 85.6mm)
    """
    # 0. Get Dynamic Institution Details
    owner = student.created_by
    inst_name = "Y.S.M ADVANCE"
    inst_sub = "EDUCATION SYSTEM"
    
    if hasattr(owner, 'profile') and owner.profile.institution_name:
        full_name = owner.profile.institution_name.upper()
        # Split name for layout if needed
        inst_name = full_name
        inst_sub = owner.profile.get_institution_type_display().upper() if hasattr(owner.profile, 'get_institution_type_display') else "EDUCATION"
    # Standard CR80 Size (Vertical)
    width, height = 53.98 * 2.83465, 85.60 * 2.83465 
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # --- COLORS (Premium Palette) ---
    NAVY_BLUE = colors.HexColor("#002855")
    GOLD_ACCENT = colors.HexColor("#D4AF37")
    WHITE_BG = colors.HexColor("#F8FAFC")
    TEXT_DARK = colors.HexColor("#1e293b")
    
    # 1. Background
    c.setFillColor(WHITE_BG)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    
    # 2. Header (Curved/Slant Design)
    path = c.beginPath()
    path.moveTo(0, height)
    path.lineTo(width, height)
    path.lineTo(width, height - 90)
    path.curveTo(width/2, height - 110, width/2, height - 70, 0, height - 90)
    path.close()
    c.setFillColor(NAVY_BLUE)
    c.drawPath(path, fill=1, stroke=0)
    
    # Accent Line
    c.setStrokeColor(GOLD_ACCENT)
    c.setLineWidth(2)
    path2 = c.beginPath()
    path2.moveTo(0, height - 92)
    path2.curveTo(width/2, height - 112, width/2, height - 72, width, height - 92)
    c.drawPath(path2, stroke=1, fill=0)

    # 3. Institution Logo & Name
    # Placeholder for Logo (White Circle)
    c.setFillColor(colors.white)
    c.circle(width/2, height - 40, 22, fill=1, stroke=0)
    
    # Draw Logo Image if exists (fallback to text)
    c.setFillColor(NAVY_BLUE)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 45, inst_name[:3])

    # School Name
    c.setFillColor(colors.white)
    
    # Dynamic Font Sizing for Long Names
    name_len = len(inst_name)
    font_size = 12
    if name_len > 20: font_size = 10
    if name_len > 30: font_size = 8
    
    c.setFont("Helvetica-Bold", font_size)
    c.drawCentredString(width/2, height - 75, inst_name)
    
    c.setFont("Helvetica", 6)
    c.drawCentredString(width/2, height - 85, inst_sub)

    # 4. Student Photo (Large & Centered with Border)
    photo_y = height - 190
    photo_size = 75
    photo_x = (width - photo_size) / 2
    
    # Shadow/Border
    c.setFillColor(colors.HexColor("#e2e8f0"))
    c.roundRect(photo_x - 2, photo_y - 2, photo_size + 4, photo_size + 4, 4, fill=1, stroke=0)
    
    c.setFillColor(colors.white) # Photo placeholder background
    c.rect(photo_x, photo_y, photo_size, photo_size, fill=1, stroke=0)

    if student.photo and os.path.exists(student.photo.path):
        try:
            img = ImageReader(student.photo.path)
            c.drawImage(img, photo_x, photo_y, width=photo_size, height=photo_size, mask='auto', preserveAspectRatio=True)
        except:
             c.setFont("Helvetica", 8)
             c.setFillColor(colors.gray)
             c.drawCentredString(width/2, photo_y + photo_size/2, "No Photo")
    else:
         c.setFont("Helvetica", 8)
         c.setFillColor(colors.gray)
         c.drawCentredString(width/2, photo_y + photo_size/2, "No Photo")

    # 5. Student Name & Role
    c.setFillColor(NAVY_BLUE)
    c.setFont("Helvetica-Bold", 14)
    # Split name if too long
    name = student.name.upper()
    if len(name) > 18:
        name_parts = name.split(' ')
        c.drawCentredString(width/2, photo_y - 20, " ".join(name_parts[:2]))
        c.drawCentredString(width/2, photo_y - 35, " ".join(name_parts[2:]))
        text_y = photo_y - 50
    else:
        c.drawCentredString(width/2, photo_y - 20, name)
        text_y = photo_y - 35
        
    c.setFillColor(GOLD_ACCENT)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, text_y, "STUDENT")

    # 6. Details Section (Clean Grid)
    start_y = text_y - 25
    line_h = 14
    left_margin = 25
    
    c.setFillColor(TEXT_DARK)
    
    def draw_detail_row(label, value, y):
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#64748b"))
        c.drawString(left_margin, y, label)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(NAVY_BLUE)
        c.drawRightString(width - left_margin, y, str(value))
        
    draw_detail_row("ID NO", student.id, start_y)
    draw_detail_row("GRADE", student.grade, start_y - line_h)
    draw_detail_row("DOB", student.dob, start_y - line_h*2)
    draw_detail_row("BLOOD GRP", student.blood_group or "N/A", start_y - line_h*3)
    draw_detail_row("PARENT", student.parent.username if student.parent else "N/A", start_y - line_h*4)
    
    # 7. QR Code (Footer)
    qr_size = 40
    qr_y = 35
    qr = qrcode.QRCode(box_size=2, border=0)
    qr_data = f"YSM|ID:{student.id}|{student.roll_number}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    c.drawInlineImage(qr_img, (width - qr_size)/2, qr_y, width=qr_size, height=qr_size)

    # 8. Footer Bar
    c.setFillColor(NAVY_BLUE)
    c.rect(0, 0, width, 25, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 7)
    c.drawCentredString(width/2, 14, "If found, please return to office.")
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(width/2, 6, inst_name)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
