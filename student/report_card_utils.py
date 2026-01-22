from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from django.utils import timezone
from django.db.models import Sum
from .models import Grade, Exam

def generate_progress_report_pdf(student):
    """
    Generate Comprehensive Progress Report Card
    Aggregates all Grade records for the student with enhanced design.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    styles = getSampleStyleSheet()
    
    elements = []
    
    # --- ENHANCED HEADER WITH DECORATIVE BORDER ---
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#002366"),
        spaceAfter=6,
        fontName='Helvetica-Bold',
        leading=28
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#004080"),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    # Header with decorative box
    header_content = [
        [Paragraph("Y.S.M ADVANCE EDUCATION SYSTEM", title_style)],
        [Paragraph("STUDENT PROGRESS REPORT", subtitle_style)],
        [Paragraph(f"Academic Session: {timezone.now().year}-{timezone.now().year+1}", 
                  ParagraphStyle('SessionStyle', parent=styles['Normal'], 
                                alignment=TA_CENTER, fontSize=10, 
                                textColor=colors.HexColor("#666666")))]
    ]
    
    header_table = Table(header_content, colWidths=[6.8*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#002366")),
        ('TOPPADDING', (0,0), (-1,-1), 15),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # --- ENHANCED STUDENT INFO SECTION ---
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#333333"),
        fontName='Helvetica'
    )
    
    info_data = [
        [Paragraph(f"<b>Student Name:</b> {student.name}", info_style), 
         Paragraph(f"<b>Roll Number:</b> {student.roll_number or 'N/A'}", info_style)],
        [Paragraph(f"<b>Class/Grade:</b> {student.grade}", info_style), 
         Paragraph(f"<b>Report Date:</b> {timezone.now().strftime('%d %B %Y')}", info_style)],
        [Paragraph(f"<b>Parent/Guardian:</b> {student.parent.username if student.parent else 'N/A'}", info_style), 
         Paragraph(f"<b>Academic Year:</b> {timezone.now().year}-{timezone.now().year+1}", info_style)]
    ]
    
    t_info = Table(info_data, colWidths=[3.4*inch, 3.4*inch])
    t_info.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ffffff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#dee2e6")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e9ecef")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.35*inch))
    
    # --- SECTION DIVIDER ---
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor("#002366"),
        fontName='Helvetica-Bold',
        spaceAfter=10,
        spaceBefore=5
    )
    elements.append(Paragraph("ACADEMIC PERFORMANCE DETAILS", section_header))
    elements.append(Spacer(1, 0.15*inch))
    
    # --- ENHANCED GRADES TABLE ---
    grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-exam__exam_date')
    
    if not grades.exists():
        no_data_style = ParagraphStyle(
            'NoData',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor("#666666"),
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=20
        )
        elements.append(Paragraph("⚠ No examination records found for this academic session.", no_data_style))
    else:
        # Enhanced table header
        header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER
        )
        
        data = [[
            Paragraph("Subject", header_style),
            Paragraph("Examination", header_style),
            Paragraph("Date", header_style),
            Paragraph("Scored", header_style),
            Paragraph("Total", header_style),
            Paragraph("Grade", header_style),
            Paragraph("Result", header_style)
        ]]
        
        total_obtained = 0
        total_max = 0
        pass_count = 0
        fail_count = 0
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER
        )
        
        for g in grades:
            subject_name = g.exam.subject.name if g.exam.subject else "General"
            exam_name = g.exam.name
            date_str = g.exam.exam_date.strftime('%d/%m/%Y')
            marks = g.marks_obtained
            max_marks = g.exam.total_marks
            is_pass = marks >= g.exam.passing_marks
            status = "Pass" if is_pass else "Fail"
            
            if is_pass:
                pass_count += 1
            else:
                fail_count += 1
            
            # Enhanced grading logic
            percent = (marks / max_marks) * 100
            if percent >= 90: grade_letter = "A+"
            elif percent >= 80: grade_letter = "A"
            elif percent >= 70: grade_letter = "B"
            elif percent >= 60: grade_letter = "C"
            elif percent >= 50: grade_letter = "D"
            else: grade_letter = "F"
            
            # Color code the status
            status_color = colors.HexColor("#2e7d32") if is_pass else colors.HexColor("#c62828")
            status_text = f'<font color="{status_color.hexval()}">{status}</font>'
            
            data.append([
                Paragraph(subject_name, cell_style),
                Paragraph(exam_name, cell_style),
                Paragraph(date_str, cell_style),
                Paragraph(f"{marks:.1f}", cell_style),
                Paragraph(str(max_marks), cell_style),
                Paragraph(f"<b>{grade_letter}</b>", cell_style),
                Paragraph(status_text, cell_style)
            ])
            
            total_obtained += marks
            total_max += max_marks
        
        # Create table with enhanced styling
        t_grades = Table(data, colWidths=[1.2*inch, 1.6*inch, 1*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.7*inch])
        t_grades.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#002366")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            
            # Body styling
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            
            # Grid and borders
            ('GRID', (0,0), (-1,-1), 0.75, colors.HexColor("#dee2e6")),
            ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#002366")),
            
            # Padding
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
            
            # Alternate row colors
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f9fa")]),
        ]))
        elements.append(t_grades)
        elements.append(Spacer(1, 0.35*inch))
        
        # --- ENHANCED SUMMARY SECTION ---
        elements.append(Paragraph("PERFORMANCE SUMMARY", section_header))
        elements.append(Spacer(1, 0.15*inch))
        
        overall_percent = (total_obtained / total_max * 100) if total_max > 0 else 0
        
        # Determine final grade and remark
        if overall_percent >= 90: 
            final_grade = "Outstanding"
            grade_color = "#1b5e20"
        elif overall_percent >= 75: 
            final_grade = "Distinction"
            grade_color = "#2e7d32"
        elif overall_percent >= 60: 
            final_grade = "First Class"
            grade_color = "#558b2f"
        elif overall_percent >= 50: 
            final_grade = "Second Class"
            grade_color = "#f57c00"
        else: 
            final_grade = "Needs Improvement"
            grade_color = "#c62828"
        
        summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=colors.HexColor("#333333")
        )
        
        summary_text = f"""
        <b style="color: #002366; font-size: 12px;">ACADEMIC STATISTICS</b><br/>
        <br/>
        Total Examinations Taken: <b>{len(grades)}</b><br/>
        Examinations Passed: <b style="color: #2e7d32;">{pass_count}</b> | 
        Examinations Failed: <b style="color: #c62828;">{fail_count}</b><br/>
        <br/>
        Total Marks Obtained: <b>{total_obtained:.1f}</b> out of <b>{total_max}</b><br/>
        Overall Percentage: <b style="font-size: 13px;">{overall_percent:.2f}%</b><br/>
        <br/>
        <b style="color: {grade_color}; font-size: 12px;">Final Grade: {final_grade}</b>
        """
        
        # Color-coded performance box
        bg_color = colors.HexColor("#e8f5e9") if overall_percent >= 50 else colors.HexColor("#ffebee")
        border_color = colors.HexColor("#2e7d32") if overall_percent >= 50 else colors.HexColor("#c62828")
        
        t_summary = Table([[Paragraph(summary_text, summary_style)]], colWidths=[6.8*inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 2, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 15),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
            ('LEFTPADDING', (0,0), (-1,-1), 20),
            ('RIGHTPADDING', (0,0), (-1,-1), 20),
        ]))
        elements.append(t_summary)
    
    # --- ENHANCED FOOTER / SIGNATURES ---
    elements.append(Spacer(1, 0.8*inch))
    
    sig_style = ParagraphStyle(
        'SigStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    sig_data = [
        [Paragraph("Class Teacher", sig_style), 
         Paragraph("Principal", sig_style), 
         Paragraph("Parent/Guardian", sig_style)],
        [Paragraph("_________________", sig_style), 
         Paragraph("_________________", sig_style), 
         Paragraph("_________________", sig_style)]
    ]
    
    t_sig = Table(sig_data, colWidths=[2.27*inch, 2.27*inch, 2.27*inch])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('TOPPADDING', (0,0), (-1,0), 0),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('TOPPADDING', (0,1), (-1,1), 15),
    ]))
    elements.append(t_sig)
    
    # Footer note
    elements.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
        fontName='Helvetica-Oblique'
    )
    elements.append(Paragraph(
        f"This is a computer-generated report | Generated on {timezone.now().strftime('%d %B %Y at %I:%M %p')}", 
        footer_style
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
