from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import GeneratedReport
from django.utils import timezone
import io
import csv
# import reportlab # If available, but let's stick to CSV/Text for robustness without dependencies

class ReportListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reports = GeneratedReport.objects.filter(user=request.user).order_by('-generated_at')
        data = [{
            "id": r.id,
            "name": r.name,
            "type": r.report_type,
            "date": r.generated_at.strftime("%Y-%m-%d"),
            "status": r.status,
            "url": r.file_url or "#"
        } for r in reports]
        return Response(data)

    def post(self, request):
        report_type = request.data.get('type')
        if not report_type:
             return Response({"error": "Type required"}, status=status.HTTP_400_BAD_REQUEST)

        # Create Record
        report = GeneratedReport.objects.create(
            user=request.user,
            name=f"{report_type} Report - {timezone.now().strftime('%b %Y')}",
            report_type=report_type,
            status='READY'
        )
        
        # Simulate Generation (In real app, use Celery)
        # For now, we return a mock URL
        report.file_url = f"/api/reports/download/{report.id}/"
        report.save()

        return Response({
            "message": "Report generated successfully",
            "report": {
                "id": report.id,
                "name": report.name,
                "status": "READY",
                "url": report.file_url
            }
        })

class ReportDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        try:
            report = GeneratedReport.objects.get(pk=pk, user=request.user)
            # Return a simple text file response
            content = f"Report: {report.name}\nGenerated: {report.generated_at}\nUser: {request.user.username}\n\n-- MOCK DATA --\nTotal Students: 120\nTotal Revenue: 50000"
            
            response = Response(content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="report_{pk}.txt"'
            return response
        except GeneratedReport.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)
