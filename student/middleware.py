import json
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.urls import resolve

class SubscriptionMiddleware:
    """
    Middleware to enforce:
    1. Subscription Expiry (Blocks Write/Unsafe methods for expired clients)
    2. Plan-based Feature Access (Gating URLs based on Plan Type)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Skip checks for Superuser or Unauthenticated users (Permission classes handle auth)
        if not request.user.is_authenticated or request.user.is_superuser:
            return self.get_response(request)

        # 2. Skip checks for Safe Methods (GET, HEAD, OPTIONS) - Allow Read-Only even if expired
        # UNLESS it's a specific premium feature that requires active sub even for reading
        # For now, we follow the "Read Only on Expiry" rule.
        is_safe_method = request.method in ['GET', 'HEAD', 'OPTIONS']
        
        # 3. Check Subscription Expiry for CLIENTS
        if hasattr(request.user, 'profile') and request.user.profile.role == 'CLIENT':
            expiry_date = request.user.profile.subscription_expiry
            
            # If expired and trying to perform unsafe action (POST, PUT, DELETE)
            if expiry_date and expiry_date < timezone.now().date():
                if not is_safe_method:
                    return JsonResponse({
                        "error": "Subscription Expired",
                        "code": "SUBSCRIPTION_EXPIRED",
                        "message": "Your subscription has expired. Please renew to perform this action.",
                        "action": "RENEW_PLAN"
                    }, status=403)

        # 4. Feature Gating (Plan specific)
        # This can be complex to map URL -> Feature.
        # Simple approach: Check URL namespace or path prefixes
        
        # Example: '/api/transport/' requires SCHOOL or INSTITUTE
        path = request.path
        plan_type = getattr(request.user.profile, 'institution_type', 'SCHOOL') # Default to lowest or safely handle
        
        # Define forbidden paths for specific plans
        # COACHING cannot access Transport, Hostel
        if plan_type == 'COACHING':
            if '/transport/' in path or '/hostel/' in path:
                return JsonResponse({
                    "error": "Feature Not Available",
                    "code": "PLAN_RESTRICTED",
                    "message": "This feature is not available in your Coaching Plan.",
                    "upgrade_required": True
                }, status=403)

        response = self.get_response(request)
        return response
