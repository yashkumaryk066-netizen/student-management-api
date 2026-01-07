from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.utils import timezone
from django.db.models import Sum
from .models import Grade, Exam

def generate_progress_report_pdf(student):
    """
    Generate Comprehensive Progress Report Card
    Aggregates all Grade records for the student.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    elements = []
    
    # --- HEADER ---
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, alignment=TA_CENTER, textColor=colors.HexColor("#002366"))
    elements.append(Paragraph("Y.S.M ADVANCE EDUCATION SYSTEM", title_style))
    elements.append(Paragraph("STUDENT PROGRESS REPORT", ParagraphStyle('Sub', parent=styles['Heading2'], alignment=TA_CENTER, fontSize=14)))
    elements.append(Spacer(1, 0.4*inch))
    
    # --- STUDENT INFO ---
    info_data = [
        [f"Name: {student.name}", f"Roll No: {student.roll_number or 'N/A'}"],
        [f"Class: {student.grade}", f"Session: {timezone.now().year}-{timezone.now().year+1}"],
        [f"Parent: {student.parent.username if student.parent else 'N/A'}", f"Date: {timezone.now().date()}"]
    ]
    
    t_info = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
    t_info.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#333333")),
    ]))
    elements.append(t_info)
    elements.append(Spacer(1, 0.3*inch))
    
    # --- ACADEMIC PERFORMANCE (GRADES) ---
    # Fetch all grades for this student
    grades = Grade.objects.filter(student=student).select_related('exam', 'exam__subject').order_by('-exam__exam_date')
    
    if not grades.exists():
        elements.append(Paragraph("No exam records found for this academic session.", styles['Normal']))
    else:
        # Table Header
        data = [["Subject", "Exam Name", "Date", "Marks", "Total", "Grade", "Status"]]
        
        total_obtained = 0
        total_max = 0
        
        for g in grades:
            subject_name = g.exam.subject.name if g.exam.subject else "General"
            exam_name = g.exam.name
            date_str = g.exam.exam_date.strftime('%d/%m/%Y')
            marks = g.marks_obtained
            max_marks = g.exam.total_marks
            status = "Pass" if marks >= g.exam.passing_marks else "Fail"
            
            # Simple grading logic
            percent = (marks / max_marks) * 100
            if percent >= 90: grade_letter = "A+"
            elif percent >= 80: grade_letter = "A"
            elif percent >= 70: grade_letter = "B"
            elif percent >= 60: grade_letter = "C"
            elif percent >= 50: grade_letter = "D"
            else: grade_letter = "F"
            
            data.append([
                subject_name, exam_name, date_str, 
                f"{marks:.1f}", str(max_marks), grade_letter, status
            ])
            
            total_obtained += marks
            total_max += max_marks
            
        # Draw Table
        t_grades = Table(data, colWidths=[1.5*inch, 2*inch, 1.2*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.8*inch])
        t_grades.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")), # Header BG
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_grades)
        elements.append(Spacer(1, 0.3*inch))
        
        # --- SUMMARY ---
        overall_percent = (total_obtained / total_max * 100) if total_max > 0 else 0
        if overall_percent >= 90: final_grade = "Outstanding"
        elif overall_percent >= 75: final_grade = "Distinction"
        elif overall_percent >= 60: final_grade = "First Class"
        elif overall_percent >= 50: final_grade = "Second Class"
        else: final_grade = "Needs Improvement"
        
        summary_text = f"""
        <b>OVERALL PERFORMANCE SUMMARY</b><br/>
        Total Marks Obtained: <b>{total_obtained:.1f} / {total_max}</b><br/>
        Overall Percentage: <b>{overall_percent:.2f}%</b><br/>
        Final Remark: <b>{final_grade}</b>
        """
        
        # Performance Box (Green/Red based on pass)
        bg_color = colors.HexColor("#e8f5e9") if overall_percent >= 50 else colors.HexColor("#ffebee")
        
        t_summary = Table([[Paragraph(summary_text, styles['Normal'])]], colWidths=[7*inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, colors.grey),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        elements.append(t_summary)
        
    # --- FOOTER / SIGNATURES ---
    elements.append(Spacer(1, 1*inch))
    
    sig_data = [
        ["Class Teacher", "Principal", "Parent Signature"],
        ["_________________", "_________________", "_________________"]
    ]
    t_sig = Table(sig_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
    ]))
    elements.append(t_sig)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
