from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel
from .academic import Subject, Student
from .coaching import Batch

class Exam(AuditModel):
    """Examination/Test configuration"""
    EXAM_TYPES = [
        ('UNIT', 'Unit Test'),
        ('MIDTERM', 'Mid-Term'),
        ('FINAL', 'Final Exam'),
        ('PRACTICAL', 'Practical'),
        ('ASSIGNMENT', 'Assignment'),
    ]
    
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)
    grade_class = models.CharField(max_length=50, help_text="Class 10, BSc-I, etc.", blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='exams')
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    exam_date = models.DateField()
    duration_minutes = models.IntegerField(default=180)
    academic_year = models.CharField(max_length=20, default='2024-25')
    
    class Meta:
        ordering = ['-exam_date']
    
    def __str__(self):
        batch_info = f" ({self.batch.name})" if self.batch else f" ({self.grade_class})"
        return f"{self.name} - {self.subject.name if self.subject else 'General'}{batch_info}"

class Grade(AuditModel):
    """Student exam grades/marks"""
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('ABSENT', 'Absent'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'exam']
        ordering = ['-exam__exam_date']
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {self.marks_obtained}/{self.exam.total_marks}"
    
    @property
    def percentage(self):
        return (self.marks_obtained / self.exam.total_marks) * 100
    
    def save(self, *args, **kwargs):
        # Auto-determine status
        if self.marks_obtained >= self.exam.passing_marks:
            self.status = 'PASS'
        else:
            self.status = 'FAIL'
        super().save(*args, **kwargs)

class ResultCard(AuditModel):
    """Consolidated result card for a student"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='result_cards')
    academic_year = models.CharField(max_length=20)
    semester_term = models.CharField(max_length=50, help_text="Semester 1, Term 2, etc.")
    grade_class = models.CharField(max_length=50)
    total_marks = models.DecimalField(max_digits=7, decimal_places=2)
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    result_status = models.CharField(max_length=20, choices=[('PASS', 'Pass'), ('FAIL', 'Fail'), ('PROMOTED', 'Promoted')])
    remarks = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'academic_year', 'semester_term']
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.semester_term} ({self.academic_year})"
