from django.conf import settings

# ==============================================================================
# 🔐 CENTRAL PERMISSION MATRIX (PREMIUM ARCHITECTURE)
# ==============================================================================
# This module implements a "Layered Access Control" system.
# Access = (Institution Type Features + Subscription Tier Features) + Ad-hoc Overrides
# This allows for granular control like "Basic School" vs "Enterprise School".

# 1. FEATURE GROUPS (Modular & Reusable)
CORE_FEATURES = {
    'dashboard', 'students', 'attendance', 'finance', 'calendar', 'profile', 'settings', 'logs'
}

ACADEMIC_FEATURES = {
    'library', 'exams', 'timetable', 'leaves', 'departments', 'routine', 'substitutes', 'assignments'
}

COACHING_FEATURES = {
    'courses', 'live_classes', 'marketing', 'leads', 'batches', 'enrollments', 'lms_materials'
}

OPERATIONS_FEATURES = {
    'hostel', 'transport', 'inventory', 'hr', 'payroll', 'roi_analytics'
}

ADVANCED_FEATURES = {
    'audit_logs', 'global_settings', 'multi_branch', 'api_access', 'white_label', 'ai_insights'
}

# 2. INSTITUTION TYPE BASELINES (The "Domain" Layer)
# Defines what modules are relevant for a specific business type.
INSTITUTION_FEATURES = {
    'SCHOOL': list(CORE_FEATURES | ACADEMIC_FEATURES | {'hr', 'payroll', 'transport'}), # Added transport/hr as standard for schools
    'COACHING': list(CORE_FEATURES | COACHING_FEATURES),
    'INSTITUTE': list(CORE_FEATURES | ACADEMIC_FEATURES | COACHING_FEATURES | OPERATIONS_FEATURES | {'approvals'}),
    
    # Special Types
    'EDUCATION SYSTEM': list(
        CORE_FEATURES | ACADEMIC_FEATURES | COACHING_FEATURES | OPERATIONS_FEATURES | ADVANCED_FEATURES | {'approvals', 'admin_approvals'}
    ),
    'SUPER_ADMIN': list(
        CORE_FEATURES | ACADEMIC_FEATURES | COACHING_FEATURES | OPERATIONS_FEATURES | ADVANCED_FEATURES | {'approvals', 'admin_approvals'}
    )
}

# 3. SUBSCRIPTION TIERS (The "Depth" Layer)
# Defines additional capabilities based on payment tiers.
# Note: These are ADDITIVE to the Institution Features.
TIER_FEATURES = {
    'BASIC': set(), # Standard Access
    'PRO': {'reports', 'events', 'notifications', 'bulk_import'},
    'ENTERPRISE': {'reports', 'events', 'notifications', 'bulk_import'} | OPERATIONS_FEATURES | ADVANCED_FEATURES
}

# 4. METADATA (For UI Rendering)
FEATURE_META = {
    'library': {'name': 'Library', 'icon': '📚'},
    'transport': {'name': 'Transport', 'icon': '🚌'},
    'hostel': {'name': 'Hostel', 'icon': '🏢'},
    'hr': {'name': 'HR & Payroll', 'icon': '👔'},
    'exams': {'name': 'Exams', 'icon': '📝'},
    'courses': {'name': 'Courses', 'icon': '🎓'},
    'live_classes': {'name': 'Live Classes', 'icon': '🔴'},
    'dashboard': {'name': 'Dashboard', 'icon': '📊'},
    'students': {'name': 'Student Management', 'icon': '🎓'},
    'finance': {'name': 'Finance & Fees', 'icon': '💰'},
    'attendance': {'name': 'Attendance', 'icon': '📅'},
    'settings': {'name': 'Settings', 'icon': '⚙️'},
    'reports': {'name': 'Advanced Reports', 'icon': '📈'},
    'ai_insights': {'name': 'AI Analytics', 'icon': '🤖'},
}

# Backward Compatibility Alias
PLAN_FEATURES = INSTITUTION_FEATURES 

def get_feature_meta(feature_key):
    return FEATURE_META.get(feature_key, {'name': feature_key.replace('_', ' ').title(), 'icon': '🔹'})

def get_effective_permissions(user):
    """
    Computes the final set of permissions for a user based on their context.
    Returns: Set[str] of feature keys.
    """
    if user.is_superuser:
        return set(INSTITUTION_FEATURES['SUPER_ADMIN'])
        
    if not hasattr(user, 'profile'):
        return set(INSTITUTION_FEATURES.get('SCHOOL', []))

    profile = user.profile
    
    # A. Base Context Permissions (Institution)
    inst_type = profile.institution_type or 'SCHOOL'
    base_features = set(INSTITUTION_FEATURES.get(inst_type, INSTITUTION_FEATURES['SCHOOL']))
    
    # B. Tier Permissions (Subscription)
    # Default to 'BASIC' if not specified
    plan_tier = profile.subscription_plan or 'BASIC' 
    tier_features = TIER_FEATURES.get(plan_tier, set())
    
    # Combine (Union)
    # Logic: You only get features that are relevant to your Institution AND allowed by your Tier?
    # OR strictly additive? 
    # Current Decision: Additive, but filter by relevance if needed. 
    # For simplicity/premium feel: Additive. An Enterprise Coaching center might want HR even if not standard.
    effective_features = base_features | tier_features
    
    # C. Custom User/Role Overrides (Granular Control)
    if profile.permissions:
        # 'features' key in JSON field serves as an explicit Override/Allowlist
        # If present, it takes precedence IF strict mode is desired.
        # But for 'Add-on' logic, we just merge.
        custom_allowed = set(profile.permissions.get('allow_features', []))
        custom_denied = set(profile.permissions.get('deny_features', []))
        
        effective_features = (effective_features | custom_allowed) - custom_denied

    return effective_features

def has_feature_access(user, feature_name):
    """
    The Premium Gatekeeper.
    Checks access against the computed matrix.
    """
    # 1. Super Admin Bypass
    if user.is_superuser:
        return True

    # 2. Expiry Check (Hard Stop)
    if hasattr(user, 'profile') and user.profile.is_plan_expired():
        # Minimal Access Mode
        SAFE_FEATURES = {'dashboard', 'payment_renewal', 'profile', 'settings'}
        if feature_name not in SAFE_FEATURES:
            return False

    # 3. Check Computed Permissions
    allowed_features = get_effective_permissions(user)
    
    return feature_name in allowed_features

def get_user_plan(user):
    """
    Legacy Helper: Returns the primary identifier for the User's "Plan".
    Now returns the Institution Type as the primary context.
    """
    if user.is_superuser: return 'SUPER_ADMIN'
    if hasattr(user, 'profile'):
        return user.profile.institution_type or 'SCHOOL'
    return 'SCHOOL'

def get_user_features(user):
    """
    Returns API-ready list of features with metadata.
    """
    features_set = get_effective_permissions(user)
    
    features_dict = {}
    for feature in features_set:
        meta = get_feature_meta(feature)
        features_dict[feature] = meta
        
    return features_dict

# Pricing Configuration (Centralized)
# SYNC: These must match frontend index.html pricing cards exactly
PLAN_PRICING = {
    'COACHING': 500,
    'SCHOOL': 2000,
    'INSTITUTE': 5000,
    'EDUCATION SYSTEM': 99999, # Enterprise/Internal
    'SUPER_ADMIN': 0
}

# Per-plan student/staff limits
PLAN_STUDENT_LIMITS = {
    'COACHING': 200,   # Up to 200 students
    'SCHOOL': 1000,    # Up to 1000 students
    'INSTITUTE': 9999, # Unlimited (9999 = no cap)
    'EDUCATION SYSTEM': 99999,
    'SUPER_ADMIN': 99999,
}

# Per-plan features label (used in emails/UI)
PLAN_LABELS = {
    'COACHING': 'Coaching Center Plan - ₹500/month',
    'SCHOOL': 'School Management Plan - ₹2,000/month',
    'INSTITUTE': 'Institute / University Plan - ₹5,000/month',
    'EDUCATION SYSTEM': 'Enterprise Education System',
    'SUPER_ADMIN': 'Super Admin Access',
}

# Maps institution type -> default subscription tier (used in ClientSubscription.activate())
DEFAULT_PLAN_BY_INSTITUTION = {
    'COACHING': 'BASIC',
    'SCHOOL': 'PRO',
    'INSTITUTE': 'ENTERPRISE',
    'EDUCATION SYSTEM': 'ENTERPRISE',
}

def get_upgrade_options(user):
    """
    Returns list of available upgrade plans based on pricing.
    """
    current_plan = get_user_plan(user)
    current_price = PLAN_PRICING.get(current_plan, 0)
    
    # If using a custom high-tier plan not in pricing, assume max tier
    if current_plan not in PLAN_PRICING:
        current_price = 99999

    options = []
    for plan_name, price in PLAN_PRICING.items():
        # Only show upgrade if price is higher and it's a public plan
        if price > current_price and price < 90000:
            options.append({
                "plan": plan_name,
                "price": price,
                "difference": price - current_price,
                "label": f"{plan_name.title().replace('_', ' ')} (₹{price}/mo)"
            })
            
    return sorted(options, key=lambda x: x['price'])
