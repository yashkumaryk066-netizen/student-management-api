"""
Plan-Based Feature Access Control
Centralized permission system for different subscription tiers
"""

# Feature definitions for each plan
PLAN_FEATURES = {
    'COACHING': {
        'students', 'attendance', 'live_classes', 'notifications', 'reports'
    },
    'SCHOOL': {
        'students', 'attendance', 'live_classes', 'notifications', 'reports',
        'exams', 'finance', 'classes', 'parents'
    },
    'INSTITUTE': {
        'students', 'attendance', 'live_classes', 'notifications', 'reports',
        'exams', 'finance', 'classes', 'parents',
        'departments', 'hostel', 'lab', 'transport', 'hr'
    }
}

# Feature display names and icons
FEATURE_META = {
    'students': {'name': 'Student Management', 'icon': '👨‍🎓'},
    'attendance': {'name': 'Attendance', 'icon': '✅'},
    'live_classes': {'name': 'Live Classes', 'icon': '📹'},
    'notifications': {'name': 'Notifications', 'icon': '🔔'},
    'reports': {'name': 'Reports & Analytics', 'icon': '📊'},
    'exams': {'name': 'Exam Management', 'icon': '📝'},
    'finance': {'name': 'Finance & Fees', 'icon': '💰'},
    'classes': {'name': 'Class Management', 'icon': '🏫'},
    'parents': {'name': 'Parent Portal', 'icon': '👪'},
    'departments': {'name': 'Departments', 'icon': '🏛️'},
    'hostel': {'name': 'Hostel Management', 'icon': '🏨'},
    'lab': {'name': 'Lab Management', 'icon': '🔬'},
    'transport': {'name': 'Transport', 'icon': '🚌'},
    'hr': {'name': 'HR Management', 'icon': '👔'}
}

def has_feature_access(user, feature_name):
    """
    Check if user has access to a specific feature based on their plan
    
    Args:
        user: Django User object with profile
        feature_name: String name of the feature (e.g., 'exams', 'finance')
    
    Returns:
        bool: True if user has access, False otherwise
    """
    if not hasattr(user, 'profile'):
        return False
    
    # Super admins have access to everything
    if user.is_superuser:
        return True
    
    # Get user's plan type
    plan_type = getattr(user.profile, 'institution_type', 'COACHING')
    
    # Get allowed features for this plan
    allowed_features = PLAN_FEATURES.get(plan_type, PLAN_FEATURES['COACHING'])
    
    return feature_name in allowed_features


def get_user_features(user):
    """
    Get list of all features available to a user based on their plan
    
    Args:
        user: Django User object with profile
    
    Returns:
        dict: Dictionary with feature names as keys and metadata as values
    """
    if user.is_superuser:
        # Super admin gets everything
        all_features = PLAN_FEATURES['INSTITUTE']
        return {f: FEATURE_META[f] for f in all_features}
    
    if not hasattr(user, 'profile'):
        return {}
    
    plan_type = getattr(user.profile, 'institution_type', 'COACHING')
    allowed_features = PLAN_FEATURES.get(plan_type, PLAN_FEATURES['COACHING'])
    
    return {f: FEATURE_META[f] for f in allowed_features}


def get_upgrade_plans_for_feature(current_plan, feature_name):
    """
    Get list of plans that include a specific feature
    
    Args:
        current_plan: Current user's plan type
        feature_name: Feature they want to access
    
    Returns:
        list: List of plan names that include this feature
    """
    available_in = []
    
    for plan, features in PLAN_FEATURES.items():
        if feature_name in features and plan != current_plan:
            available_in.append(plan)
    
    return available_in
