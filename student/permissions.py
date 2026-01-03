from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    """Allow only users with STUDENT role"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'STUDENT'

class IsTeacher(permissions.BasePermission):
    """Allow only users with TEACHER role"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'TEACHER'

class IsParent(permissions.BasePermission):
    """Allow only users with PARENT role"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'PARENT'


class IsAdminRole(permissions.BasePermission):
    """
    Custom permission for System Superadmins ONLY.
    Clients are NOT Admins in this context. Use IsClient for them.
    """
    def has_permission(self, request, view):
        # Only Superuser is 'ADMIN' in the strict sense for Critical System Actions
        return bool(request.user and request.user.is_superuser)

class IsClient(permissions.BasePermission):
    """
    Custom permission for Subscription Clients (Schools/Coaching Owners).
    They have FULL access but ONLY to their institution type data.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Superuser implicitly has client access too (god mode)
        if request.user.is_superuser:
            return True
            
        # Check Role is CLIENT
        is_client = hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT'
        
        if is_client:
            # Check Subscription Validity
            from django.utils import timezone
            profile = request.user.profile
            if profile.subscription_expiry and profile.subscription_expiry < timezone.now().date():
                 return False # Expired
            return True
        return False

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Updated to allow Teachers OR Clients (Owners).
    Clients act as Admins for their organization.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        if hasattr(request.user, 'profile'):
             role = request.user.profile.role
             
             # Allow Access if role is TEACHER, CLIENT, or ADMIN (Legacy)
             if role in ['TEACHER', 'CLIENT', 'ADMIN']:
                 # CRITICAL: For CLIENT, check Expiry!
                 if role == 'CLIENT':
                     from django.utils import timezone
                     if request.user.profile.subscription_expiry and request.user.profile.subscription_expiry < timezone.now().date():
                         return False # Expired
                 return True
        
        return False
