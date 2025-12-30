from django.db import models
from django.contrib.auth.models import User
from student.models import Student, Subject, Classroom

class Exam(models.Model):
    """Examination details"""
    EXAM_TYPES = [
        ('MID_TERM', 'Mid Term'),
        ('FINAL', 'Final_Semester'),
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
    ]
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    total_marks = models.IntegerField(default=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.subject.name}"

class Grade(models.Model):
    """Grade/Results for a student in an exam"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    grade_letter = models.CharField(max_length=2, blank=True)  # A+, A, B, etc.
    
    class Meta:
        unique_together = ['student', 'exam']

    def save(self, *args, **kwargs):
        # Auto calculate grade letter
        percentage = (self.marks_obtained / self.exam.total_marks) * 100
        if percentage >= 90: self.grade_letter = 'A+'
        elif percentage >= 80: self.grade_letter = 'A'
        elif percentage >= 70: self.grade_letter = 'B'
        elif percentage >= 60: self.grade_letter = 'C'
        elif percentage >= 50: self.grade_letter = 'D'
        else: self.grade_letter = 'F'
        super().save(*args, **kwargs)

class ResultCard(models.Model):
    """Final Report Card / Transcript"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=20)
    term = models.CharField(max_length=50)
    total_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    generated_date = models.DateField(auto_now_add=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.term} ({self.academic_year})"
