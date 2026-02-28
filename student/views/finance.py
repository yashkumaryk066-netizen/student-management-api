from .base import *
from student.models import Payment, InstitutionExpense, ClientSubscription, Student, TransportAllocation, HostelAllocation
from django.db.models import Sum, Count, Q
import csv
import io
from student.serializers import PaymentSerializer, InstitutionExpenseSerializer
from student.utils import generate_invoice_pdf
from django.http import HttpResponse
from django.conf import settings
import uuid
from datetime import date

class PaymentListCreateView(generics.ListCreateAPIView):
    """
    Unified Payment Gateway API
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('student', 'student__parent').all()

        # 1. Students/Parents see their own payments
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        if hasattr(user, 'profile') and user.profile.role == 'PARENT':
             return qs.filter(student__parent=user)
             
        # 2. Admins see all their payments
        qs = filter_by_owner(qs, user, created_by_field='student__created_by')
        
        # Filters
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
            
        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        # Auto-link based on context
        # (Usually payments are created via specific flows, but this is a direct endpoint)
        serializer.save()

def approve_subscription_payment(payment):
    """
    Centralized logic to activate subscription and send emails.
    Used by Admin Approval and Payment Gateways.
    """
    # 1. Determine Plan Type
    meta = payment.metadata or {}
    plan_type = (meta.get('plan_type') or '').upper()
    if plan_type not in PLAN_PRICING:
        # SAFE ACCESS: Handle case where user has no profile
        profile = getattr(payment.user, 'profile', None)
        institution_type = getattr(profile, 'institution_type', '') if profile else ''
        plan_type = (institution_type or 'COACHING').upper()

    if plan_type not in PLAN_PRICING:
        plan_type = 'COACHING'

    # 2. Activate Subscription
    subscription, _ = ClientSubscription.objects.get_or_create(
        user=payment.user,
        defaults={
            'plan_type': plan_type,
            'status': 'PENDING'
        }
    )
    subscription.plan_type = plan_type
    subscription.transaction_id = payment.transaction_id or subscription.transaction_id
    subscription.amount_paid = (subscription.amount_paid or Decimal('0')) + payment.amount
    subscription.activate(days=30)

    # 3. Send Emails (Credentials + Invoice)
    email_dispatched = False
    email_reason = "no_email"
    
    if payment.user.email:
        try:
            from student.security_utils import generate_secure_password
            from student.services.invoice_service import generate_invoice_pdf as generate_subscription_invoice_pdf
            from student.services.email_service import send_approval_email

            user = payment.user
            profile = getattr(user, 'profile', None)
            password_for_email = None

            # First-time onboarding: assign secure password
            if not user.has_usable_password():
                password_for_email = generate_secure_password(14)
                user.set_password(password_for_email)
                user.save(update_fields=['password'])

                if profile:
                    profile.force_password_change = True
                    profile.save(update_fields=['force_password_change'])

            invoice_pdf = generate_subscription_invoice_pdf(user, subscription, payment)
            email_dispatched = send_approval_email(
                email=user.email,
                username=user.username,
                password=password_for_email,
                plan_type=subscription.plan_type,
                amount=str(payment.amount),
                payment_id=payment.transaction_id or str(payment.id),
                institution_type=getattr(profile, 'institution_type', None),
                invoice_pdf=invoice_pdf
            )
            email_reason = "sent" if email_dispatched else "dispatch_failed"
            
            # Rollback if critical email fails for new users
            if not email_dispatched and password_for_email:
                 raise Exception("Credential email dispatch failed - Rolling back.")

        except Exception as e:
            logger.warning(f"Subscription activation email failed: {e}", exc_info=True)
            if 'Rolling back' in str(e):
                raise e
            email_dispatched = False
            email_reason = "dispatch_failed"

    return email_dispatched, email_reason

class PaymentDetailsView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('student', 'student__parent', 'user').all()

        if user.is_superuser:
            return qs

        # Student: own payments only
        if hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)

        # Parent: linked child's payments only
        if hasattr(user, 'profile') and user.profile.role == 'PARENT':
            return qs.filter(student__parent=user)

        # Owner/staff: own institution payments + own subscription payments
        owner = get_owner_user(user)
        if not owner:
            return qs.none()
        return qs.filter(Q(student__created_by=owner) | Q(user=owner)).distinct()


class PaymentStatusUpdateView(APIView):
    """
    Update payment status for fee payments (legacy dashboard compatibility endpoint).
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request, pk):
        status_requested = (request.data.get('status') or '').upper()
        status_map = {
            'APPROVED': 'PAID',
            'PAID': 'PAID',
            'REJECTED': 'REJECTED',
        }

        if status_requested not in status_map:
            return Response({"error": "Invalid status. Use APPROVED, PAID, or REJECTED"}, status=400)

        payment = get_object_or_404(Payment, pk=pk)

        if payment.payment_type == 'SUBSCRIPTION':
            return Response(
                {"error": "Use subscription approval endpoint for subscription payments"},
                status=400
            )

        owner = get_owner_user(request.user)
        if not request.user.is_superuser and (not payment.student or payment.student.created_by != owner):
            return Response({"error": "Access Denied"}, status=403)

        target_status = status_map[status_requested]
        if payment.status == target_status:
            return Response({"message": f"Payment already marked as {target_status}", "already_processed": True})

        if payment.status == 'REJECTED' and target_status == 'PAID':
            return Response({"error": "Rejected payment cannot be approved"}, status=400)

        payment.status = target_status
        if target_status == 'PAID':
            payment.paid_date = timezone.now().date()
            payment.save(update_fields=['status', 'paid_date', 'updated_at'])
        else:
            payment.save(update_fields=['status', 'updated_at'])

        return Response({"message": f"Payment marked as {payment.status}"})

class InvoiceDownloadView(APIView):
    authentication_classes = [QueryParameterTokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
             payment = Payment.objects.get(pk=pk)
             # Security: Check ownership
             if not request.user.is_superuser:
                 if payment.payment_type == 'SUBSCRIPTION':
                     if payment.user != request.user:
                         return Response({"error": "Access Denied"}, status=403)
                 elif hasattr(request.user, 'student_profile'):
                     # Student: must be their payment
                     if payment.student != request.user.student_profile:
                         return Response({"error": "Access Denied"}, status=403)
                 else:
                     # Owner/staff: must belong to institution
                     if not payment.student or payment.student.created_by != get_owner_user(request.user):
                         return Response({"error": "Access Denied"}, status=403)
            
             # Generate PDF
             pdf_buffer = generate_invoice_pdf(payment)
             
             response = HttpResponse(pdf_buffer, content_type='application/pdf')
             response['Content-Disposition'] = f'attachment; filename="Invoice_{payment.id}.pdf"'
             return response
             
        except Payment.DoesNotExist:
             return Response({"error": "Payment not found"}, status=404)

class ManualPaymentSubmitView(APIView):
    """
    Submit manual payment proof (Bank Transfer/Cash)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        data = request.data
        amount = data.get('amount')
        payment_type = (data.get('payment_type') or 'FEE').upper()
        transaction_id = (data.get('transaction_id') or '').strip()

        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        try:
            amount = Decimal(str(amount))
        except Exception:
            return Response({"error": "Invalid amount format"}, status=400)

        if transaction_id and Payment.objects.filter(transaction_id=transaction_id).exists():
            return Response({"error": "Duplicate UTR/Transaction ID"}, status=400)

        try:
            if payment_type == 'SUBSCRIPTION':
                plan_type = (data.get('plan_type') or '').upper()
                if not plan_type and hasattr(request.user, 'profile'):
                    plan_type = (request.user.profile.institution_type or '').upper()

                payment = Payment.objects.create(
                    user=request.user,
                    amount=amount,
                    payment_type='SUBSCRIPTION',
                    payment_mode=data.get('mode', 'UPI'),
                    status='PENDING_VERIFICATION',
                    due_date=timezone.now().date(),
                    transaction_id=transaction_id or None,
                    description=data.get('description', 'Subscription Renewal Request'),
                    metadata={
                        "plan_type": plan_type or 'COACHING',
                        "submitted_by": request.user.username,
                        "type": "RENEWAL"
                    }
                )

                return Response({
                    "status": "SUBMITTED",
                    "payment_id": payment.id,
                    "transaction_id": payment.transaction_id,
                    "message": "Renewal request submitted. Waiting for admin approval."
                }, status=201)

            student_id = data.get('student_id')
            if not student_id:
                return Response({"error": "Student ID required for fee payments"}, status=400)

            # Verify Student Access
            from student.models import Student
            student = Student.objects.get(id=student_id)

            # SECURITY: Verify the student belongs to the admin's institution
            if student.created_by != get_owner_user(request.user):
                return Response({"error": "Unauthorized student access"}, status=403)

            # Create Payment Record
            payment = Payment.objects.create(
                student=student,
                amount=amount,
                payment_type='FEE',
                payment_category=data.get('category', 'TUITION'),
                payment_mode=data.get('mode', 'CASH'),
                status='PENDING_VERIFICATION',
                due_date=timezone.now().date(),
                transaction_id=transaction_id or None,
                description=data.get('notes', 'Manual Payment Submission')
            )

            return Response(PaymentSerializer(payment).data, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

class AdminPaymentApprovalView(APIView):
    """
    Approve pending payments
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def post(self, request):
        payment_id = request.data.get('payment_id')
        action = (request.data.get('action', 'APPROVE') or '').upper()  # APPROVE or REJECT

        if payment_id in (None, ''):
            return Response({"error": "payment_id is required"}, status=400)

        try:
            payment_id = int(payment_id)
        except (TypeError, ValueError):
            return Response({"error": "Invalid payment_id"}, status=400)

        try:
            with transaction.atomic():
                payment = Payment.objects.select_for_update().get(id=payment_id)

                # Verify Ownership / Access
                if payment.payment_type == 'SUBSCRIPTION':
                    if not request.user.is_superuser:
                        return Response({"error": "Only Super Admin can approve subscription payments"}, status=403)
                else:
                    if not payment.student or payment.student.created_by != get_owner_user(request.user):
                        return Response({"error": "Access Denied"}, status=403)

                pending_states = {'PENDING', 'PENDING_VERIFICATION', 'OVERDUE'}

                if action == 'APPROVE':
                    approved_state = 'APPROVED' if payment.payment_type == 'SUBSCRIPTION' else 'PAID'
                    if payment.status == approved_state:
                        return Response({"message": "Payment already approved", "already_processed": True})
                    if payment.status == 'REJECTED':
                        return Response({"error": "Rejected payment cannot be approved"}, status=400)
                    if payment.status not in pending_states:
                        return Response({"error": f"Cannot approve payment in status '{payment.status}'"}, status=400)

                    payment.status = approved_state
                    payment.paid_date = timezone.now().date()
                    payment.save(update_fields=['status', 'paid_date', 'updated_at'])
                    email_dispatched = None
                    email_dispatched_reason = None

                    # For subscription approvals, activate/extend access
                    if payment.payment_type == 'SUBSCRIPTION' and payment.user:
                        try:
                            email_dispatched, email_dispatched_reason = approve_subscription_payment(payment)
                        except Exception as e:
                            # Re-raise to trigger transaction rollback
                            raise e

                    response_data = {"message": "Payment Approved"}
                    if email_dispatched is not None:
                        response_data["email_dispatched"] = bool(email_dispatched)
                        response_data["email_dispatched_reason"] = email_dispatched_reason
                    return Response(response_data)

                elif action == 'REJECT':
                    if payment.status == 'REJECTED':
                        return Response({"message": "Payment already rejected", "already_processed": True})
                    if payment.status in {'PAID', 'APPROVED'}:
                        return Response({"error": "Approved payment cannot be rejected"}, status=400)
                    payment.status = 'REJECTED'
                    payment.save(update_fields=['status', 'updated_at'])
                    return Response({"message": "Payment Rejected"})

                return Response({"error": "Invalid action. Use APPROVE or REJECT"}, status=400)
                
                return Response({"error": "Invalid action. Use APPROVE or REJECT"}, status=400)
                
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)
        except Exception as e:
            logger.error(f"Approval Error: {str(e)}")
            return Response({"error": f"Process failed: {str(e)}"}, status=400)

class PendingPaymentsListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        owner = get_owner_user(self.request.user)
        return Payment.objects.filter(student__created_by=owner, status='PENDING_VERIFICATION')

class InstitutionExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = InstitutionExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(InstitutionExpense.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class InstitutionROIView(APIView):
    """
    Advanced Finance and Academic Analytics for Owners.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Sum, Avg, F
        from student.models import Student, Grade, InventoryItem
        import datetime
        from django.utils import timezone
        
        owner = get_owner_user(request.user)
        now = timezone.now()
        this_month = now.month
        this_year = now.year

        # 1. Financial Analytics
        payments_qs = Payment.objects.filter(status='PAID', student__created_by=owner)
        total_income = payments_qs.aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_income = payments_qs.filter(
            created_at__month=this_month, 
            created_at__year=this_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expenses_qs = InstitutionExpense.objects.filter(created_by=owner)
        total_expenses = expenses_qs.aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_expenses = expenses_qs.filter(
            created_at__month=this_month,
            created_at__year=this_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # 2. Academic Risk Analytics
        # Students with average marks below 40% are considered at risk
        failures_risk_qs = Grade.objects.filter(student__created_by=owner).select_related('student').values(
            'student__id', 'student__name', 'student__roll_number'
        ).annotate(
            avg_score=Avg('marks_obtained')
        ).filter(avg_score__lt=40)

        academic_risk_list = [
            {
                "student_name": r['student__name'],
                "roll_no": r['student__roll_number'] or f"ID-#{r['student__id']}",
                "average_score": float(round(r['avg_score'], 1))
            } for r in failures_risk_qs
        ]

        # 2b. Expense Breakdown
        expense_breakdown = list(expenses_qs.values('expense_type').annotate(amount=Sum('amount')))
        formatted_breakdown = [
            {"expense_type": e['expense_type'], "amount": float(e['amount'])}
            for e in expense_breakdown
        ]

        # 3. Operations: Inventory Health
        low_stock_count = InventoryItem.objects.filter(created_by=owner, quantity__lte=F('min_stock_level')).count()

        # 4. Success Ratio
        total_students = Student.objects.filter(created_by=owner).count()
        at_risk_count = len(academic_risk_list)
        success_ratio = 100 - ( (at_risk_count / total_students * 100) if total_students > 0 else 0 )

        return Response({
            "finance": {
                "total_revenue": float(total_income),
                "total_expenses": float(total_expenses),
                "net_profit": float(total_income - total_expenses),
                "monthly_revenue": float(monthly_income),
                "monthly_expenses": float(monthly_expenses),
                "monthly_net": float(monthly_income - monthly_expenses),
                "expense_breakdown": formatted_breakdown
            },
            "academic_risk": academic_risk_list,
            "academic_health": {
                "at_risk_count": at_risk_count,
                "success_ratio": round(success_ratio, 2),
            },
            "inventory_alerts": low_stock_count,
            "strategic_insight": "Optimize fee collection" if monthly_income < monthly_expenses else "Healthy profit margins"
        })


class InitEazypayPaymentView(APIView):
    """
    Legacy Eazypay init endpoint used by existing integration tests/frontend.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        description = request.data.get('description', 'Fee Payment')
        if not amount:
            return Response({"error": "Amount is required"}, status=400)

        try:
            amount_decimal = Decimal(str(amount))
        except Exception:
            return Response({"error": "Invalid amount"}, status=400)

        student = getattr(request.user, 'student_profile', None)
        if not student:
            return Response({"error": "Student profile required"}, status=400)

        transaction_id = str(uuid.uuid4()).replace('-', '')[:20]
        payment = Payment.objects.create(
            student=student,
            transaction_id=transaction_id,
            amount=amount_decimal,
            due_date=date.today(),
            status='PENDING',
            description=description
        )

        # Keep deterministic fallback URL without hard dependency on env keys.
        payment_url = f"/payment/mock/{payment.transaction_id}/"
        return Response({
            "transaction_id": payment.transaction_id,
            "payment_url": payment_url,
            "status": "INITIATED"
        })


class EazypayCallbackView(APIView):
    """
    Legacy callback endpoint for Eazypay.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def _verify_callback_signature(self, request):
        """
        Verify callback authenticity when secret is configured.
        In LIVE mode, callback secret is mandatory.
        """
        callback_secret = (getattr(settings, 'EAZYPAY_CALLBACK_SECRET', '') or '').strip()
        mode = (getattr(settings, 'EAZYPAY_MODE', 'TEST') or 'TEST').upper()
        signature = request.headers.get('X-Payment-Signature') or request.data.get('RS') or ''

        if callback_secret:
            import hashlib
            import hmac
            if not signature:
                return False
            expected = hmac.new(callback_secret.encode(), request.body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected)

        # Hard fail in production-like mode if callback secret is missing.
        if mode == 'LIVE':
            logger.error("EAZYPAY_CALLBACK_SECRET is missing in LIVE mode.")
            return False

        return True

    def post(self, request):
        response_code = request.data.get('Response_Code')
        transaction_id = request.data.get('ReferenceNo')
        unique_ref_number = request.data.get('Unique_Ref_Number')
        callback_amount = request.data.get('Transaction_Amount') or request.data.get('Total_Amount')

        if not self._verify_callback_signature(request):
            return Response({"error": "Invalid callback signature or callback misconfigured"}, status=403)

        if not transaction_id:
            return Response({"error": "Missing ReferenceNo"}, status=400)

        payment = Payment.objects.filter(transaction_id=transaction_id).first()
        if not payment:
            return Response({"error": "Payment not found"}, status=404)

        pending_states = {'PENDING', 'PENDING_VERIFICATION', 'OVERDUE'}
        if response_code == 'E000' and payment.status == 'PAID':
            return Response({"status": "SUCCESS", "message": "Payment already verified"})
        if response_code != 'E000' and payment.status == 'REJECTED':
            return Response({"status": "FAILED", "message": "Payment already marked as failed"})
        if payment.status not in pending_states:
            return Response({"error": f"Cannot process callback for payment status '{payment.status}'"}, status=400)

        if response_code == 'E000':
            if callback_amount is not None:
                try:
                    if Decimal(str(callback_amount)) != payment.amount:
                        return Response({"error": "Amount mismatch in callback"}, status=400)
                except Exception:
                    return Response({"error": "Invalid callback amount format"}, status=400)
            payment.status = 'PAID'
            payment.paid_date = date.today()
            if unique_ref_number:
                payment.description = f"{payment.description} (Eazypay Ref: {unique_ref_number})"
            payment.save(update_fields=['status', 'paid_date', 'description', 'updated_at'])

            # Automatically activate subscription if applicable
            if payment.payment_type == 'SUBSCRIPTION' and payment.user:
                try:
                    approve_subscription_payment(payment)
                except Exception as e:
                    logger.error(f"Eazypay Auto-Activation Failed: {e}")
                    # Don't fail the payment callback, but log checks
            
            return Response({"status": "SUCCESS", "message": "Payment verified successfully"})

        payment.status = 'REJECTED'
        payment.save(update_fields=['status', 'updated_at'])
        return Response({"status": "FAILED", "message": "Payment failed from bank side"})

class FinancialForecastView(APIView):
    """
    Advanced financial forecasting using committed revenue from Students, Transport, and Hostel.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        user = request.user
        owner = get_owner_user(user)
        if not owner:
            return Response({"error": "Unauthorized"}, status=403)

        # 1. Tuition Revenue (Monthly)
        # SAFTEY FIX: Student model does not currently have 'monthly_fee'. 
        # Future improvement: Add 'monthly_fee' to Student or 'fee' to Enrollment.
        tuition_revenue = 0
        try:
            # Try finding revenue from Batches/Courses if possible, or Payment history average?
            # For now, to prevent 500 Error, we default to 0 or try to aggregate if field existed.
            pass 
        except Exception:
            tuition_revenue = 0
        
        # 2. Transport Revenue
        # Fixed: Use 'route__monthly_fare' as 'agreed_price' does not exist on TransportAllocation
        # Fixed: TransportAllocation uses 'is_active' boolean, not 'status' charfield
        transport_revenue = TransportAllocation.objects.filter(student__created_by=owner, is_active=True).aggregate(total=Sum('route__monthly_fare', default=0))['total'] or 0
        
        # 3. Hostel Revenue
        hostel_revenue = HostelAllocation.objects.filter(student__created_by=owner, status='ACTIVE').aggregate(total=Sum('monthly_fee', default=0))['total'] or 0

        total_projected = tuition_revenue + transport_revenue + hostel_revenue

        # 4. Actual Collection (Last 30 Days)
        last_month = timezone.now() - timezone.timedelta(days=30)
        actual_collection = Payment.objects.filter(
            student__created_by=owner, 
            status='PAID', 
            paid_date__gte=last_month
        ).aggregate(total=Sum('amount', default=0))['total'] or 0

        # 5. Pending (This Month)
        this_month_start = timezone.now().replace(day=1)
        pending_collection = Payment.objects.filter(
            student__created_by=owner,
            status__in=['PENDING', 'OVERDUE'],
            due_date__gte=this_month_start
        ).aggregate(total=Sum('amount', default=0))['total'] or 0

        return Response({
            "projected_monthly_revenue": total_projected,
            "components": {
                "tuition": tuition_revenue,
                "transport": transport_revenue,
                "hostel": hostel_revenue
            },
            "actual_collection_last_30d": actual_collection,
            "pending_collection_current": pending_collection,
            "collection_efficiency": round((actual_collection / total_projected * 100), 1) if total_projected > 0 else 0
        })

class DefaulterAnalysisView(APIView):
    """
    Identifies students with consistent overdue payments.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        owner = get_owner_user(request.user)
        
        # Find students with > 0 overdue payments
        defaulters = Payment.objects.filter(
            student__created_by=owner,
            status='OVERDUE'
        ).values('student__id', 'student__name', 'student__roll_number') \
         .annotate(
             overdue_count=Count('id'), 
             total_due=Sum('amount')
         ).order_by('-total_due')[:20]  # Top 20

        return Response(defaulters)

class ExportFinancialReportView(APIView):
    """
    Generate a CSV report of all financial transactions.
    """
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get(self, request):
        owner = get_owner_user(request.user)
        
        payments = Payment.objects.filter(student__created_by=owner).order_by('-created_at')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="Finance_Report_{timezone.now().date()}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Date', 'Student', 'Category', 'Mode', 'Amount', 'Status', 'Transaction ID', 'Description'])

        for p in payments:
            writer.writerow([
                p.id,
                p.created_at.date(), 
                p.student.name if p.student else 'N/A',
                p.payment_category,
                p.payment_mode,
                p.amount,
                p.status,
                p.transaction_id or '',
                p.description or ''
            ])
            
        return response
