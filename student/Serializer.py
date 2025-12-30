from rest_framework import serializers
from .models import Student,Attendence

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

class AttendenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendence
        fields = "__all__"
        
        
        
