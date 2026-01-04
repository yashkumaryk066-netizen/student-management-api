from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from student.models import UserProfile, ClientSubscription, Notification

class Command(BaseCommand):
    help = 'Sends subscription expiry reminders and suspension notices.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        self.stdout.write(f"Running Reminder Job for {today}...")

        # Get all clients
        clients = UserProfile.objects.filter(role='CLIENT', subscription_expiry__isnull=False)
        
        count = 0
        for profile in clients:
            days_left = (profile.subscription_expiry - today).days
            user = profile.user
            email = user.email
            
            # --- PRE-EXPIRY REMINDERS ---
            if days_left in [7, 3, 1]:
                subject = f"⚠️ Action Required: Your Plan Expires in {days_left} Days"
                message = f"""
Dear {user.first_name},

Your {profile.institution_type} Subscription will expire on {profile.subscription_expiry}.

To ensure uninterrupted access to your data and features, please renew your plan now.

Login to Dashboard: https://yashamishra.pythonanywhere.com/

Thank you,
NextGen ERP Team
                """
                self.send_alert(user, subject, message)
                count += 1
                
            # --- EXPIRY DAY ---
            elif days_left == 0:
                 subject = "🚨 URGENT: Your Plan Expires Today!"
                 message = f"""
Dear {user.first_name},

This is a final reminder that your subscription expires TODAY ({profile.subscription_expiry}).

After today, your account will be restricted to READ-ONLY mode. You will not be able to add new data.

Renew Now: https://yashamishra.pythonanywhere.com/

Thank you,
NextGen ERP Team
                 """
                 self.send_alert(user, subject, message)
                 count += 1
                 
            # --- POST-EXPIRY (SUSPENSION) ---
            elif days_left in [-1, -5, -10]:
                 subject = "❌ Service Suspended: Plan Expired"
                 message = f"""
Dear {user.first_name},

Your plan expired on {profile.subscription_expiry}.
Your account is now in READ-ONLY mode.

Please renew immediately to restore full access.

Renew Now: https://yashamishra.pythonanywhere.com/

Thank you,
NextGen ERP Team
                 """
                 self.send_alert(user, subject, message)
                 count += 1

        self.stdout.write(self.style.SUCCESS(f'Sent {count} reminders.'))

    def send_alert(self, user, subject, message):
        # 1. Email
        if user.email:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True
                )
            except:
                pass
        
        # 2. In-App Notification
        Notification.objects.create(
            recipient=user,
            recipient_type='ADMIN', # Client is Admin of their institute
            title=subject,
            message=message
        )
