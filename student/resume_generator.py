"""
Premium Resume PDF Generator
Creates beautiful, professional resume PDFs with modern design
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime

class PremiumResumeGenerator:
    """Generate premium PDF resumes"""
    
    def __init__(self):
        self.buffer = BytesIO()
        self.width, self.height = letter
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Custom paragraph styles for premium look"""
        
        # Name/Title style
        self.styles.add(ParagraphStyle(
            name='ResumeName',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='ResumeTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.HexColor('#6366f1'),
            borderPadding=4
        ))
        
        # Job title
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))
        
        # Company name
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6366f1'),
            spaceAfter=6,
            fontName='Helvetica-Oblique'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ResumeBodyText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#334155'),
            spaceAfter=8,
            leading=12
        ))
    
    def generate(self, resume_data):
        """
        Generate PDF resume from data
        
        Args:
            resume_data: Dictionary with resume information
        
        Returns:
            BytesIO object containing PDF
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Header
        story.extend(self._create_header(resume_data))
        
        # Professional Summary
        if resume_data.get('summary'):
            story.extend(self._create_summary(resume_data['summary']))
        
        # Experience
        if resume_data.get('experience'):
            story.extend(self._create_experience(resume_data['experience']))
        
        # Skills
        if resume_data.get('skills'):
            story.extend(self._create_skills(resume_data['skills']))
        
        # Projects
        if resume_data.get('projects'):
            story.extend(self._create_projects(resume_data['projects']))
        
        # Education
        if resume_data.get('education'):
            story.extend(self._create_education(resume_data['education']))
        
        # Certifications
        if resume_data.get('certifications'):
            story.extend(self._create_certifications(resume_data['certifications']))
        
        # Footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        
        self.buffer.seek(0)
        return self.buffer
    
    def _create_header(self, data):
        """Create resume header with contact info"""
        elements = []
        
        # Name
        name = Paragraph(data.get('name', 'Your Name'), self.styles['ResumeName'])
        elements.append(name)
        
        # Title
        title = Paragraph(data.get('title', 'Professional Title'), self.styles['ResumeTitle'])
        elements.append(title)
        
        # Contact info
        contact_parts = []
        if data.get('email'):
            contact_parts.append(f"✉ {data['email']}")
        if data.get('phone'):
            contact_parts.append(f"📞 {data['phone']}")
        if data.get('location'):
            contact_parts.append(f"📍 {data['location']}")
        
        if contact_parts:
            contact_style = ParagraphStyle(
                'Contact',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#64748b'),
                alignment=TA_CENTER,
                spaceAfter=4
            )
            contact = Paragraph(' &nbsp;|&nbsp; '.join(contact_parts), contact_style)
            elements.append(contact)
        
        # Links
        link_parts = []
        if data.get('github'):
            link_parts.append(f'<a href="{data["github"]}" color="#6366f1">GitHub</a>')
        if data.get('linkedin'):
            link_parts.append(f'<a href="{data["linkedin"]}" color="#6366f1">LinkedIn</a>')
        if data.get('website'):
            link_parts.append(f'<a href="{data["website"]}" color="#6366f1">Portfolio</a>')
        
        if link_parts:
            link_style = ParagraphStyle(
                'Links',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#6366f1'),
                alignment=TA_CENTER,
                spaceAfter=16
            )
            links = Paragraph(' &nbsp;•&nbsp; '.join(link_parts), link_style)
            elements.append(links)
        
        # Separator line
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_summary(self, summary):
        """Create professional summary section"""
        elements = []
        elements.append(Paragraph('PROFESSIONAL SUMMARY', self.styles['SectionHeading']))
        elements.append(Paragraph(summary, self.styles['ResumeBodyText']))
        return elements
    
    def _create_experience(self, experiences):
        """Create experience section"""
        elements = []
        elements.append(Paragraph('EXPERIENCE', self.styles['SectionHeading']))
        
        for exp in experiences:
            # Job title and dates
            title_date = f"{exp.get('title', '')} <i>({exp.get('start_date', '')} - {exp.get('end_date', 'Present')})</i>"
            elements.append(Paragraph(title_date, self.styles['JobTitle']))
            
            # Company
            company_loc = exp.get('company', '')
            if exp.get('location'):
                company_loc += f" • {exp['location']}"
            elements.append(Paragraph(company_loc, self.styles['Company']))
            
            # Description
            if exp.get('description'):
                elements.append(Paragraph(exp['description'], self.styles['ResumeBodyText']))
            
            # Achievements
            if exp.get('achievements'):
                for achievement in exp['achievements']:
                    bullet = Paragraph(f"• {achievement}", self.styles['ResumeBodyText'])
                    elements.append(bullet)
            
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_skills(self, skills_by_category):
        """Create skills section with categories"""
        elements = []
        elements.append(Paragraph('TECHNICAL SKILLS', self.styles['SectionHeading']))
        
        for category, skills in skills_by_category.items():
            skill_list = ', '.join(skills)
            category_text = f"<b>{category}:</b> {skill_list}"
            elements.append(Paragraph(category_text, self.styles['ResumeBodyText']))
        
        return elements
    
    def _create_projects(self, projects):
        """Create projects section"""
        elements = []
        elements.append(Paragraph('KEY PROJECTS', self.styles['SectionHeading']))
        
        for project in projects[:5]:  # Top 5 projects
            # Project name
            proj_name = project.get('name', '')
            if project.get('url'):
                proj_name = f'<a href="{project["url"]}" color="#6366f1"><b>{proj_name}</b></a>'
            else:
                proj_name = f'<b>{proj_name}</b>'
            
            elements.append(Paragraph(proj_name, self.styles['ResumeBodyText']))
            
            # Description
            if project.get('description'):
                elements.append(Paragraph(project['description'], self.styles['ResumeBodyText']))
            
            # Tech stack
            if project.get('tech_stack'):
                tech = f"<i>Technologies: {', '.join(project['tech_stack'])}</i>"
                elements.append(Paragraph(tech, self.styles['ResumeBodyText']))
            
            elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _create_education(self, education_list):
        """Create education section"""
        elements = []
        elements.append(Paragraph('EDUCATION', self.styles['SectionHeading']))
        
        for edu in education_list:
            degree = f"<b>{edu.get('degree', '')}</b> - {edu.get('year', '')}"
            elements.append(Paragraph(degree, self.styles['ResumeBodyText']))
            
            institution = edu.get('institution', '')
            if edu.get('location'):
                institution += f", {edu['location']}"
            elements.append(Paragraph(institution, self.styles['ResumeBodyText']))
            
            if edu.get('description'):
                elements.append(Paragraph(edu['description'], self.styles['ResumeBodyText']))
            
            elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _create_certifications(self, certs):
        """Create certifications section"""
        elements = []
        elements.append(Paragraph('CERTIFICATIONS', self.styles['SectionHeading']))
        
        for cert in certs:
            cert_text = f"• <b>{cert.get('name', '')}</b> - {cert.get('issuer', '')} ({cert.get('date', '')})"
            elements.append(Paragraph(cert_text, self.styles['ResumeBodyText']))
        
        return elements
    
    def _create_footer(self):
        """Create footer"""
        elements = []
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#94a3b8'),
            alignment=TA_CENTER,
            spaceBefore=20
        )
        
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y')} • References available upon request"
        elements.append(Paragraph(footer_text, footer_style))
        
        return elements
    
    def _add_page_number(self, canvas, doc):
        """Add page number to each page"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#94a3b8'))
        canvas.drawRightString(7.5*inch, 0.5*inch, text)
