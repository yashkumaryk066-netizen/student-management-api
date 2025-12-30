from django.db import models

class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    rental_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    charge_per_month = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField()
    def __str__(self):
        return self.name
    
class Member(models.Model):
    name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=30)
    contact_number = models.CharField(max_length=13)
    membership_type = models.CharField()
    adhar_number = models.CharField()
    late_submission_charge = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class BookedBook(models.Model):
    book = models.ForeignKey(Book, related_name="booked_books", on_delete=models.CASCADE)
    member = models.ForeignKey(Member, related_name="members", on_delete=models.CASCADE)
    provided_date = models.DateField(auto_now_add=True)
    return_date = models.DateField()
    is_returned = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.book.name} booked by {self.member.name}"

