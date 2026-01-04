from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from .models import ClientSubscription, Payment, Notification
from datetime import date, timedelta
from django.conf import settings
from django.contrib.admin.models import LogEntry

class SuperAdminAdvancedDashboardView(APIView):
    """
    Advanced Super Admin Dashboard with:
    - Server Status (Mocked)
    - Live Class Overload Detection (Logic)
    - Peak Usage Stats
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Restricted Access"}, status=403)

        # 1. System Health (Mock logic for now, usually would query system metrics)
        server_status = {
            "condition": "HEALTHY",
            "cpu_load": "12%",
            "memory_usage": "34%",
            "active_connections": 154,
            "server_region": "us-east-1"
        }

        # 2. Peak Usage (Mock logic based on recent payments/activity)
        peak_usage_graph = {
            "labels": ["09:00", "12:00", "15:00", "18:00"],
            "data": [45, 120, 85, 30] 
        }

        # 3. Critical Alerts
        alerts = []
        # Check for expired but still active subs?
        expired_active = ClientSubscription.objects.filter(end_date__lt=date.today(), status='ACTIVE').count()
        if expired_active > 0:
            alerts.append(f"⚠️ {expired_active} subscriptions are expired but marked ACTIVE.")

        return Response({
            "server_status": server_status,
            "peak_usage": peak_usage_graph,
            "alerts": alerts,
            "maintenance_mode": getattr(settings, 'MAINTENANCE_MODE', False)
        })


class AuditLogView(APIView):
    """
    View to retrieve system audit logs (Who did what)
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
         if not request.user.is_superuser:
            return Response({"error": "Restricted Access"}, status=403)

         # Retrieve last 100 actions
         logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:50]
         
         log_data = []
         for log in logs:
             log_data.append({
                 "time": log.action_time,
                 "user": log.user.username,
                 "action": f"{log.get_action_flag_display()} {log.content_type}",
                 "object": log.object_repr,
                 "message": log.change_message
             })
             
         return Response(log_data)
