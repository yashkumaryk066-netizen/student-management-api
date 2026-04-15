from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from student.models import UserProfile, ClientSubscription, Notification

class Command(BaseCommand):
    help = 'Sends subscription expiry reminders and suspension notices.'

    def handle(self, *args, **kwargs):
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from django.core.mail import EmailMessage

        today = timezone.now().date()
        self.stdout.write(f"🚀 Initializing Neural Expiry Scan for {today}...")

        # Get all clients
        clients = UserProfile.objects.filter(role='CLIENT', subscription_expiry__isnull=False)
        
        count = 0
        for profile in clients:
            days_left = (profile.subscription_expiry - today).days
            user = profile.user
            email = user.email

            # Protocol: Send alerts from 5 days before to 10 days after expiry
            # We skip if they are already renewed (days_left > 5)
            if days_left > 5:
                continue
            
            # Stop alerts after 10 days of suspension (too far gone)
            if days_left < -10:
                continue

            # --- DYNAMIC SUBJECT & MESSAGE ---
            if days_left > 0:
                title = "PLAN TERMINATION CYCLE"
                subject = f"⚠️ [ACTION REQUIRED] Plan Expires in {days_left} Days"
                days_display = f"{days_left} DAYS LEFT"
                footer_message = "Initiate renewal to avoid protocol suspension."
            elif days_left == 0:
                title = "EXPIRY PROTOCOL: TODAY"
                subject = "🚨 URGENT: System Shutdown in 24 Hours!"
                days_display = "LAST 24 HOURS"
                footer_message = "Final Warning. Read-Only mode starts tomorrow."
            else:
                 title = "SYSTEM SUSPENDED"
                 subject = f"❌ [SUSPENDED] Your Node has Expired"
                 days_display = f"{abs(days_left)} DAYS EXPIRED"
                 footer_message = "Your system is in READ-ONLY mode. Renew now to restore access."

            # --- PREMIUM HTML TEMPLATE ---
            context = {
                'title': title,
                'subject': subject,
                'plan_type': profile.institution_type or "Active",
                'days_display': days_display,
                'footer_message': footer_message,
                'site_url': settings.SITE_URL,
            }
            
            html_message = render_to_string('emails/subscription_expiry_alert.html', context)
            plain_message = strip_tags(html_message)

            self.send_alert(user, subject, plain_message, html_message)
            count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Successfully dispatched {count} neural alerts.'))

    def send_alert(self, user, subject, plain_message, html_message=None):
        from django.core.mail import EmailMessage
        # 1. Email (Enterprise Grade)
        if user.email:
            try:
                email = EmailMessage(
                    f"🚀 {subject}",
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                if html_message:
                    email.content_subtype = "html"
                    email.body = html_message
                
                email.send(fail_silently=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Fail to send email to {user.email}: {str(e)}"))
        
        # 2. In-App Notification (Glassmorphism Trigger)
        Notification.objects.create(
            recipient=user,
            recipient_type='ADMIN',
            title=subject,
            message=plain_message
        )

