import random
import logging
import string
from decimal import Decimal
from rest_framework import serializers

# --- DRF IMPORTS ---
from rest_framework.views import APIView as DRFAPIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authentication import SessionAuthentication

# --- DJANGO IMPORTS ---
from django.db import transaction, IntegrityError
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

# --- SECURITY & AUTH ---
from student.authentication import QueryParameterTokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

# --- UTILS ---
from core.optimizations import (
    cache_api_response, 
    invalidate_cache, 
    OptimizedQueryMixin, 
    track_performance
)
from student.utils import get_owner_user, filter_by_owner
from student.permissions import IsPlanFeatureEnabled, IsTeacherOrAdmin

# --- LOGGING ---
logger = logging.getLogger(__name__)


class SpectacularFallbackSerializer(serializers.Serializer):
    """Fallback serializer for APIViews that return dynamic payloads."""
    detail = serializers.CharField(required=False)


class APIView(DRFAPIView):
    """
    Base APIView with default serializer_class for schema generation.
    """
    serializer_class = SpectacularFallbackSerializer

# --- CONSTANTS ---
SUB_ACTIVE = 'ACTIVE'
PAYMENT_APPROVED = 'APPROVED'
PAYMENT_PENDING = 'PENDING_VERIFICATION'

PLAN_PRICING = {
    'COACHING': Decimal('500.00'),
    'SCHOOL': Decimal('2000.00'),
    'INSTITUTE': Decimal('5000.00'),
}

SUBSCRIPTION_DAYS = 30
