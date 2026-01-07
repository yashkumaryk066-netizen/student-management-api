"""
IMPROVED PAYMENT APPROVAL FUNCTION
Replace lines 107-138 in student/admin.py
"""

def approve_payment_and_renew(self, request, queryset):
    """
    Approve payment and activate/extend subscription
    - First purchase: Send email with credentials
    - Renewal: Just extend 30 days, no new credentials
    """
    from django.core.mail import send_mail
    from django.conf import settings
    from django.utils import timezone
    
    success_count = 0
    for payment in queryset:
        if payment.status == 'APPROVED':
            self.message_user(request, f"⚠️ Payment #{payment.id} already approved.", level='warning')
            continue
        
        # Update Payment Status
        payment.status = 'APPROVED'
        payment.paid_date = timezone.now().date()
        payment.save()
        
        # Process Subscription Payment
        if payment.payment_type == 'SUBSCRIPTION' and payment.user:
            user = payment.user
            
            # Check if renewal or first purchase
            is_renewal = False
            if hasattr(user, 'profile') and user.profile.plan_purchased_at:
                is_renewal = True
            
            # Extend/Activate Subscription
            if hasattr(user, 'subscription'):
                user.subscription.activate(days=30)
                
                # Sync with UserProfile
                if hasattr(user, 'profile'):
                    if not user.profile.plan_purchased_at:
                        user.profile.plan_purchased_at = timezone.now()
                    user.profile.subscription_expiry = user.subscription.end_date
                    user.profile.is_active = True
                    user.profile.save()
            
            # Email Notification
            plan_name = user.profile.institution_type if hasattr(user, 'profile') else 'Standard'
            
            if is_renewal:
                # RENEWAL - No credentials, just extension notice
                subject = f'✅ Subscription Renewed - {plan_name} Plan'
                message = f"""
Dear {user.get_full_name() or user.username},

Your {plan_name} Plan subscription has been renewed successfully!

🔄 RENEWAL DETAILS:
- Plan Extended: +30 Days
- New Expiry: {user.profile.subscription_expiry if hasattr(user, 'profile') else 'N/A'}
- Amount Paid: ₹{payment.amount}

Continue enjoying full access to all {plan_name} features!

Dashboard: https://yashamishra.pythonanywhere.com/dashboard

Thank you for your continued trust!
Best Regards,
Y.S.M ADVANCE EDUCATION SYSTEM
                """
            else:
                # FIRST PURCHASE - Send credentials
                login_url = "https://yashamishra.pythonanywhere.com/admin/"
                subject = f'🎉 Welcome! Your {plan_name} Plan is Active'
                message = f"""
Dear {user.get_full_name() or user.username},

Welcome to Y.S.M ADVANCE EDUCATION SYSTEM!

Your payment has been approved and your {plan_name} Plan is now ACTIVE!

🔐 LOGIN CREDENTIALS:
Dashboard URL: {login_url}
Username: {user.username}
Email: {user.email}

⏰ PLAN DETAILS:
- Plan Type: {plan_name}
- Validity: 30 Days
- Expires On: {user.profile.subscription_expiry if hasattr(user, 'profile') else 'N/A'}

📌 IMPORTANT:
✅ You have access ONLY to {plan_name} plan features
✅ Please change your password after first login
✅ Renew before expiry to avoid service interruption

Get Started: {login_url}

Thank you for choosing us!
Best Regards,
Y.S.M Team
                """
            
            # Send Email
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                self.message_user(request, f"✅ Email sent to {user.email}")
            except Exception as e:
                self.message_user(request, f"⚠️ Email failed for {user.username}: {str(e)}", level='warning')
        
        success_count += 1
    
    self.message_user(request, f"✅ Successfully approved {success_count} payment(s).")

approve_payment_and_renew.short_description = "✅ Approve Payment & Activate Plan (Send Email)"
