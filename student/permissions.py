from rest_framework import permissions
from .plan_permissions import PLAN_FEATURES, get_user_plan

class IsPlanFeatureEnabled(permissions.BasePermission):
    """
    DRF Permission to gate API endpoints based on the User's Plan.
    Usage in View:
    permission_classes = [IsAuthenticated, IsPlanFeatureEnabled]
    required_feature = 'library' 
    """
    
    def has_permission(self, request, view):
        # 1. Unrestricted for Super Admin
        if request.user.is_superuser:
            return True
            
        # 2. Get required feature from View
        # Views must define `required_feature = '...'`
        required_feature = getattr(view, 'required_feature', None)
        
        if not required_feature:
            # If view doesn't specify a feature, we assume it's open (or handled elsewhere)
            return True
            
        # 3. Check Plan
        # 3. Check Access using Centralized Logic
        from .plan_permissions import has_feature_access
        return has_feature_access(request.user, required_feature)

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Allows access to Teachers (Staff) and Admins (Owners).
    """
    def has_object_permission(self, request, view, obj):
        # Super Admin Bypass
        if request.user.is_superuser:
            return True

        if not request.user.is_authenticated:
            return False

        # Owner Logic
        if hasattr(request.user, 'profile') and request.user.profile.role in ['CLIENT', 'ADMIN']:
            # Check if obj belongs to this owner (if obj has 'created_by' or 'user')
            # Assuming obj is usually related to the owner directly or indirectly
            # Basic check: owner is allowed
            return True

        # Staff Logic
        if hasattr(request.user, 'profile') and request.user.profile.role == 'TEACHER':
            # Staff typically can view/edit specific things, refine as needed
            return True
            
        return False

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if not request.user.is_authenticated:
            return False
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        return role in ['TEACHER', 'CLIENT', 'ADMIN', 'HR']

class StudentLimitPermission(permissions.BasePermission):
    """
    Checks if client has exceeded student limit.
    """
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return True # Placeholder for now

class IsStaffWithPermission(permissions.BasePermission):
    """
    Checks for specific granular permissions (e.g. 'can_manage_fees').
    Usage:
    permission_classes = [IsAuthenticated, IsStaffWithPermission]
    required_permission = 'can_manage_fees'
    """
    def has_permission(self, request, view):
        # 1. Super Admin / Owner always has access
        if request.user.is_superuser:
            return True
            
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return False
            
        # Owners (Clients) and Admins usually have full access within their plan
        if profile.role in ['CLIENT', 'ADMIN']:
            return True

        # 2. Check Granular Permission
        required_perm = getattr(view, 'required_permission', None)
        if not required_perm:
            return True # If no specific permission required, allow generic staff
            
        # Check if permission exists in user's profile
        # Structure: profile.permissions = {'capabilities': ['can_manage_fees', 'can_edit_students']}
        if profile.permissions and 'capabilities' in profile.permissions:
            return required_perm in profile.permissions['capabilities']
            
        return False
