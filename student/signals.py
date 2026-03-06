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
    Check if user is being activated (inactive -> active).
    Uses transaction.on_commit to ensure email is sent only after DB commit.
    FIX C-2: Removed hasattr(instance, 'profile') guard — in pre_save, the related
    profile object isn't always cached on the instance. We re-fetch from DB in on_commit.
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if not old_instance.is_active and instance.is_active:
                user_pk = instance.pk  # Capture PK, not the stale instance

                def send_activation_email():
                    try:
                        from student.services.email_service import send_approval_email
                        user_refresh = User.objects.select_related('profile').get(pk=user_pk)
                        if user_refresh.email:
                            profile = getattr(user_refresh, 'profile', None)
                            send_approval_email(
                                email=user_refresh.email,
                                username=user_refresh.username,
                                password=None,  # No new password — just account activation notice
                                plan_type=getattr(profile, 'institution_type', None) or 'COACHING',
                                amount='0',
                                payment_id=None,
                                institution_type=getattr(profile, 'institution_type', None),
                            )
                    except Exception as e:
                        logger.error(f"Failed to send activation email for user pk={user_pk}: {e}")

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
    """
    FIX H-3: Use update_fields to avoid triggering another post_save on User,
    which would cause infinite recursion if profile.save() triggered user.save().
    Also skip if 'created' to avoid double-save with create_user_profile.
    """
    created = kwargs.get('created', False)
    if not created and hasattr(instance, 'profile'):
        try:
            # Only save profile metadata fields, not PKs/relations that could loop
            instance.profile.save(update_fields=[
                'last_login_ip', 'streak_count', 'last_activity_date',
                'force_password_change', 'last_password_change'
            ])
        except Exception as e:
            # This can fail if profile doesn't have all those fields yet — that's ok
            pass
