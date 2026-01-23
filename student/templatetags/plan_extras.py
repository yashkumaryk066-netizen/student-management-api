from django import template
from student.plan_permissions import has_feature_access

register = template.Library()

@register.filter(name='has_feature')
def has_feature(user, feature_name):
    """
    Template filter to check if user has access to a feature.
    Usage: {% if user|has_feature:'students' %} ... {% endif %}
    """
    return has_feature_access(user, feature_name)

@register.filter(name='is_plan_expired')
def is_plan_expired(user):
    """Check if user plan is expired"""
    if hasattr(user, 'profile'):
        return user.profile.is_plan_expired()
    return False
