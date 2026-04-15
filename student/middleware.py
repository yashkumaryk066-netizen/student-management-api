from django.http import JsonResponse
from django.utils import timezone


class DisableCacheMiddleware:
    """
    Disable caching for all responses to ensure fresh data.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"
        return response


class SubscriptionMiddleware:
    """
    Enterprise Subscription Middleware

    Enforces:
    1. Subscription expiry rules (Write blocked on expiry)
    2. Plan-based feature access (URL gating)
    3. Read-only fallback for expired subscriptions
    """

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
    
    # Exempt URLs from expiry block (so they can renew)
    EXEMPT_URLS = (
        '/payment/',
        '/subscription/',
        '/auth/',
        '/api/payment/',
        '/api/subscription/',
        '/api/auth/',
    )

    # Plan → Restricted URL keywords
    PLAN_RESTRICTIONS = {
        'COACHING': (
            '/transport/',
            '/hostel/',
            '/payroll/',
            '/library/',
            # '/analytics/', # REMOVED: ROI Analytics needed for Owners
        ),
        'SCHOOL': (
            '/hostel/',
            '/payroll/',
            # '/analytics/', # REMOVED: ROI Analytics needed for Owners
        ),
        'INSTITUTE': (),  # Full access
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        # --------------------------------------------------
        # 1. FAST EXIT – unauthenticated / superuser
        # --------------------------------------------------
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            return self.get_response(request)

        # CRITICAL: Superuser bypass - MUST be checked AFTER authentication
        # Superadmins have UNRESTRICTED access to ALL features
        if user.is_superuser:
            return self.get_response(request)

        profile = getattr(user, 'profile', None)
        if not profile:
            return self.get_response(request)

        # Normalize
        plan_type = (getattr(profile, 'institution_type', '') or '').upper()
        path = request.path.lower()

        # --------------------------------------------------
        # 2. SUBSCRIPTION EXPIRY CHECK
        # --------------------------------------------------
        expiry_date = getattr(profile, 'subscription_expiry', None)
        is_safe_method = request.method in self.SAFE_METHODS
        is_exempt_url = any(url in path for url in self.EXEMPT_URLS)

        if expiry_date and expiry_date < timezone.now().date():
            # Expired → write blocked (Read-Only)
            if not is_safe_method and not is_exempt_url:
                return JsonResponse({
                    "code": "SUBSCRIPTION_EXPIRED",
                    "message": "Your subscription has expired. Read-Only access only.",
                    "action": "RENEW_PLAN"
                }, status=403)

            # Read-only allowed, skip plan restrictions (allow them to see what they had)
            if not is_exempt_url:
                 # Should we enforce plan restrictions? user says "sirf read kr sake apne data ko"
                 # It's better to allow full Read Only access to THEIR data.
                 # But plan restrictions prevent accessing features they didn't pay for.
                 # If they are expired, they technically have NO plan. 
                 # But preserving "their data" implies sticking to their old plan scope?
                 # Actually, usually Expired = Read Only view of existing data.
                 # If they had "Transport" in School plan, they should see it.
                 # If they didn't, they shouldn't.
                 # So we SHOULD continue to enforce plan restrictions?
                 # Or just skip it because they can't Add anyway.
                 # Middleware currently skips restrictions if expired. I'll leave it as is (Permissive Read Only).
                 pass
            
            return self.get_response(request)

        # --------------------------------------------------
        # 3. PLAN-BASED FEATURE GATING (ACTIVE SUBS ONLY)
        # --------------------------------------------------
        restricted_paths = self.PLAN_RESTRICTIONS.get(plan_type, ())

        for keyword in restricted_paths:
            if keyword in path:
                return JsonResponse({
                    "success": False,
                    "error": {
                        "code": "PLAN_RESTRICTED",
                        "message": f"This feature is not available in your {plan_type} plan.",
                        "upgrade_required": True
                    }
                }, status=403)

        return self.get_response(request)


# =============================================================================
# SECURITY MIDDLEWARE (Added for Security Audit Fixes)
# =============================================================================

import logging
from django.utils.deprecation import MiddlewareMixin
from student.models import AuditLog

logger = logging.getLogger('security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds comprehensive security headers to all responses
    Implements OWASP recommended security headers
    """
    
    def process_response(self, request, response):
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Prevent clickjacking (Allow same-origin and Razorpay frames)
        response['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (UI-safe with external CDNs)
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com https://*.razorpay.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
            "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' https://api.openai.com https://generativelanguage.googleapis.com https://api.anthropic.com https://api.groq.com https://api.deepseek.com https://api.mistral.ai wss: ws: https://unpkg.com https://cdn.jsdelivr.net https://*.razorpay.com; "
            "frame-src 'self' https://*.razorpay.com; "
            "object-src 'none';"
        )
        
        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = (
            "geolocation=(self), "
            "microphone=(), "
            "camera=()"
        )
        
        return response


class RequestValidationMiddleware(MiddlewareMixin):
    """
    Validates incoming requests for suspicious patterns
    Blocks requests with excessively large payloads or suspicious headers
    """
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    def process_request(self, request):
        # Check request size
        if request.META.get('CONTENT_LENGTH'):
            try:
                content_length = int(request.META['CONTENT_LENGTH'])
                if content_length > self.MAX_REQUEST_SIZE:
                    logger.warning(
                        f"⚠️ Request too large: {content_length} bytes from {request.META.get('REMOTE_ADDR')}"
                    )
                    return JsonResponse({
                        'error': 'Request payload too large'
                    }, status=413)
            except (ValueError, TypeError):
                pass
        
        # Check for suspicious user agents (basic bot detection)
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        suspicious_patterns = ['sqlmap', 'nikto', 'nmap', 'masscan', 'nessus']
        
        if any(pattern in user_agent for pattern in suspicious_patterns):
            logger.warning(
                f"⚠️ Suspicious user agent detected: {user_agent} from {request.META.get('REMOTE_ADDR')}"
            )
            return JsonResponse({
                'error': 'Access denied'
            }, status=403)
        
        return None


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Logs security-sensitive operations for audit trail
    """
    
    SENSITIVE_PATHS = [
        '/api/login',
        '/api/password-reset',
        '/api/admin',
        '/api/payments',
        '/api/super-admin'
    ]
    
    def process_response(self, request, response):
        # Log sensitive operations
        if any(request.path.startswith(path) for path in self.SENSITIVE_PATHS):
            # Only log if user is authenticated or if it's a failed auth attempt
            if hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    AuditLog.objects.create(
                        created_by=request.user,
                        action=f"{request.method} {request.path}",
                        description=f"Status: {response.status_code}",
                        ip_address=self.get_client_ip(request)
                    )
                except Exception as e:
                    logger.error(f"Failed to create audit log: {e}")
            elif response.status_code in [401, 403]:
                # Log failed authentication attempts
                logger.warning(
                    f"⚠️ Failed auth attempt: {request.method} {request.path} "
                    f"from {self.get_client_ip(request)} - Status: {response.status_code}"
                )
        
        return response
    
    def get_client_ip(self, request):
        """Extract client IP from request, handling proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip

