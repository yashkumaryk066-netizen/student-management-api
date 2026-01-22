from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, Count, Q
from django.conf import settings
from django.utils import timezone
from django.contrib.admin.models import LogEntry
from django.core.cache import cache
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .models import ClientSubscription, Payment, UserProfile, Student, SupportTicket, GlobalAnnouncement

# =========================
# CONSTANTS
# =========================
SUB_ACTIVE = 'ACTIVE'
PAYMENT_APPROVED = 'APPROVED'
AUDIT_LOG_LIMIT = 50
DASHBOARD_CACHE_KEY = "super_admin_dashboard_v2"
DASHBOARD_CACHE_TTL = 60 * 2  # 2 minutes refresh

# =========================
# SUPER ADMIN DASHBOARD API
# =========================
class SuperAdminAdvancedDashboardView(APIView):
    """
    International Level Super Admin Dashboard API
    Provides aggregation for Multi-Institute Management, Financials, and System Health.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"detail": "Restricted Access: Super Admin Only"},
                status=status.HTTP_403_FORBIDDEN
            )

        # =========================
        # 1. OVERVIEW KPIS
        # =========================
        
        # Institute Stats
        total_institutes = ClientSubscription.objects.count()
        active_institutes = ClientSubscription.objects.filter(status='ACTIVE').count()
        
        # User Stats
        total_students = Student.objects.count()
        total_users = User.objects.count()
        active_users_24h = User.objects.filter(last_login__gte=timezone.now() - timezone.timedelta(hours=24)).count()
        
        # Financial Stats
        total_revenue = Payment.objects.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_revenue = Payment.objects.filter(
            status='APPROVED', 
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        kpi_stats = {
            "institutes": total_institutes,
            "active_institutes": active_institutes,
            "students": total_students,
            "total_users": total_users,
            "revenue": str(total_revenue), 
            "monthly_revenue": str(monthly_revenue),
            "active_users_24h": active_users_24h
        }

        # =========================
        # 2. APPROVALS (PENDING)
        # =========================
        approvals = []
        
        # Pending Subscriptions
        pending_subs = ClientSubscription.objects.filter(status='PENDING').select_related('user', 'user__profile').order_by('-created_at')
        for sub in pending_subs:
            approvals.append({
                "id": sub.id,
                "type": "SUBSCRIPTION",
                "entity_name": sub.user.profile.institution_name or sub.user.username,
                "sub_text": f"{sub.user.profile.city if hasattr(sub.user.profile, 'city') else 'Location N/A'}", # Check field if exists
                "plan": sub.get_plan_type_display(),
                "amount": str(sub.amount_paid),
                "transaction_id": sub.transaction_id or "N/A",
                "status": "PENDING VERIFICATION",
                "created_at": sub.created_at,
                "time_ago": self.get_time_ago(sub.created_at),
                "icon": "🏫" if sub.plan_type == 'SCHOOL' else "🎓"
            })
            
        # Pending Payments (Manual/Bank Transfer)
        pending_payments = Payment.objects.filter(status='PENDING_VERIFICATION').select_related('user').order_by('-created_at')
        for pay in pending_payments:
            approvals.append({
                "id": pay.id,
                "type": "PAYMENT",
                "entity_name": pay.user.username,
                "sub_text": f"Payment via {pay.payment_mode}",
                "plan": "Payment Top-up",
                "amount": str(pay.amount),
                "transaction_id": pay.transaction_id or "N/A",
                "status": "CONFIRM RECEIPT",
                "created_at": pay.created_at,
                "time_ago": self.get_time_ago(pay.created_at),
                "icon": "💰"
            })
            
        # Sort approvals by date (newest first)
        approvals.sort(key=lambda x: x['created_at'], reverse=True)


        # =========================
        # 3. INSTITUTE LIST
        # =========================
        recent_institutes = []
        subs = ClientSubscription.objects.select_related('user').order_by('-created_at')[:10]
        
        for sub in subs:
            recent_institutes.append({
                "name": sub.user.get_full_name() or sub.user.username,
                "type": sub.plan_type,
                "plan": sub.plan_type,
                "status": sub.status,
                "joined": sub.created_at.strftime("%d %b %Y")
            })

        # =========================
        # 4. SYSTEM HEALTH
        # =========================
        try:
            User.objects.first()
            db_status = "HEALTHY"
        except:
            db_status = "CRITICAL"
            
        system_health = {
            "status": "ONLINE",
            "db_status": db_status,
            "latency": "24ms", 
            "storage_usage": "45%",
            "server_region": getattr(settings, "SERVER_REGION", "Global Edge")
        }

        # =========================
        # 5. SUPPORT TICKETS
        # =========================
        tickets = SupportTicket.objects.select_related('user').order_by('-created_at')[:5]
        ticket_data = []
        for t in tickets:
            ticket_data.append({
                "id": t.id,
                "subject": t.subject,
                "priority": t.priority,
                "status": t.status,
                "user": t.user.username,
                "created": t.created_at.strftime("%d %b")
            })
            
        return Response({
            "stats": kpi_stats,
            "approvals": approvals,
            "institutes": recent_institutes,
            "health": system_health,
            "tickets": ticket_data,
            "last_updated": timezone.now()
        })

    def get_time_ago(self, time):
        now = timezone.now()
        diff = now - time
        if diff.days > 0:
            return f"{diff.days} days ago"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hours ago"
        minutes = (diff.seconds // 60) % 60
        return f"{minutes} mins ago"

class AdminApprovalActionView(APIView):
    """
    Handle Approve/Reject actions for Subscriptions and Payments
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, action_type, item_id):
        if not request.user.is_superuser:
            return Response({"error": "Permission denied"}, status=403)
            
        action = request.data.get('action') # 'APPROVE' or 'REJECT'
        reason = request.data.get('reason', '')
        
        if action_type == 'SUBSCRIPTION':
            sub = get_object_or_404(ClientSubscription, id=item_id)
            if action == 'APPROVE':
                sub.activate() # Uses the model method
                self.log_action(request.user, "APPROVED_SUBSCRIPTION", f"Approved {sub.plan_type} for {sub.user.username}")
                return Response({"message": "Subscription Approved & Activated"})
            elif action == 'REJECT':
                sub.status = 'SUSPENDED' # Or Rejected
                sub.save()
                self.log_action(request.user, "REJECTED_SUBSCRIPTION", f"Rejected subscription: {reason}")
                return Response({"message": "Subscription Rejected"})
                
        elif action_type == 'PAYMENT':
            pay = get_object_or_404(Payment, id=item_id)
            if action == 'APPROVE':
                pay.status = 'APPROVED'
                pay.save()
                self.log_action(request.user, "APPROVED_PAYMENT", f"Approved payment {pay.transaction_id}")
                return Response({"message": "Payment Verified & Approved"})
            elif action == 'REJECT':
                pay.status = 'REJECTED'
                pay.save()
                self.log_action(request.user, "REJECTED_PAYMENT", f"Rejected payment: {reason}")
                return Response({"message": "Payment Rejected"})
                
        return Response({"error": "Invalid Type"}, status=400)

    def log_action(self, user, action, desc):
        # Helper to log to LogEntry or AuditLog
        from django.contrib.admin.models import LogEntry, CHANGE
        from django.contrib.contenttypes.models import ContentType
        # Simplified logging for now
        pass

# =========================
# AUDIT LOG VIEW (Enhanced)
# =========================
class AuditLogView(APIView):
    """
    Secure System Audit Logs for SuperAdmin
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Denied"}, status=403)

        logs = LogEntry.objects.select_related('user', 'content_type').order_by('-action_time')[:50]

        data = []
        for log in logs:
            data.append({
                "time": log.action_time,
                "user": log.user.username,
                "action": log.get_action_flag_display(),
                "object": log.object_repr,
                "message": log.change_message
            })

        return Response({"logs": data})
