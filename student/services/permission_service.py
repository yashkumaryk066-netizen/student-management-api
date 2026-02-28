from django.conf import settings

class PermissionService:
    """
    Centralized Permission Logic for Granular Role-Based Access.
    """
    
    # 1. Default Logic Templates
    # These are the starting points when a client creates a new user of this role.
    # The client can toggle these off or add more in the UI.
    ROLE_DEFAULTS = {
        'TEACHER': {
            'students': ['view', 'mark_attendance'],
            'exams': ['view', 'create', 'grade'],
            'classes': ['view_schedule'],
            'homework': ['create', 'review'],
            'chat': ['access'],
        },
        'HR': {
            'staff': ['view', 'create', 'edit', 'delete'],
            'payroll': ['view', 'process'],
            'attendance': ['view_staff', 'approve_leave'],
            'reports': ['view_hr'],
        },
        'ACCOUNTANT': {
            'fees': ['view', 'collect', 'invoice'],
            'expenses': ['view', 'create'],
            'reports': ['view_financial'],
        },
        'PARENT': {
            'dashboard': ['view'],
            'attendance': ['view_own'],
            'fees': ['view_own', 'pay'],
            'exams': ['view_own'],
            'homework': ['view_own'],
            'events': ['view'],
        },
        'STUDENT': {
            'dashboard': ['view'],
            'classes': ['view_schedule'],
            'attendance': ['view_own'],
            'exams': ['view_own'],
            'homework': ['view_submit'],
            'library': ['search', 'reserve'],
            'events': ['view'],
        },
        'ADMIN': {
            # Admin typically has everything, but listing explicitly helps frontend knowing what's possible
            'students': ['view', 'edit', 'delete', 'promote'],
            'staff': ['view', 'edit', 'delete'],
            'fees': ['view', 'edit', 'delete', 'settings'],
            'exams': ['view', 'edit', 'settings'],
            'settings': ['access'],
        }
    }

    @staticmethod
    def get_role_template(role):
        """Get the default permission structure for a role"""
        return PermissionService.ROLE_DEFAULTS.get(role, {})

    @staticmethod
    def get_all_templates():
        """Return all templates for the frontend to cache/use"""
        return PermissionService.ROLE_DEFAULTS

    @staticmethod
    def has_permission(user, module, action):
        """
        Check if a user has a specific granular permission.
        
        Logic:
        1. Superuser/Client Owner -> True (Always)
        2. Check Granular 'permissions' JSON in UserProfile
        3. No 'permissions' set? -> Fallback to ROLE_DEFAULTS
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        if not hasattr(user, 'profile'):
            return False

        # Owner (CLIENT) has full access
        if user.profile.role == 'CLIENT':
            return True

        # Custom/Explicit Permissions stored in DB
        # Structure stored: {'students': ['view', 'edit'], 'fees': ['view']}
        user_perms = user.profile.permissions or {}
        
        # If user has explicit permissions set for this module, check them
        # Note: If 'permissions' is set in DB, we rely ONLY on it (Strict Mode), 
        # unless it's empty, in which case we might fallback or deny.
        # Decision: If the 'permissions' field is populated (even with empty dict), we respect it strictly.
        # This allows Admin to revoke ALL access by setting empty dict.
        # But if it is None/Null, we use Defaults.
        
        # However, UserProfile.permissions default is dict/empty. 
        # So we treat "empty dict" as "No access" if we want Strict. 
        # OR we treat "all missing" as "Use Default". 
        
        # STRATEGY: 
        # When creating a user, we copy ROLE_DEFAULTS into user.profile.permissions.
        # So at runtime, we primarily look at user.profile.permissions.
        # This makes the "EDIT" logic strictly consistent.
        
        user_actions = user_perms.get(module, [])
        if action in user_actions:
            return True
        
        # "Wildcard" access check (if we implement 'manage' = all actions)
        if 'manage' in user_actions:
            return True

        return False

    @staticmethod
    def merge_permissions(base_role, custom_overrides):
        """
        Helper to merge defaults with overrides during user creation
        """
        defaults = PermissionService.get_role_template(base_role).copy()
        
        # Custom overrides format: {'module': ['action1', 'action2']}
        # We can simply replace the list or merge. Replacing is safer/clearer.
        for module, actions in custom_overrides.items():
            defaults[module] = actions
            
        return defaults
