from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import transaction
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=User)
def check_activation(sender, instance, **kwargs):
    """
    Check if user is being activated.
    Uses transaction.on_commit to ensure email is sent only after successful commit.
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Check if toggling from Inactive -> Active
            if not old_instance.is_active and instance.is_active:
                # Notify user they have been activated
                if hasattr(instance, 'profile'):
                    # Use Premium Email Service with Robust Error Handling
                    def send_activation_email():
                        try:
                            from student.services.email_service import send_approval_email
                            # Re-fetch minimal required data to avoid stale objects
                            user_refresh = User.objects.get(pk=instance.pk)
                            if hasattr(user_refresh, 'profile') and user_refresh.email:
                                send_approval_email(
                                    email=user_refresh.email,
                                    username=user_refresh.username,
                                    password=None,  # Indicates existing credentials (no new pass)
                                    plan_type=user_refresh.profile.institution_type or 'COACHING',
                                    amount='0',
                                    payment_id=None,
                                    institution_type=user_refresh.profile.institution_type,
                                )
                        except Exception as e:
                            logger.error(f"Failed to send activation email for {instance.username}: {e}")

                    # Execute only after transaction commits successfully
                    transaction.on_commit(send_activation_email)

        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Default for Superusers - Premium Setup
        if instance.is_superuser:
            UserProfile.objects.get_or_create(
                user=instance,
                defaults={
                    'role': 'ADMIN',
                    'institution_type': 'SCHOOL',
                    'subscription_plan': 'ENTERPRISE',
                    'institution_name': 'Y.S.M CENTRAL COMMAND'
                }
            )
        else:
            # Ensure profile exists for all users to prevent crashes in views
            UserProfile.objects.get_or_create(
                user=instance, 
                defaults={
                    'role': 'STUDENT', # Default safe role
                    'institution_type': 'SCHOOL'
                }
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        try:
            instance.profile.save()
        except Exception as e:
            logger.error(f"Error saving profile for user {instance.username}: {e}")
