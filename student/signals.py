from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile

@receiver(pre_save, sender=User)
def check_activation(sender, instance, **kwargs):
    """
    Check if user is being activated.
    Note: We need the 'old' instance to compare, but pre_save gives us the new one.
    To get old, we need to query DB.
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Check if toggling from Inactive -> Active
            if not old_instance.is_active and instance.is_active:
                # Check if it is an AI USER
                if hasattr(instance, 'profile') and instance.profile.role == 'AI_USER':
                    send_approval_email(instance)
        except User.DoesNotExist:
            pass

def send_approval_email(user):
    """Send approval notification"""
    try:
        subject = 'Y.S.M AI Access Approved'
        message = f"""
        Greetings {user.username},
        
        Your access request for Y.S.M Architect Intelligence (Antigravity v4.0) has been APPROVED by the Super Admin.
        
        You can now login securely using your registered credentials.
        
        Access Portal: https://yashamishra.pythonanywhere.com/api/ai/auth/
        
        Regards,
        System Admin
        """
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        
        send_mail(subject, message, email_from, recipient_list, fail_silently=True)
    except Exception as e:
        print(f"Failed to send email: {e}")
