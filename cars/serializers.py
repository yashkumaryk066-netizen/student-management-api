from rest_framework import serializers
from .models import Manufacturer, Car, ServicingCenter

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["id", "name", "location", "phone_number"]

class ServicingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicingCenter
        fields = ["id", "manufacturer", "name", "address", "phone"]

class ServicingMiniCenterSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer()
    class Meta:
        model = ServicingCenter
        fields = ["id", "manufacturer", "name", "address", "phone"]
