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

        if expiry_date and expiry_date < timezone.now().date():
            # Expired → write blocked
            if not is_safe_method:
                return JsonResponse({
                    "success": False,
                    "error": {
                        "code": "SUBSCRIPTION_EXPIRED",
                        "message": "Your subscription has expired.",
                        "action": "RENEW_PLAN"
                    }
                }, status=403)

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
