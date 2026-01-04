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
        # TODO: Implement strict check if the Institute's plan is expired?
        # For now, simplistic role check.
        # In a real world scenario, we'd link Parent -> Student -> Institute -> Expiry.
        # Assuming current scope, we focus on Client access restrictions.
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
    Custom permission for Subscription Clients.
    - Active Plan: Full Access
    - Expired Plan: Read Only (GET, HEAD, OPTIONS)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if request.user.is_superuser:
            return True
            
        is_client = hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT'
        
        if is_client:
            # 1. Check for Hard Block/Suspension first
            if hasattr(request.user, 'subscription'):
                 if request.user.subscription.status in ['SUSPENDED', 'BLOCKED']:
                     return False # Full Block (Security)

            # 2. Check Subscription Validity (Expiry)
            from django.utils import timezone
            profile = request.user.profile
            is_active = not profile.subscription_expiry or profile.subscription_expiry >= timezone.now().date()
            
            if is_active:
                return True
            
            # If Expired (but not Blocked), Allow Safe Methods Only
            if request.method in permissions.SAFE_METHODS:
                return True
                
            return False # Block Write operations
            
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
                         # Expired: Allow Read Only
                         if request.method in permissions.SAFE_METHODS:
                             return True
                         return False # Block Write
                 return True
        
        return False

# ============================================
# PLAN-BASED ACCESS CONTROL
# ============================================

from .models import Student

class HasPlanAccess(permissions.BasePermission):
    """
    Check if user's plan allows access to specific features
    
    SCHOOL Plan: Student mgmt, school exams, transport, hostel (unlimited students)
    COACHING Plan: Student mgmt (200 max), coaching classes, test series (NO school features)
    INSTITUTE Plan: Full access (unlimited)
    """
    
    PLAN_FEATURES = {
        'SCHOOL': ['students', 'school_exams', 'attendance', 'transport', 'hostel', 'parents', 'teachers', 'reports', 'payments'],
        'COACHING': ['students', 'coaching_classes', 'test_series', 'study_material', 'basic_attendance', 'teachers', 'reports', 'payments'],
        'INSTITUTE': ['students', 'school_exams', 'coaching_classes', 'test_series', 'attendance', 'transport', 'hostel', 'parents', 'teachers', 'reports', 'payments', 'study_material', 'lab', 'library']
    }
    
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
        if not request.user.is_authenticated:
            return False
        
        try:
            plan_type = request.user.profile.institution_type
        except:
            return False
        
        required_feature = getattr(view, 'required_feature', None)
        
        if not required_feature:
            return True
        
        allowed_features = self.PLAN_FEATURES.get(plan_type, [])
        
        if required_feature not in allowed_features:
            self.message = f"This feature is not available in {plan_type} plan. Upgrade to access."
            return False
        
        return True


class StudentLimitPermission(permissions.BasePermission):
    """
    Enforce student limits: COACHING=200, SCHOOL/INSTITUTE=Unlimited
    """
    
    STUDENT_LIMITS = {'COACHING': 200, 'SCHOOL': None, 'INSTITUTE': None}
    
    def has_permission(self, request, view):
        if request.method != 'POST' or request.user.is_superuser:
            return True
        
        try:
            plan_type = request.user.profile.institution_type
        except:
            return False
        
        student_limit = self.STUDENT_LIMITS.get(plan_type)
        
        if student_limit is None:
            return True
        
        current_count = Student.objects.filter(created_by=request.user).count()
        
        if current_count >= student_limit:
            self.message = f"COACHING plan: Maximum {student_limit} students. You have {current_count}. Upgrade to SCHOOL/INSTITUTE for unlimited."
            return False
        
        return True
