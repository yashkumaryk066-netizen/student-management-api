from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from student.models import ClientSubscription, UserProfile
from student.models import Payment
from student.models import Student
from student.models import Course, Batch
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
import datetime

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class GlobalStatsAPI(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        # 1. High Level Metrics
        total_institutes = ClientSubscription.objects.count()
        
        # Calculate SaaS Revenue (Subscription Payments)
        saas_revenue_agg = Payment.objects.filter(
            payment_type='SUBSCRIPTION', 
            status__in=['PAID', 'APPROVED']
        ).aggregate(Sum('amount'))
        
        saas_revenue = saas_revenue_agg['amount__sum'] or 0
        
        # Add legacy/direct amount_paid from ClientSubscription
        legacy_revenue = ClientSubscription.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        total_revenue = float(saas_revenue) + float(legacy_revenue)

        total_students = Student.objects.count() # Use Student model for accurate count
        pending_approvals = ClientSubscription.objects.filter(status='PENDING').count()
        
        # 2. Graph Data (Last 6 Months Revenue)
        today = timezone.now().date()
        six_months_ago = today - datetime.timedelta(days=180)
        
        monthly_revenue = Payment.objects.filter(
            payment_type='SUBSCRIPTION',
            status__in=['PAID', 'APPROVED'],
            created_at__gte=six_months_ago
        ).values('created_at__month').annotate(total=Sum('amount')).order_by('created_at__month')
        
        return Response({
            "total_institutes": total_institutes,
            "total_revenue": total_revenue,
            "total_students": total_students,
            "pending_count": pending_approvals,
            "monthly_growth": monthly_revenue
        })

class GlobalStudentListAPI(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        """
        Fetches detailed student data by combining UserProfile (Login/Auth)
        and Student (Academic) models.
        """
        query = request.GET.get('q', '')
        # Prefetch related data for performance
        students = Student.objects.select_related('user', 'parent').all().order_by('-created_at')
        
        if query:
            students = students.filter(
                Q(name__icontains=query) | 
                Q(roll_number__icontains=query) |
                Q(user__email__icontains=query)
            )

        students = students[:50] # Pagination Shield
        
        data = []
        for s in students:
            # Try to fetch institute name from the underlying user profile if linked
            institute_name = "N/A"
            if s.user and hasattr(s.user, 'profile'):
                institute_name = s.user.profile.institution_name or "N/A"
            
            data.append({
                "id": s.id,
                "name": s.name,
                "roll_no": s.roll_number or "N/A",
                "email": s.user.email if s.user else "No Account",
                "institution": institute_name,
                "grade": s.grade,
                "parent_name": s.parent.get_full_name() if s.parent else "N/A",
                "dob": s.dob,
                "status": "Active" if (s.user and s.user.is_active) else "Inactive",
                "phone": s.phone_number if hasattr(s, 'phone_number') else "N/A",
                "photo": s.photo.url if s.photo else None
            })
        return Response(data)

class GlobalClientListAPI(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        clients = ClientSubscription.objects.all().select_related('user').order_by('-created_at')
        data = []
        for c in clients:
            profile = getattr(c.user, 'profile', None)
            data.append({
                "id": c.id,
                "user_id": c.user.id,
                "username": c.user.username,
                "email": c.user.email,
                "institution": profile.institution_name if profile else "Unknown Institute",
                "plan": c.plan_type,
                "status": c.status,
                "phone": profile.phone if profile else "N/A",
                "expiry": c.end_date,
                "revenue": c.amount_paid,
                "location": profile.address if profile else "N/A"
            })
        return Response(data)

from rest_framework_simplejwt.tokens import RefreshToken

class GlobalImpersonateAPI(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request, user_id):
        try:
            # 1. Verify target user exists
            target_user = User.objects.get(id=user_id)
            
            # 2. Generate Tokens manually
            refresh = RefreshToken.for_user(target_user)
            
            # 3. Return tokens + redirect role
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': 'admin', # Assuming we are logging in as institute admins
                'message': f'Successfully logged in as {target_user.username}'
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class GlobalFinanceAPI(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        # Fetch both SUBSCRIPTION (SaaS Revenue) and FEE (Institute Throughput)
        # to give Super Admin a god-view of money movement.
        payments = Payment.objects.select_related('user', 'student').order_by('-created_at')[:100]
        
        data = []
        for p in payments:
            payer = "Unknown"
            if p.payment_type == 'SUBSCRIPTION' and p.user:
                payer = f"{p.user.username} (Client)"
            elif p.payment_type == 'FEE' and p.student:
                payer = f"{p.student.name} (Student)"

            data.append({
                "id": p.id,
                "type": p.payment_type, # SUBSCRIPTION or FEE
                "payer": payer,
                "amount": p.amount,
                "status": p.status,
                "date": p.created_at.strftime("%Y-%m-%d"),
                "mode": p.payment_mode,
                "txn_id": p.transaction_id or "N/A"
            })
        return Response(data)

class GlobalCourseListAPI(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        """
        Global view of all courses running across all institutes.
        Helpful to see what content is popular.
        """
        courses = Course.objects.all().annotate(
            batch_count=Count('batches')
        ).order_by('-created_at')[:50]
        
        data = []
        for c in courses:
            data.append({
                "id": c.id,
                "name": c.name,
                "code": c.code,
                "level": c.level,
                "fee": c.fee,
                "batches": c.batch_count,
                # Duration converted to nice string
                "duration": f"{c.duration_weeks} Weeks",
                "active": c.is_active
            })
        return Response(data)
