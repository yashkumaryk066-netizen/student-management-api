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
    """Allow only users with ADMIN role AND valid subscription"""
    def has_permission(self, request, view):
        # 1. Superuser always allow (Lifetime Access)
        if request.user.is_superuser:
            return True
            
        # 2. Check Role
        if hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
            # 3. Check Subscription Validity
            from django.utils import timezone
            profile = request.user.profile
            if profile.subscription_expiry and profile.subscription_expiry < timezone.now().date():
                return False # Subscription Expired
            return True
            
        return False

class IsTeacherOrAdmin(permissions.BasePermission):
    """Allow users with TEACHER or ADMIN role"""
    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role in ['TEACHER', 'ADMIN']
