from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Student
from student.views import get_owner_user
import logging

logger = logging.getLogger(__name__)

class StudentApprovalView(APIView):
    """
    Handle approval or rejection of pending student requests by the Institute Owner.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Approve a student request"""
        try:
            student = get_object_or_404(Student, pk=pk)
            owner = get_owner_user(request.user)

            # Ensure the requester is the OWNER/ADMIN of this student's organization
            if student.created_by != owner:
                 return Response({"error": "Permission denied. You are not the owner of this student record."}, status=403)

            # Approve
            student.is_approved = True
            student.save()
            return Response({"success": True, "message": f"Student {student.name} approved and activated."})

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def delete(self, request, pk):
        """Reject (Delete) a student request"""
        try:
            student = get_object_or_404(Student, pk=pk)
            owner = get_owner_user(request.user)
            
            # Ensure the requester is the OWNER/ADMIN of this student's organization
            if student.created_by != owner:
                 return Response({"error": "Permission denied. Only Owner can reject requests."}, status=403)

            # Reject/Delete
            student.delete()
            return Response({"success": True, "message": "Request rejected and removed."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
