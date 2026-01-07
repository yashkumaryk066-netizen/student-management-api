from django.http import JsonResponse
from django.utils import timezone


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
            '/analytics/',
        ),
        'SCHOOL': (
            '/hostel/',
            '/payroll/',
            '/analytics/',
        ),
        'INSTITUTE': (),  # Full access
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # --------------------------------------------------
        # 1. FAST EXIT – unauthenticated / superuser
        # --------------------------------------------------
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated or user.is_superuser:
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

            # Read-only allowed, skip plan restrictions
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

        # --------------------------------------------------
        # 4. ALLOW REQUEST
        # --------------------------------------------------
        return self.get_response(request)
