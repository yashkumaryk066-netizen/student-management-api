"""
Custom Throttling Classes for Rate Limiting
SECURITY FIX #14: Implement rate limiting correctly using settings.py
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Strict rate limiting for login attempts
    Prevents brute force attacks
    """
    scope = 'login'


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Rate limiting for password reset requests
    Prevents enumeration attacks
    """
    scope = 'password_reset'


class PaymentRateThrottle(UserRateThrottle):
    """
    Rate limiting for payment submissions
    Prevents DOS attacks on payment endpoints
    """
    scope = 'payment_submit'


class StrictUserRateThrottle(UserRateThrottle):
    """
    Stricter rate limiting for authenticated users
    """
    scope = 'user'


class BurstRateThrottle(UserRateThrottle):
    """
    Short-term burst protection
    """
    scope = 'burst'


class AttendanceRateThrottle(UserRateThrottle):
    """
    Rate limiting for attendance marking
    Prevents duplicate submissions and spoofing attempts
    """
    scope = 'attendance'
