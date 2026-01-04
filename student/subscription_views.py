from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import ClientSubscription, UserProfile, Payment
from datetime import date, timedelta
import random
import string
import logging
from decimal import Decimal
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class SubscriptionPurchaseView(APIView):
    """
    Returns bank payment details for manual transfer.
    User will transfer money and submit UTR for verification.
    """
    permission_classes = [permissions.AllowAny]

    PRICING = {
        'SCHOOL': Decimal('1000.00'),
        'COACHING': Decimal('500.00'),
        'INSTITUTE': Decimal('1500.00')
    }

    def post(self, request):
        plan_type = request.data.get('plan_type')
        email = request.data.get('email')
        phone = request.data.get('phone')
        
        if not plan_type or not email:
            return Response({"error": "Plan Type and Email are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get pricing
        expected_price = self.PRICING.get(plan_type)
        if not expected_price:
            return Response({"error": "Invalid Plan Type"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Return bank payment details
        return Response({
            "status": "PAYMENT_PENDING",
            "plan_type": plan_type,
            "amount_to_pay": str(expected_price),
            "payment_method": "BANK_TRANSFER",
            "bank_details": {
                "account_name": "Your Institute Name",
                "account_number": "1234567890",
                "ifsc_code": "SBIN0001234",
                "bank_name": "State Bank of India",
                "branch": "Main Branch",
                "upi_id": "yourinstitute@sbi"
            },
            "qr_code_url": "/static/images/payment_qr.png",  # Upload QR code image
            "instructions": [
                f"Transfer exactly ₹{expected_price} to the above account",
                "Save your payment screenshot",
                "Note down the UTR/Transaction Reference Number",
                "Submit UTR in next step for verification",
                "Admin will verify and activate your account within 1-2 hours"
            ],
            "next_step": "/api/subscription/verify-payment/"
        })


class SubscriptionPaymentVerifyView(APIView):
    """
    User submits UTR and payment screenshot for admin verification.
    Creates a pending payment record.
    """
    permission_classes = [permissions.AllowAny]

    PRICING = {
        'SCHOOL': Decimal('1000.00'),
        'COACHING': Decimal('500.00'),
        'INSTITUTE': Decimal('1500.00')
    }

    authentication_classes = [] # Disable auth to prevent CSRF errors on public endpoint

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Dispatch Error: {str(e)}")
            return JsonResponse({
                "error": "Server Error",
                "message": f"Server failed to process request: {str(e)}"
            }, status=500)

    def post(self, request):
        try:
            email = request.data.get('email')
            phone = request.data.get('phone')
            plan_type = request.data.get('plan_type')
            utr_number = request.data.get('utr_number')  # UTR/Transaction Reference
            amount = request.data.get('amount')
            payment_screenshot = request.FILES.get('payment_screenshot')  # Optional
            
            if not all([email, plan_type, utr_number, amount]):
                return Response({
                    "error": "Missing required fields",
                    "required": ["email", "plan_type", "utr_number", "amount"]
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify minimum length for UTR
            if len(str(utr_number)) < 10:
                return Response({
                    "error": "Invalid UTR Number",
                    "message": "UTR/Transaction Reference must be at least 10 characters"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for duplicate UTR
            if Payment.objects.filter(transaction_id=utr_number).exists():
                return Response({
                    "error": "Duplicate Transaction",
                    "message": "This UTR number has already been submitted"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify pricing
            try:
                amount = Decimal(str(amount))
            except:
                amount = Decimal('0.00')
            
            expected_price = self.PRICING.get(plan_type)
            if amount < expected_price:
                return Response({
                    "error": "Insufficient Payment Amount",
                    "message": f"Required ₹{expected_price} for {plan_type} plan, but you submitted ₹{amount}",
                    "required": str(expected_price),
                    "received": str(amount)
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create or get user (without password initially)
            user, created = User.objects.get_or_create(
                username=email,
                defaults={'email': email}
            )
            
            if created:
                user.set_unusable_password()  # No access until verified
                user.save()
            
            # Create profile if not exists
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(
                    user=user,
                    role='CLIENT',
                    institution_type=plan_type,
                    phone=phone or ''
                )
            
            # Create pending payment record
            payment = Payment.objects.create(
                student=None,  # No student yet, will be linked after verification
                transaction_id=utr_number,
                amount=amount,
                due_date=date.today(),
                status='PENDING_VERIFICATION',
                description=f"{plan_type} Plan - Bank Transfer (UTR: {utr_number})"
            )
            
            # Store additional metadata
            payment.metadata = {
                'email': email,
                'phone': phone,
                'plan_type': plan_type,
                'user_id': user.id
            }
            payment.save()
            
            # Notify admin
            logger.info(f"🔔 NEW PAYMENT SUBMISSION: {plan_type} - ₹{amount} - UTR: {utr_number} - Email: {email}")
            
            return Response({
                "status": "SUBMITTED_FOR_VERIFICATION",
                "message": "Payment submitted successfully!",
                "details": {
                    "utr_number": utr_number,
                    "amount": str(amount),
                    "plan_type": plan_type,
                    "verification_status": "PENDING"
                },
                "next_steps": [
                    "Admin will verify your payment with bank statement",
                    "You will receive credentials via email/SMS within 1-2 hours",
                    "Check your email for updates"
                ],
                "estimated_activation": "1-2 hours"
            })
            
        except Exception as e:
            logger.error(f"❌ Payment Verification Failed: {str(e)}")
            # Return JSON error to prevent frontend crash
            return Response({
                "error": "Server Error",
                "message": f"Could not process payment: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminPaymentApprovalView(APIView):
    """
    Super Admin ONLY - Verifies payment from bank statement and approves/rejects.
    Regular clients cannot approve payments.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        # CRITICAL: Only superuser can approve payments
        if not request.user.is_superuser:
            return Response({
                "error": "Access Denied",
                "message": "Only super admin can approve/reject payments."
            }, status=status.HTTP_403_FORBIDDEN)
        
        payment_id = request.data.get('payment_id')
        action = request.data.get('action')  # 'approve' or 'reject'
        admin_notes = request.data.get('notes', '')
        
        if not payment_id or not action:
            return Response({"error": "payment_id and action required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payment = Payment.objects.get(id=payment_id, status='PENDING_VERIFICATION')
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found or already processed"}, status=status.HTTP_404_NOT_FOUND)
        
        metadata = payment.metadata or {}
        email = metadata.get('email')
        phone = metadata.get('phone')
        plan_type = metadata.get('plan_type')
        amount = payment.amount
        
        if action == 'approve':
            # APPROVE AND ACTIVATE SUBSCRIPTION
            try:
                user = User.objects.get(email=email)
                
                # Generate password
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                user.set_password(password)
                user.is_active = True
                user.save()
                
                # Update profile
                profile = user.profile
                profile.subscription_expiry = date.today() + timedelta(days=30)
                profile.institution_type = plan_type
                profile.role = 'ADMIN'  # Client gets ADMIN role, NOT superuser
                profile.save()
                
                # Create/update subscription
                sub, sub_created = ClientSubscription.objects.get_or_create(user=user)
                sub.plan_type = plan_type
                sub.amount_paid = amount
                sub.activate(days=30)
                
                # Update payment status
                payment.status = 'APPROVED'
                payment.description += f" | VERIFIED by {request.user.username}"
                payment.save()
                
                logger.info(f"✅ PAYMENT APPROVED: {email} - {plan_type} - ₹{amount}")
                
                # Send credentials via email
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    subject = f"🎉 {plan_type} Plan Activated - Login Credentials"
                    message = f"""
Hello!

Your {plan_type} Plan has been successfully activated!

🔐 Login Credentials:
━━━━━━━━━━━━━━━━━━━━━━━━━━
Username: {user.username}
Password: {password}
Login URL: https://yashamishra.pythonanywhere.com/login/

📅 Subscription Details:
━━━━━━━━━━━━━━━━━━━━━━━━━━
Plan: {plan_type}
Valid Until: {profile.subscription_expiry}
Amount Paid: ₹{amount}

Please change your password after your first login.

Regards,
Institute Management System Team
                    """
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    
                    logger.info(f"📧 Credentials email sent to {email}")
                    
                except Exception as mail_error:
                    logger.error(f"❌ Failed to send email to {email}: {str(mail_error)}")
                    # Don't fail the request, just log it. Admin can resend manually if needed.
                    # Don't fail the approval if email fails
                
                return Response({
                    "status": "APPROVED",
                    "message": "Payment verified and account activated. Credentials sent via email.",
                    "credentials": {
                        "username": user.username,
                        "password": password,
                        "login_url": "https://yashamishra.pythonanywhere.com/login/",
                        "valid_until": profile.subscription_expiry
                    },
                    "email_sent": True
                })
                
            except Exception as e:
                logger.error(f"❌ Approval Error: {e}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif action == 'reject':
            # REJECT PAYMENT
            payment.status = 'REJECTED'
            payment.description += f" | REJECTED by {request.user.username}: {admin_notes}"
            payment.save()
            
            logger.info(f"❌ PAYMENT REJECTED: {email} - Reason: {admin_notes}")
            
            return Response({
                "status": "REJECTED",
                "message": "Payment rejected",
                "reason": admin_notes
            })
        
        else:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)


class PendingPaymentsListView(APIView):
    """
    Admin can view all pending payments for verification.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        pending_payments = Payment.objects.filter(status='PENDING_VERIFICATION').order_by('-created_at')
        
        payments_data = []
        for payment in pending_payments:
            metadata = payment.metadata or {}
            payments_data.append({
                'id': payment.id,
                'utr_number': payment.transaction_id,
                'amount': str(payment.amount),
                'email': metadata.get('email'),
                'phone': metadata.get('phone'),
                'plan_type': metadata.get('plan_type'),
                'submitted_date': payment.due_date,
                'description': payment.description
            })
        
        return Response({
            "total_pending": len(payments_data),
            "payments": payments_data
        })


class SubscriptionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'subscription'):
            return Response({"status": "NO_SUBSCRIPTION", "message": "No active plan found."})
        
        sub = request.user.subscription
        today = date.today()
        days_left = 0
        if sub.end_date:
            days_left = (sub.end_date - today).days
        
        return Response({
            "plan_type": sub.plan_type,
            "status": sub.status,
            "start_date": sub.start_date,
            "end_date": sub.end_date,
            "days_left": days_left if days_left > 0 else 0,
            "amount_paid": sub.amount_paid,
            "is_expired": days_left <= 0
        })


class SubscriptionRenewView(APIView):
    """
    Same manual bank transfer flow for renewals.
    """
    permission_classes = [permissions.IsAuthenticated]

    PRICING = {
        'SCHOOL': Decimal('1000.00'),
        'COACHING': Decimal('500.00'),
        'INSTITUTE': Decimal('1500.00')
    }

    def post(self, request):
        if not hasattr(request.user, 'subscription'):
            return Response({
                "error": "No existing subscription found"
            }, status=status.HTTP_404_NOT_FOUND)

        sub = request.user.subscription
        plan_type = request.data.get('plan_type', sub.plan_type)
        expected_price = self.PRICING.get(plan_type)

        # Return same bank details for renewal
        return Response({
            "status": "RENEWAL_PAYMENT_PENDING",
            "plan_type": plan_type,
            "amount_to_pay": str(expected_price),
            "payment_method": "BANK_TRANSFER",
            "bank_details": {
                "account_name": "Your Institute Name",
                "account_number": "1234567890",
                "ifsc_code": "SBIN0001234",
                "bank_name": "State Bank of India",
                "upi_id": "yourinstitute@sbi"
            },
            "instructions": [
                f"Transfer exactly ₹{expected_price} for renewal",
                "Submit UTR at /api/subscription/verify-payment/",
                "Use same email: {request.user.email}"
            ]
        })
