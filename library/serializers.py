from rest_framework import serializers
from .models import Book, Member, BookedBook

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "name", "author", "rental_price", "charge_per_month", "is_available", "description"]
        
class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ["id", "name", "age", "gender", "contact_number", "membership_type", "adhar_number", "late_submission_charge"]
        
class BookedBookSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BookedBook
        fields = ["book", "member", "return_date", "is_returned"]