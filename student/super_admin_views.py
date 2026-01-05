from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum
from django.conf import settings
from django.utils import timezone
from django.contrib.admin.models import LogEntry
from django.core.cache import cache

from .models import ClientSubscription, Payment, UserProfile


# =========================
# CONSTANTS
# =========================
SUB_ACTIVE = 'ACTIVE'
PAYMENT_APPROVED = 'APPROVED'
AUDIT_LOG_LIMIT = 50
DASHBOARD_CACHE_KEY = "super_admin_dashboard"
DASHBOARD_CACHE_TTL = 60 * 5  # 5 minutes


# =========================
# SUPER ADMIN DASHBOARD
# =========================
class SuperAdminAdvancedDashboardView(APIView):
    """
    Enterprise-Level Super Admin Dashboard
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Restricted Access"},
                status=status.HTTP_403_FORBIDDEN
            )

        # =========================
        # CACHE (Enterprise practice)
        # =========================
        cached = cache.get(DASHBOARD_CACHE_KEY)
        if cached:
            return Response(cached, status=status.HTTP_200_OK)

        today = timezone.now().date()

        # =========================
        # 1. SYSTEM HEALTH (Mocked)
        # =========================
        server_status = {
            "condition": "HEALTHY",
            "cpu_load": "12%",
            "memory_usage": "34%",
            "active_connections": 154,
            "server_region": getattr(settings, "SERVER_REGION", "unknown")
        }

        # =========================
        # 2. PEAK USAGE (Mocked)
        # =========================
        peak_usage = {
            "labels": ["09:00", "12:00", "15:00", "18:00"],
            "data": [45, 120, 85, 30]
        }

        # =========================
        # 3. ALERTS
        # =========================
        alerts = []

        expired_active_count = ClientSubscription.objects.filter(
            end_date__lt=today,
            status=SUB_ACTIVE
        ).count()

        if expired_active_count:
            alerts.append({
                "type": "SUBSCRIPTION",
                "severity": "HIGH",
                "message": f"{expired_active_count} subscriptions expired but still ACTIVE."
            })

        # =========================
        # 4. AGGREGATED STATS
        # =========================
        total_revenue = (
            Payment.objects
            .filter(status=PAYMENT_APPROVED)
            .aggregate(total=Sum('amount'))
            .get('total') or 0
        )

        stats = {
            "total_revenue": str(total_revenue),
            "total_clients": UserProfile.objects.filter(role='ADMIN').count(),
            "active_subscriptions": ClientSubscription.objects.filter(status=SUB_ACTIVE).count(),
            "growth_rate": "12%"  # Placeholder
        }

        response_data = {
            "stats": stats,
            "server_status": server_status,
            "peak_usage": peak_usage,
            "alerts": alerts,
            "maintenance_mode": getattr(settings, "MAINTENANCE_MODE", False)
        }

        # Cache result
        cache.set(DASHBOARD_CACHE_KEY, response_data, DASHBOARD_CACHE_TTL)

        return Response(response_data, status=status.HTTP_200_OK)


# =========================
# AUDIT LOG VIEW
# =========================
class AuditLogView(APIView):
    """
    Secure System Audit Logs
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Restricted Access"},
                status=status.HTTP_403_FORBIDDEN
            )

        logs = (
            LogEntry.objects
            .select_related('user', 'content_type')
            .only(
                'action_time',
                'user__username',
                'action_flag',
                'content_type__model',
                'object_repr',
                'change_message'
            )
            .order_by('-action_time')[:AUDIT_LOG_LIMIT]
        )

        data = [
            {
                "time": log.action_time,
                "user": log.user.username if log.user else "SYSTEM",
                "action": log.get_action_flag_display(),
                "model": log.content_type.model if log.content_type else None,
                "object": log.object_repr,
                "message": log.change_message
            }
            for log in logs
        ]

        return Response(
            {
                "count": len(data),
                "logs": data
            },
            status=status.HTTP_200_OK
        )
