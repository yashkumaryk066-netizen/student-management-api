from django import template
from student.plan_permissions import PLAN_FEATURES, get_user_plan

register = template.Library()

@register.filter(name='has_feature')
def has_feature(user, feature_name):
    """
    Usage: {% if user|has_feature:'library' %} ... {% endif %}
    
    PREMIUM LOGIC:
    1. SUPERUSER / ROOT -> ALWAYS TRUE (God Mode)
    2. Client -> Checks their Plan Type against PLAN_FEATURES
    """
    
    # 1. GOD MODE (Super Admin Rule)
    if user.is_superuser:
        return True
        
    # 2. Get User's Plan
    plan_type = get_user_plan(user)
    
    # 3. Validation
    # If plan is not in our keys (e.g. 'BASIC'), default to minimal or block
    allowed_features = PLAN_FEATURES.get(plan_type, [])
    
    # 4. Check access
    # 'dashboard' and 'settings' are usually universal, but we check anyway
    if feature_name in ['dashboard', 'settings', 'profile']:
        return True
        
    return feature_name in allowed_features

@register.filter(name='plan_name')
def plan_name(user):
    if user.is_superuser:
        return "SUPER ADMIN (UNLIMITED)"
    return get_user_plan(user)
