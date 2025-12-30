from django.db import models
from django.contrib.auth.models import User
from student.models import Student

class LibraryBook(models.Model):
    """Enhanced Book Model"""
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    edition = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    shelf_location = models.CharField(max_length=50, help_text="Row-Rack-Shelf")
    cover_image_url = models.URLField(blank=True)
    
    def __str__(self):
        return self.title

class BookIssue(models.Model):
    """Book Transaction History"""
    STATUS_CHOICES = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('LOST', 'Lost'),
        ('DAMAGED', 'Damaged'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues')
    book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ISSUED')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.student.name}"
