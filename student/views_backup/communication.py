from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q

from student.models import Notification, DemoRequest
from student.serializers import NotificationSerializer
from student.permissions import IsTeacherOrAdmin

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.profile.role
        qs = Notification.objects.filter(
            Q(recipient=request.user) |
            Q(recipient_type=role) |
            Q(recipient_type='ALL')
        )
        return Response(NotificationSerializer(qs, many=True).data)

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        notification = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='ALL'),
            id=id
        ).first()

        if not notification:
            return Response({"error": "Not found"}, status=404)

        notification.is_read = True
        notification.save()
        return Response({"message": "Marked as read"})

class NotificationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DemoRequestView(APIView):
    permission_classes = [permissions.AllowAny] 
    
    def post(self, request):
        data = request.data
        try:
            demo = DemoRequest.objects.create(
                name=data.get('name'),
                phone=data.get('phone'),
                email=data.get('email'),
                institution_name=data.get('institution_name', ''),
                institution_type=data.get('institution_type', ''),
                message=data.get('message', '')
            )
            return Response({"message": "Demo request submitted successfully", "id": demo.id}, status=201)
        except Exception as e:
             return Response({"error": str(e)}, status=400)
