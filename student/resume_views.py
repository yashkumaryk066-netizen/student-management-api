"""
Resume Download View
Serves dynamically generated PDF resumes
"""

from django.http import HttpResponse, FileResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .resume_generator import PremiumResumeGenerator
import logging

logger = logging.getLogger(__name__)


class DownloadResumeView(View):
    """
    Generate and download resume as PDF
    Public endpoint - doesn't require authentication
    """
    
    def get(self, request):
        """Generate and return PDF resume"""
        
        try:
            # Prepare resume data (hardcoded for Yash's profile)
            # In future, this can pull from ResumeProfile model
            resume_data = self._get_resume_data()
            
            # Generate PDF
            generator = PremiumResumeGenerator()
            pdf_buffer = generator.generate(resume_data)
            
            # Track download (optional)
            self._track_download(request)
            
            # Return PDF response
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Yash_Mishra_Resume.pdf"'
            response['Content-Length'] = len(pdf_buffer.getvalue())
            
            logger.info(f"Resume downloaded from IP: {self._get_client_ip(request)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Resume generation failed: {str(e)}")
            return HttpResponse("Error generating resume. Please try again later.", status=500)
    
    def _get_resume_data(self):
        """Get resume data - hardcoded for now, can be database-driven"""
        return {
            'name': 'Yash A Mishra',
            'title': 'Strategic Software Architect & AI Innovator',
            'email': 'yashkumaryk066@gmail.com',
            'phone': '+91 83569 26231',
            'location': 'Rangra, Bihar, India',
            'github': 'https://github.com/yashkumaryk066',
            'linkedin': 'https://linkedin.com/in/yash-mishra-developer',
            'website': 'https://yash.dev',
            
            'summary': (
                'Visionary technologist with 8+ years of experience building scalable, AI-native '
                'ecosystems and enterprise-grade software solutions. Proven track record of architecting '
                'complex systems from healthcare to education, with expertise in full-stack development, '
                'AI/ML integration, and cloud infrastructure. Founded YSM AI to democratize advanced '
                'artificial intelligence for businesses across India.'
            ),
            
            'experience': [
                {
                    'title': 'Founder & Chief Architect',
                    'company': 'YSM AI',
                    'location': 'Rangra, Bihar',
                    'start_date': '2024',
                    'end_date': 'Present',
                    'description': 'Leading next-generation AI research lab focused on AGI and automated reasoning systems.',
                    'achievements': [
                        'Built custom LLM infrastructure serving 1000+ daily users',
                        'Developed enterprise AI solutions for Fortune 500 companies',
                        'Research focus: Multi-agent systems and automated code generation'
                    ]
                },
                {
                    'title': 'Lead Software Architect',
                    'company': 'Y.S.M Advance Education',
                    'location': 'Bihar, India',
                    'start_date': '2023',
                    'end_date': 'Present',
                    'description': 'Architected comprehensive SaaS ERP managing 5000+ students and 200+ institutions.',
                    'achievements': [
                        'Designed multi-tenant architecture with role-based access control',
                        'Implemented real-time analytics dashboard processing 100K+ events daily',
                        'Integrated biometric attendance and automated grading systems',
                        'Achieved 99.9% uptime with Django + PostgreSQL + Redis stack'
                    ]
                },
                {
                    'title': 'Full Stack Developer',
                    'company': 'Ok Care Health Systems',
                    'location': 'Remote',
                    'start_date': '2021',
                    'end_date': '2022',
                    'description': 'Developed healthcare management platform with appointment scheduling and patient records.',
                    'achievements': [
                        'Built RESTful APIs serving 50K+ monthly requests',
                        'Implemented secure HIPAA-compliant data storage',
                        'Reduced patient wait times by 40% through optimized scheduling algorithms'
                    ]
                },
                {
                    'title': 'Software Engineer',
                    'company': 'Vibe Talk Communications',
                    'location': 'Remote',
                    'start_date': '2021',
                    'end_date': '2022',
                    'description': 'Developed real-time chat platform with WebSocket support and message encryption.',
                    'achievements': [
                        'Scaled to support 10K concurrent users with Redis pub/sub',
                        'Implemented end-to-end encryption for secure messaging',
                        'Optimized WebSocket connections reducing latency by 60%'
                    ]
                }
            ],
            
            'skills': {
                'Backend': ['Python', 'Django', 'FastAPI', 'Node.js', 'PostgreSQL', 'Redis', 'MongoDB'],
                'Frontend': ['React', 'Next.js', 'Vue.js', 'Tailwind CSS', 'JavaScript/TypeScript'],
                'AI/ML': ['OpenAI API', 'Anthropic Claude', 'LangChain', 'TensorFlow', 'PyTorch', 'Transformers'],
                'DevOps': ['Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Linux', 'Nginx'],
                'Tools': ['Git', 'VSCode', 'Postman', 'Figma', 'Jira']
            },
            
            'projects': [
                {
                    'name': 'YSM AI Platform',
                    'description': 'Advanced AI research lab with custom LLM infrastructure and multi-agent systems',
                    'tech_stack': ['Python', 'OpenAI', 'Claude', 'LangChain', 'FastAPI'],
                    'url': ''
                },
                {
                    'name': 'Y.S.M Advance Education ERP',
                    'description': 'Comprehensive education management system with AI-powered analytics and 20+ modules',
                    'tech_stack': ['Django', 'React', 'PostgreSQL', 'Redis', 'WebSockets'],
                    'url': ''
                },
                {
                    'name': 'Ok Care Health Platform',
                    'description': 'HIPAA-compliant healthcare management with appointment scheduling and telemedicine',
                    'tech_stack': ['Django', 'Vue.js', 'PostgreSQL', 'Stripe'],
                    'url': ''
                },
                {
                    'name': 'Vibe Talk',
                    'description': 'Real-time encrypted messaging platform with 10K+ concurrent users support',
                    'tech_stack': ['Django Channels', 'WebSockets', 'Redis', 'React'],
                    'url': ''
                },
                {
                    'name': 'Vijay Enterprises ERP',
                    'description': 'Manufacturing logistics and inventory management system',
                    'tech_stack': ['Django', 'PostgreSQL', 'Celery', 'Pandas'],
                    'url': ''
                }
            ],
            
            'education': [
                {
                    'degree': 'Bachelor of Computer Science',
                    'institution': 'Self-Taught & Online Certifications',
                    'location': 'India',
                    'year': '2016-2020',
                    'description': 'Focused on software engineering, algorithms, and distributed systems'
                }
            ],
            
            'certifications': [
                {
                    'name': 'AWS Certified Solutions Architect',
                    'issuer': 'Amazon Web Services',
                    'date': '2023'
                },
                {
                    'name': 'Advanced Python Programming',
                    'issuer': 'Coursera/University of Michigan',
                    'date': '2022'
                },
                {
                    'name': 'Full Stack Web Development',
                    'issuer': 'freeCodeCamp',
                    'date': '2020'
                }
            ]
        }
    
    def _track_download(self, request):
        """Track resume downloads for analytics"""
        try:
            from .models import ResumeDownload
            ResumeDownload.objects.create(
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:200]
            )
        except Exception:
            pass  # Don't block download if tracking fails
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip
