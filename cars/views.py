from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Car, Manufacturer, ServicingCenter
from .serializers import CarSerializer, ManufacturerSerializer, ServicingCenterSerializer


class CarListCreateView(APIView):
    def get(self, request):
        cars = Car.objects.all()
        serializer = CarSerializer(cars, many=True)
        
        return Response(serializer.data)

    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarRetrieveUpdateDestroyView(APIView):
    def get(self, request, id):
        car = get_object_or_404(Car, id=id)
        serializer = CarSerializer(car)
        return Response(serializer.data)

    def put(self, request, id):
        car = get_object_or_404(Car, id=id)
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        car = get_object_or_404(Car, id=id)
        car.delete()
        return Response({"Deleted"}, status=status.HTTP_204_NO_CONTENT)

class ManufacturerListCreateView(APIView):
    def get(self, request):
        manufacturers = Manufacturer.objects.all()
        serializer = ManufacturerSerializer(manufacturers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManufacturerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManufacturerRetrieveUpdateDestroyView(APIView):
    def get(self, request, id):
        manufacturer = get_object_or_404(Manufacturer, id=id)
        serializer = ManufacturerSerializer(manufacturer)
        return Response(serializer.data)

    def put(self, request, id):
        manufacturer = get_object_or_404(Manufacturer, id=id)
        serializer = ManufacturerSerializer(manufacturer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        manufacturer = get_object_or_404(Manufacturer, id=id)
        manufacturer.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)

class ServicingCenterListCreateView(APIView):
    def get(self, request):
        centers = ServicingCenter.objects.all()
        serializer = ServicingCenterSerializer(centers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServicingCenterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServicingCenterRetrieveUpdateDestroyView(APIView):
    def get(self, request, id):
        center = get_object_or_404(ServicingCenter, id=id)
        serializer = ServicingCenterSerializer(center)
        return Response(serializer.data)

    def put(self, request, id):
        center = get_object_or_404(ServicingCenter, id=id)
        serializer = ServicingCenterSerializer(center, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        center = get_object_or_404(ServicingCenter, id=id)
        center.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_204_NO_CONTENT)
