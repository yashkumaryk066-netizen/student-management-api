from django.db import models

class Student(models.Model):
        name = models.CharField(max_length=20)
        age = models.PositiveBigIntegerField()
        gender = models.CharField(max_length=10)
        dob = models.DateField()
        grade = models.IntegerField()
        relation = models.CharField(max_length=50)
        
        def __str__(self):
            return self.name
        
        
class Attendence(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ("student", "date")

    def __str__(self):
        return f"{self.student.name} - {self.date}"

    
