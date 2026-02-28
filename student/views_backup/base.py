from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from django.utils import timezone

# COMMON HELPERS (SAAS ISOLATION)

def get_owner_user(user):
    """
    Get the owner user for data filtering (multi-tenancy isolation)
    Returns the user who 'owns' the data being accessed
    """
    # Super admin: return special marker to filter their own data separately
    if user.is_superuser:
        return user  # Super admin sees only their own created data
    
    # CLIENT or ADMIN role: they are the owner of their data
    if hasattr(user, 'profile') and user.profile.role in ['CLIENT', 'ADMIN']:
        return user
    
    # Teacher/Staff: find their client/owner
    if hasattr(user, 'employee_profile'):
        return user.employee_profile.created_by
    
    # Parent/Student: should see data from their associated client
    if hasattr(user, 'profile') and user.profile.role in ['PARENT', 'STUDENT']:
        return getattr(user.profile, 'created_by', user)
    
    return user


def filter_by_owner(qs, user, created_by_field='created_by'):
    """
    Filter queryset to show only data owned by the current user
    CRITICAL: Ensures complete data isolation between clients and super admin
    """
    if user.is_superuser:
        return qs # God Mode: Super Admin sees EVERYTHING
    
    owner = get_owner_user(user)
    if owner:
        # Filter by created_by to show only this owner's data
        lookup = {created_by_field: owner}
        return qs.filter(**lookup)
    
    # Fallback: return empty queryset for safety
    return qs.none()
