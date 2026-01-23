from rest_framework import permissions
from django.utils import timezone
from student.models import Student


# =========================
# BASIC ROLE PERMISSIONS
# =========================

class IsStudent(permissions.BasePermission):
    """Allow only users with STUDENT role"""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'STUDENT'
        )


class IsTeacher(permissions.BasePermission):
    """Allow only users with TEACHER role"""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'TEACHER'
        )


class IsParent(permissions.BasePermission):
    """Allow only users with PARENT role"""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'PARENT'
        )

class IsHR(permissions.BasePermission):
    """Allow only users with HR role"""
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and
            hasattr(request.user, 'profile') and
            request.user.profile.role == 'HR'
        )


class IsAdminRole(permissions.BasePermission):
    """
    STRICT system admin (Django superuser only).
    Clients are NOT admins here.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


# =========================
# CLIENT / SUBSCRIPTION
# =========================

class IsClient(permissions.BasePermission):
    """
    Subscription Client Permission
    - Active plan: Full access
    - Expired plan: Read-only
    - Suspended/Blocked: No access
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'profile'):
            return False

        profile = request.user.profile
        if profile.role != 'CLIENT':
            return False

        # Hard block first
        if hasattr(request.user, 'subscription'):
            if request.user.subscription.status in ['SUSPENDED', 'BLOCKED']:
                return False

        # Expiry check
        expiry = profile.subscription_expiry
        is_active = not expiry or expiry >= timezone.now().date()

        if is_active:
            return True

        # Expired → read-only
        return request.method in permissions.SAFE_METHODS


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Allow TEACHER or CLIENT (Org Owner).
    CLIENT access is subscription-aware.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if not hasattr(request.user, 'profile'):
            return False

        role = request.user.profile.role

        if role in ['TEACHER', 'ADMIN']:
            return True

        if role == 'CLIENT':
            expiry = request.user.profile.subscription_expiry
            if expiry and expiry < timezone.now().date():
                return request.method in permissions.SAFE_METHODS
            return True

        return False


# =========================
# PLAN-BASED FEATURE ACCESS
# =========================

class HasPlanAccess(permissions.BasePermission):
    """
    View must define: required_feature = 'students' | 'hostel' | ...
    """

    PLAN_FEATURES = {
        'SCHOOL': [
            'dashboard', 'students', 'exams', 'attendance',
            'transport', 'hostel', 'parents', 'teachers',
            'reports', 'payments', 'events', 'settings', 'subscription', 'hr'
        ],
        'COACHING': [
            'dashboard', 'students', 'courses', 'live_classes',
            'attendance', 'reports', 'payments', 'events', 'settings', 'subscription'
        ],
        'INSTITUTE': [
            'dashboard', 'students', 'exams', 'courses',
            'attendance', 'transport', 'hostel',
            'parents', 'teachers', 'reports', 'payments',
            'lab', 'library', 'hr', 'events', 'settings', 'subscription', 'logs', 'users', 'live_classes'
        ],
    }

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request.user, 'profile'):
            return False

        plan = (request.user.profile.institution_type or '').upper()
        required_feature = getattr(view, 'required_feature', None)

        if not required_feature:
            return True

        allowed = self.PLAN_FEATURES.get(plan, [])
        if required_feature not in allowed:
            self.message = f"{required_feature} not available in {plan} plan."
            return False

        return True


# =========================
# PLAN LIMITS
# =========================

class StudentLimitPermission(permissions.BasePermission):
    """
    COACHING: max 200 students
    SCHOOL / INSTITUTE: unlimited
    """
    STUDENT_LIMITS = {'COACHING': 200, 'SCHOOL': None, 'INSTITUTE': None}

    def has_permission(self, request, view):
        if request.method != 'POST' or request.user.is_superuser:
            return True

        if not hasattr(request.user, 'profile'):
            return False

        plan = (request.user.profile.institution_type or '').upper()
        limit = self.STUDENT_LIMITS.get(plan)

        if limit is None:
            return True

        current = Student.objects.filter(created_by=request.user).count()
        if current >= limit:
            self.message = f"Limit reached: {limit} students for {plan} plan."
            return False

        return True


# =========================
# STRICT PLAN GATES
# =========================

class IsSuperAdminExclusive(permissions.BasePermission):
    """Only Django superusers"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsSchool(permissions.BasePermission):
    """Allow SCHOOL + INSTITUTE"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.profile.institution_type in ['SCHOOL', 'INSTITUTE']
        except:
            return False


class IsCoaching(permissions.BasePermission):
    """Allow COACHING + INSTITUTE"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.profile.institution_type in ['COACHING', 'INSTITUTE']
        except:
            return False


class IsInstitute(permissions.BasePermission):
    """Allow ONLY INSTITUTE"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.profile.institution_type == 'INSTITUTE'
        except:
            return False
