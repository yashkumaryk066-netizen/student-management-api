"""
Premium Resume Management Models
Stores resume content for auto-generation
"""

from django.db import models
from django.contrib.auth.models import User

class ResumeProfile(models.Model):
    """Main resume profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume_profile')
    
    # Personal Info
    full_name = models.CharField(max_length=200, default='Yash A Mishra')
    title = models.CharField(max_length=200, default='Strategic Software Architect')
    tagline = models.TextField(default='Building AI-native ecosystems and enterprise-grade software')
    email = models.EmailField(default='yashkumaryk066@gmail.com')
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, default='Rangra, Bihar, India')
    website = models.URLField(blank=True, default='https://yash.dev')
    
    # Social Links
    github = models.URLField(default='https://github.com/yashkumaryk066-netizen')
    linkedin = models.URLField(default='https://www.linkedin.com/in/yash-kumar-342330213/')
    twitter = models.URLField(blank=True, default='https://x.com/yashmishra362')
    
    # Summary
    professional_summary = models.TextField(default='Visionary technologist with 8+ years building scalable AI-native ecosystems')
    
    # Metadata
    download_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Resume: {self.full_name}"


class Experience(models.Model):
    """Work experience entries"""
    resume = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='experiences')
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_date = models.CharField(max_length=50)  # e.g., "2024"
    end_date = models.CharField(max_length=50, default='Present')
    description = models.TextField()
    achievements = models.JSONField(default=list)  # List of achievement strings
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-order', '-start_date']
    
    def __str__(self):
        return f"{self.title} at {self.company}"


class Education(models.Model):
    """Educational background"""
    resume = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='education')
    
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    year = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-order', '-year']
    
    def __str__(self):
        return f"{self.degree} - {self.institution}"


class Skill(models.Model):
    """Technical skills"""
    CATEGORY_CHOICES = [
        ('BACKEND', 'Backend Development'),
        ('FRONTEND', 'Frontend Development'),
        ('AI_ML', 'AI/ML'),
        ('DEVOPS', 'DevOps & Cloud'),
        ('DATABASE', 'Database'),
        ('OTHER', 'Other'),
    ]
    
    resume = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='skills')
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    proficiency = models.IntegerField(default=80)  # 0-100
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', '-proficiency', 'order']
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class Project(models.Model):
    """Portfolio projects"""
    resume = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='projects')
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    tech_stack = models.JSONField(default=list)  # List of technologies
    url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    highlights = models.JSONField(default=list)  # List of key highlights
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-order']
    
    def __str__(self):
        return self.name


class Certification(models.Model):
    """Certifications and awards"""
    resume = models.ForeignKey(ResumeProfile, on_delete=models.CASCADE, related_name='certifications')
    
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date = models.CharField(max_length=50)
    credential_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-order', '-date']
    
    def __str__(self):
        return f"{self.name} - {self.issuer}"
