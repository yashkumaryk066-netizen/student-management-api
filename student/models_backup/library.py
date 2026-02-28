from django.db import models
from datetime import timedelta
from django.utils import timezone
from student.conf import CURRENCY_SYMBOL
from .base import AuditModel
from .academic import Student

class LibraryBook(AuditModel):
    """Library book catalog"""
    CATEGORIES = [
        ('FICTION', 'Fiction'),
        ('NON_FICTION', 'Non-Fiction'),
        ('TEXTBOOK', 'Textbook'),
        ('REFERENCE', 'Reference'),
        ('MAGAZINE', 'Magazine'),
        ('JOURNAL', 'Journal'),
        ('EQUIPMENT', 'Lab Equipment'),
        ('ASSET', 'Other Asset'),
    ]
    
    isbn = models.CharField(max_length=13, unique=True, help_text="ISBN-10 or ISBN-13")
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    published_year = models.IntegerField()
    edition = models.CharField(max_length=50, blank=True)
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cover_image = models.ImageField(upload_to='library/covers/', null=True, blank=True)
    location_rack = models.CharField(max_length=50, blank=True, help_text="Shelf/Rack Location")
    shelf_location = models.CharField(max_length=50, blank=True)
    
    # Premium Fields
    description = models.TextField(blank=True, help_text="Synopsis or details")
    added_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.available_copies > 0

class BookIssue(AuditModel):
    """Book issue/return tracking"""
    STATUS_CHOICES = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('OVERDUE', 'Overdue'),
        ('LOST', 'Lost'),
    ]
    
    book = models.ForeignKey(LibraryBook, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ISSUED')
    fine_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.student.name} ({self.status})"
    
    def calculate_fine(self):
        """Calculate fine for overdue books"""
        if self.status == 'OVERDUE' and self.due_date < timezone.now().date():
            days_late = (timezone.now().date() - self.due_date).days
            self.fine_amount = days_late * 5  # Cost per day calculation to be externalized later
        return self.fine_amount
    
    def save(self, *args, **kwargs):
        # Update book availability
        if self.pk is None:  # New issue
            self.book.available_copies -= 1
            self.book.save()
        
        # Check if overdue
        if self.status == 'ISSUED' and self.due_date < timezone.now().date():
            self.status = 'OVERDUE'
            self.calculate_fine()
        
        # Mark as returned and restore availability
        if self.return_date and self.status != 'RETURNED':
            self.status = 'RETURNED'
            self.book.available_copies += 1
            self.book.save()
        
        super().save(*args, **kwargs)
