from django.db import models
from django.contrib.auth.models import User
from .base import AuditModel
from .academic import Student

class Attendence(AuditModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.name} - {self.date}"
