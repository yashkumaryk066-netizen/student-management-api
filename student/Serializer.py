from rest_framework import serializers
from .models import Student, Attendence, UserProfile, Payment, Notification

class StudentSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = "__all__"
    
    def get_parent_name(self, obj):
        return obj.parent.username if obj.parent else None

class AttendenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    
    class Meta:
        model = Attendence
        fields = "__all__"

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'role', 'phone', 'created_at']
        read_only_fields = ['created_at']

class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        return obj.status != 'PAID' and obj.due_date < timezone.now().date()

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']
    
    def get_recipient_name(self, obj):
        return obj.recipient.username if obj.recipient else "All"
        
        
        
        
