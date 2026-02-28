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
from django.db import transaction
import string, random

from .models import (
    ClientSubscription, Payment, UserProfile, Student, 
    SupportTicket, GlobalAnnouncement, AuditLog
)
from .services.invoice_service import generate_invoice_pdf
from .services.email_service import send_credentials_with_invoice, send_approval_email, send_rejection_email

# =========================
# UTIL
# =========================
def generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

def get_time_ago(time):
    now = timezone.now()
    diff = now - time
    if diff.days > 0:
        return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hours ago"
    minutes = (diff.seconds // 60) % 60
    return f"{minutes} mins ago"

# =========================
# SUPER ADMIN DASHBOARD API
# =========================
class SuperAdminAdvancedDashboardView(APIView):
    """
    Elite Level Super Admin Dashboard API
    Provides aggregation for Multi-Institute Management, Financials, and System Health.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Restricted Access"}, status=403)

        # 1. OVERVIEW KPIS
        total_institutes = ClientSubscription.objects.count()
        active_institutes = ClientSubscription.objects.filter(status='ACTIVE').count()
        total_students = Student.objects.count()
        total_users = User.objects.count()
        active_users_24h = User.objects.filter(last_login__gte=timezone.now() - timezone.timedelta(hours=24)).count()
        
        total_revenue = Payment.objects.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0
        
        pending_count = ClientSubscription.objects.filter(status='PENDING').count() + \
                        Payment.objects.filter(status='PENDING_VERIFICATION').count()

        kpi_stats = {
            "institutes": total_institutes,
            "active_institutes": active_institutes,
            "students": total_students,
            "total_users": total_users,
            "revenue": str(total_revenue),
            "pending": pending_count,
            "active_users_24h": active_users_24h
        }

        # 2. APPROVALS (PENDING)
        approvals = []
        pending_payments = Payment.objects.filter(status='PENDING_VERIFICATION').select_related('user').order_by('-created_at')
        
        for pay in pending_payments:
            meta = pay.metadata or {}
            email = pay.user.email if pay.user else meta.get('email', 'N/A')
            entity_name = meta.get('institution_name') or (pay.user.username if pay.user else 'Public Lead')
            plan_label = meta.get('plan_type') or 'BASIC'
            
            approvals.append({
                "id": pay.id,
                "type": "PAYMENT",
                "entity_name": entity_name,
                "email": email,
                "sub_text": f"Request for {plan_label} Plan",
                "plan": plan_label,
                "amount": str(pay.amount),
                "transaction_id": pay.transaction_id or "N/A",
                "time_ago": get_time_ago(pay.created_at),
                "created_at": pay.created_at,
                "icon": "🛡️"
            })

        # 3. INSTITUTE NODES (DETAILED)
        institutes = []
        subs = ClientSubscription.objects.select_related('user', 'user__profile').order_by('-created_at')
        for s in subs:
            profile = getattr(s.user, 'profile', None)
            institutes.append({
                "id": s.user.id,
                "name": profile.institution_name if profile else s.user.username,
                "username": s.user.username,
                "password": profile.temp_password if profile else "******",
                "type": s.plan_type,
                "plan": profile.subscription_plan if profile else "BASIC",
                "status": s.status,
                "is_active": s.user.is_active,
                "expiry": s.end_date.strftime("%d %b %Y") if s.end_date else "N/A",
                "days_left": s.days_remaining,
                "joined": s.created_at.strftime("%d %b %Y")
            })

        # 4. SYSTEM HEALTH
        system_health = {
            "db_status": "HEALTHY",
            "latency": "24ms", 
            "storage_usage": "45%",
        }

        # 5. MOCK ANALYTICS
        analytics_charts = {
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "registrations": [12, 19, 3, 5, 2, 3],
            "revenue": [12000, 19000, 3000, 5000, 2000, 3000]
        }

        # 6. SUPPORT TICKETS (RECENT)
        tickets = SupportTicket.objects.select_related('user').order_by('-created_at')[:10]
        ticket_data = [{
            "id": t.id,
            "user": t.user.username,
            "subject": t.subject,
            "priority": t.priority,
            "status": t.status,
            "time_ago": get_time_ago(t.created_at)
        } for t in tickets]

        # 7. RECENT SUCCESSFUL REVENUE (LEDGER)
        recent_revenue = Payment.objects.filter(status='APPROVED').select_related('user').order_by('-created_at')[:10]
        revenue_data = [{
            "id": r.id,
            "entity": r.user.username if r.user else "Public",
            "amount": str(r.amount),
            "ref": r.transaction_id,
            "time": r.created_at.strftime("%d %b, %H:%M")
        } for r in recent_revenue]

        return Response({
            "stats": kpi_stats,
            "approvals": approvals,
            "institutes": institutes,
            "health": system_health,
            "charts": analytics_charts,
            "tickets": ticket_data,
            "ledger": revenue_data
        })

# =========================
# ADMIN ACTION CONTROL
# =========================
class AdminApprovalActionView(APIView):
    """
    Handle Complex Actions: Approve, Reject, Block, Unblock, Extend
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, action_type, item_id):
        if not request.user.is_superuser:
            return Response({"error": "Admin access required"}, status=403)
            
        action = request.data.get('action') # APPROVE, REJECT, BLOCK, UNBLOCK, EXTEND, REDUCE
        
        try:
            with transaction.atomic():
                # --- 1. APPROVAL LOGIC (Subscription/Payment) ---
                if action_type == 'PAYMENT':
                    pay = get_object_or_404(Payment, id=item_id)
                    if action == 'APPROVE':
                        # 1. Identity Verification & Provisioning
                        user = pay.user
                        if not user:
                            email = pay.metadata.get('email')
                            username = email.split('@')[0]
                            # Collision Check
                            original_username = username
                            counter = 1
                            while User.objects.filter(username=username).exists():
                                username = f"{original_username}{counter}"
                                counter += 1
                            user = User.objects.create_user(username=username, email=email)
                            pay.user = user
                        
                        # Generate Elite Credentials for New Nodes
                        password = None
                        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'CLIENT'})
                        is_new_account = not user.has_usable_password() or profile.temp_password
                        
                        if is_new_account:
                            password = generate_password()
                            user.set_password(password)
                            profile.temp_password = password
                            profile.save()
                            user.save()

                        # 2. Subscription Node Activation
                        sub, _ = ClientSubscription.objects.get_or_create(user=user)
                        sub.plan_type = pay.metadata.get('plan_type') or 'COACHING'
                        sub.amount_paid = pay.amount
                        sub.transaction_id = pay.transaction_id
                        sub.activate(days=30) 

                        # 3. Financial Settlement
                        pay.status = 'APPROVED'
                        pay.save()

                        # 4. Dispatch Credentials & Tax Invoice
                        invoice_pdf = generate_invoice_pdf(user, sub, pay)
                        send_approval_email(
                            email=user.email,
                            username=user.username,
                            password=password or "EXISTING_PASSWORD",
                            plan_type=sub.plan_type,
                            amount=str(pay.amount),
                            payment_id=pay.transaction_id,
                            invoice_pdf=invoice_pdf
                        )

                        return Response({"message": "Access Authorized. Credentials & Invoice Dispatched via Secure Mail."})

                    elif action == 'REJECT':
                        pay.status = 'REJECTED'
                        pay.save()
                        
                        send_rejection_email(
                            email=(pay.metadata or {}).get('email') or user.email,
                            plan_type=(pay.metadata or {}).get('plan_type', 'BASIC'),
                            amount=str(pay.amount),
                            payment_id=pay.transaction_id,
                            reason=request.data.get('reason', 'Verification sequence failed to validate transaction.')
                        )
                        return Response({"message": "Protocol Rejected. Notification Dispatched."})

                # --- 2. CLIENT MANAGEMENT (Block/Unblock/Extend) ---
                elif action_type == 'CLIENT':
                    user = get_object_or_404(User, id=item_id)
                    sub = get_object_or_404(ClientSubscription, user=user)
                    profile = get_object_or_404(UserProfile, user=user)

                    if action == 'BLOCK':
                        user.is_active = False
                        sub.status = 'SUSPENDED'
                        user.save()
                        sub.save()
                        return Response({"message": f"Organization {user.username} has been BLOCKED."})

                    elif action == 'UNBLOCK':
                        user.is_active = True
                        sub.status = 'ACTIVE'
                        user.save()
                        sub.save()
                        return Response({"message": f"Organization {user.username} RESTORED."})

                    elif action == 'EXTEND':
                        sub.activate(days=30)
                        profile.subscription_expiry = sub.end_date
                        profile.save()
                        # Send Renewal Email (No password)
                        pay_dummy = Payment.objects.create(
                            user=user, amount=sub.amount_paid, 
                            status='APPROVED', description='Plan Extension (Manual)'
                        )
                        invoice_pdf = generate_invoice_pdf(user, sub, pay_dummy)
                        send_credentials_with_invoice(user, None, sub.plan_type, invoice_pdf)
                        return Response({"message": f"Plan extended. Expiry: {sub.end_date}"})

                    elif action == 'UPDATE_INFO':
                        user.username = request.data.get('username', user.username)
                        user.email = request.data.get('email', user.email)
                        profile.institution_name = request.data.get('name', profile.institution_name)
                        user.save()
                        profile.save()
                        return Response({"message": "Node Identity Synchronized."})

                    elif action == 'REDUCE':
                        if sub.end_date:
                            sub.end_date -= timezone.timedelta(days=7)
                            sub.save()
                            profile.subscription_expiry = sub.end_date
                            profile.save()
                            return Response({"message": "Plan duration reduced by 7 days."})

                return Response({"error": "Invalid Command"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

# =========================
# ROOT PROFILE MANAGEMENT
# =========================
class RootProfileView(APIView):
    """
    Manage the SuperAdmin's own identity
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)
        
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'ADMIN'})
        
        return Response({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": profile.phone or "",
            "address": profile.address or "",
            "institution_name": profile.institution_name or "Y.S.M ADVANCE",
            "profile_image": profile.institution_logo.url if profile.institution_logo else None,
            "is_superuser": user.is_superuser,
            "last_login": user.last_login
        })

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Forbidden"}, status=403)
            
        user = request.user
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'ADMIN'})
        
        # Update User
        user.username = request.data.get('username', user.username)
        user.email = request.data.get('email', user.email)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.save()

        # Update Profile
        profile.phone = request.data.get('phone', profile.phone)
        profile.address = request.data.get('address', profile.address)
        profile.institution_name = request.data.get('institution_name', profile.institution_name)
        
        if 'profile_image' in request.FILES:
            profile.institution_logo = request.FILES['profile_image']
            
        profile.save()
        
        return Response({"message": "Root Identity & Profile Synchronized successfully."})

# =========================
# GLOBAL BROADCAST SYSTEM
# =========================
class SuperAdminAnnouncementView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser: return Response(status=403)
        announcements = GlobalAnnouncement.objects.select_related('created_by').order_by('-created_at')
        return Response([{
            "id": a.id,
            "title": a.title,
            "group": a.recipient_group,
            "content": a.content,
            "is_active": a.is_active,
            "created_at": a.created_at.strftime("%d %b, %H:%M")
        } for a in announcements])

    def post(self, request):
        if not request.user.is_superuser: return Response(status=403)
        title = request.data.get('title')
        content = request.data.get('content')
        group = request.data.get('recipient_group', 'ALL')
        
        announcement = GlobalAnnouncement.objects.create(
            title=title,
            content=content,
            recipient_group=group,
            created_by=request.user
        )
        return Response({"message": "Global Broadcast Dispatched Successfully."})

# =========================
# SUPPORT HUB VIEW
# =========================
class SuperAdminSupportHubView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser: return Response(status=403)
        tickets = SupportTicket.objects.select_related('user').order_by('-created_at')
        return Response([{
            "id": t.id,
            "username": t.user.username,
            "email": t.user.email,
            "subject": t.subject,
            "message": t.message,
            "status": t.status,
            "priority": t.priority,
            "created_at": t.created_at.strftime("%d %b %Y")
        } for t in tickets])

    def post(self, request, ticket_id):
        if not request.user.is_superuser: return Response(status=403)
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        action = request.data.get('action') # RESOLVE, CLOSE, IN_PROGRESS
        
        if action == 'RESOLVE':
            ticket.status = 'RESOLVED'
            ticket.resolved_at = timezone.now()
        elif action == 'IN_PROGRESS':
            ticket.status = 'IN_PROGRESS'
        elif action == 'CLOSE':
            ticket.status = 'CLOSED'
            
        ticket.save()
        return Response({"message": f"Ticket #{ticket_id} protocol updated to {ticket.status}."})

# =========================
# AUDIT LOG VIEW
# =========================
class AuditLogView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        logs = AuditLog.objects.select_related('created_by').order_by('-created_at')[:100]
        return Response({"logs": [{
            "time": l.created_at, 
            "user": l.created_by.username if l.created_by else "SYSTEM", 
            "action": l.action,
            "object": l.ip_address or "SECURE_IP", 
            "message": l.description
        } for l in logs]})
