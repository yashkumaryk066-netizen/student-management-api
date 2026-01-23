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
    Generate Premium "International Level" Student ID Card.
    Dimensions: ISO ID-1 (CR80) - 2.125 x 3.37 inches (53.98 x 85.60 mm)
    """
    # --- Dimensions & Canvas Setup ---
    width_mm, height_mm = 53.98, 85.60
    width_pt, height_pt = width_mm * 2.83465, height_mm * 2.83465
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width_pt, height_pt))
    
    # --- Color Palette (International Premium) ---
    COLOR_PRIMARY = colors.HexColor("#0f172a")    # Deep Navy/Slate
    COLOR_ACCENT = colors.HexColor("#f59e0b")     # Amber/Gold
    COLOR_SECONDARY = colors.HexColor("#334155")  # Lighter Slate
    COLOR_BG = colors.HexColor("#f8fafc")         # Off-white
    COLOR_TEXT_MAIN = colors.HexColor("#1e293b")
    COLOR_TEXT_MUTED = colors.HexColor("#64748b")
    
    # --- Background & Watermark ---
    # Draw full background
    c.setFillColor(COLOR_BG)
    c.rect(0, 0, width_pt, height_pt, fill=1, stroke=0)
    
    # Subtle Watermark Pattern (Abstract Curves)
    c.saveState()
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setLineWidth(0.5)
    c.setDash(1, 2)
    for i in range(0, int(height_pt), 15):
        p = c.beginPath()
        p.moveTo(0, i)
        p.curveTo(width_pt/3, i+20, 2*width_pt/3, i-20, width_pt, i)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()
    
    # --- Header Section (Curved Geometric Design) ---
    c.saveState()
    # Deep Blue Header Background
    p = c.beginPath()
    p.moveTo(0, height_pt)
    p.lineTo(width_pt, height_pt)
    p.lineTo(width_pt, height_pt - 60)
    # Beziers for a wave effect
    p.curveTo(width_pt*0.75, height_pt - 80, width_pt*0.25, height_pt - 50, 0, height_pt - 70)
    p.close()
    c.setFillColor(COLOR_PRIMARY)
    c.drawPath(p, fill=1, stroke=0)
    
    # Gold Accent Stripe
    c.setStrokeColor(COLOR_ACCENT)
    c.setLineWidth(3)
    p2 = c.beginPath()
    p2.moveTo(0, height_pt - 72)
    p2.curveTo(width_pt*0.25, height_pt - 52, width_pt*0.75, height_pt - 82, width_pt, height_pt - 62)
    c.drawPath(p2, stroke=1, fill=0)
    
    # Institution Name & Logo
    inst_name = "Y.S.M ADVANCE"
    inst_sub = "EDUCATION SYSTEM"
    owner = student.created_by
    logo_path = None
    sig_path = None

    if hasattr(owner, 'profile'):
        if owner.profile.institution_name:
            inst_name = owner.profile.institution_name.upper()
        if hasattr(owner.profile, 'institution_type'):
            # Try to get display name, fall back to raw value
            if hasattr(owner.profile, 'get_institution_type_display'):
                 inst_sub = f"{owner.profile.get_institution_type_display()} SYSTEM".upper()
            else:
                 inst_sub = f"{owner.profile.institution_type} SYSTEM".upper()
        
        # Check for Logo
        if owner.profile.institution_logo and hasattr(owner.profile.institution_logo, 'path'):
            if os.path.exists(owner.profile.institution_logo.path):
                logo_path = owner.profile.institution_logo.path
        
        # Check for Signature
        if owner.profile.digital_signature and hasattr(owner.profile.digital_signature, 'path'):
             if os.path.exists(owner.profile.digital_signature.path):
                sig_path = owner.profile.digital_signature.path
            
    c.setFillColor(colors.white)
    
    # Header Layout with Logo
    if logo_path:
        try:
            logo = ImageReader(logo_path)
            # Draw Logo (Left of center or above title)
            # Let's put it top-center, smaller
            c.drawImage(logo, width_pt/2 - 12, height_pt - 32, width=24, height=24, mask='auto', preserveAspectRatio=True)
            
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(width_pt/2, height_pt - 42, inst_name)
            
            c.setFont("Helvetica-Bold", 5)
            c.drawCentredString(width_pt/2, height_pt - 48, inst_sub)
        except Exception:
             # Fallback
             c.setFont("Helvetica-Bold", 11)
             c.drawCentredString(width_pt/2, height_pt - 25, inst_name)
             c.setFont("Helvetica-Bold", 6)
             c.drawCentredString(width_pt/2, height_pt - 35, inst_sub)
    else:
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(width_pt/2, height_pt - 25, inst_name)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(width_pt/2, height_pt - 35, inst_sub)

    c.restoreState()
    
    # --- Photo Section ---
    photo_w, photo_h = 75, 75
    photo_x = (width_pt - photo_w) / 2
    photo_y = height_pt - 155
    
    # Shadow for depth
    c.setFillColor(colors.HexColor("#cbd5e1"))
    c.roundRect(photo_x + 3, photo_y - 3, photo_w, photo_h, 8, fill=1, stroke=0)
    
    # White Border
    c.setFillColor(colors.white)
    c.roundRect(photo_x, photo_y, photo_w, photo_h, 8, fill=1, stroke=0)
    
    # Photo Placeholder or Image
    if student.photo and os.path.exists(student.photo.path):
        try:
            img = ImageReader(student.photo.path)
            # Clip path to rounded rect
            c.saveState()
            p_mask = c.beginPath()
            p_mask.roundRect(photo_x+2, photo_y+2, photo_w-4, photo_h-4, 6)
            c.clipPath(p_mask, stroke=0, fill=0)
            c.drawImage(img, photo_x, photo_y, width=photo_w, height=photo_h, preserveAspectRatio=True, anchor='c')
            c.restoreState()
        except Exception:
             c.setFillColor(colors.HexColor("#f1f5f9"))
             c.roundRect(photo_x+2, photo_y+2, photo_w-4, photo_h-4, 6, fill=1, stroke=0)
             c.setFillColor(colors.gray)
             c.setFont("Helvetica", 8)
             c.drawCentredString(width_pt/2, photo_y + photo_h/2, "No Photo")
    else:
         c.setFillColor(colors.HexColor("#f1f5f9"))
         c.roundRect(photo_x+2, photo_y+2, photo_w-4, photo_h-4, 6, fill=1, stroke=0)
         c.setFillColor(colors.gray)
         c.setFont("Helvetica", 8)
         c.drawCentredString(width_pt/2, photo_y + photo_h/2, "No Photo")

    # --- Student Details ---
    # Name
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 14)
    name = student.name.upper()
    c.drawCentredString(width_pt/2, photo_y - 20, name)
    
    # Role Badge
    c.setFillColor(COLOR_ACCENT)
    c.roundRect(width_pt/2 - 30, photo_y - 35, 60, 10, 5, fill=1, stroke=0)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(width_pt/2, photo_y - 32, "STUDENT CARD")
    
    # Data Grid
    cursor_y = photo_y - 55
    spacing = 11
    left_x = 20
    right_x = width_pt - 20
    
    def draw_row(label, value):
        nonlocal cursor_y
        c.setFillColor(COLOR_TEXT_MUTED)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(left_x, cursor_y, label)
        
        c.setFillColor(COLOR_TEXT_MAIN)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(right_x, cursor_y, str(value))
        
        # Dotted line
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.setLineWidth(0.5)
        c.setDash(1, 2)
        c.line(left_x + 35, cursor_y + 2, right_x - 5, cursor_y + 2)
        
        cursor_y -= spacing

    draw_row("ID NO", f"{student.id:06d}")
    draw_row("GRADE", student.grade)
    draw_row("DOB", student.dob)
    draw_row("PARENT", student.parent.get_full_name() if student.parent and hasattr(student.parent, 'get_full_name') and student.parent.get_full_name() else (student.parent.username if student.parent else "N/A"))
    draw_row("VALID", f"2025-2026") # Static Academic Year for Premium Feel
    
    # --- Footer / QR Code ---
    
    # Digital Signature display
    if sig_path:
        try:
            sig = ImageReader(sig_path)
            # Position: Bottom Right, above QR area approximately
            c.drawImage(sig, width_pt - 50, 15, width=40, height=25, mask='auto', preserveAspectRatio=True)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 5)
            c.drawRightString(width_pt - 10, 10, "Principal/Auth Sign")
        except Exception:
            pass

    # QR Code background container
    footer_h = 50
    c.setFillColor(colors.white)
    
    # Generate QR
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data(f"YSM|{student.id}|{student.name}|{student.grade}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    c.drawInlineImage(qr_img, width_pt/2 - 20, 25, width=40, height=40)
    
    # Fake Chip (Simulated) for high-tech look
    chip_w, chip_h = 22, 16
    chip_x = 25
    chip_y = cursor_y - 20
    
    # Only draw chip if space permits above QR? No, maybe below photo
    # Let's put chip on top left of photo
    # Actually, chip looks good on left side under details if space exists.
    # Let's skip chip to avoid clutter, focus on clean typography.
    
    # Footer Text
    c.setFillColor(COLOR_PRIMARY)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(width_pt/2, 12, "AUTHORIZED CAMPUS IDENTIFICATION")
    c.setFillColor(COLOR_ACCENT)
    c.rect(0, 0, width_pt, 5, fill=1, stroke=0)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
