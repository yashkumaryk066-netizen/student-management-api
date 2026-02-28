from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class DualAuthenticationBackend(ModelBackend):
    """
    Y.S.M ADVANCE • DUAL IDENTITY RESOLVER
    Allows users to authenticate using either Username OR Email.
    Engineered for premium UX where clients might forget their handle but remember their mail.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Dual check: Username OR Email
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
            
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
        except Exception:
            return None
