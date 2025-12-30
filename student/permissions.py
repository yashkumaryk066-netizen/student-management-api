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
    """Allow only users with ADMIN role"""
    def has_permission(self, request, view):
        return hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'

class IsTeacherOrAdmin(permissions.BasePermission):
    """Allow users with TEACHER or ADMIN role"""
    def has_permission(self, request, view):
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role in ['TEACHER', 'ADMIN']
