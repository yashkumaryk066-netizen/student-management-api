from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .permissions import IsPlanFeatureEnabled, StudentLimitPermission
from .plan_permissions import PLAN_FEATURES, FEATURE_META, get_user_plan
from .models import Student

class UserPlanFeaturesView(APIView):
    """
    Returns list of features available to authenticated user based on their plan
    """
    permission_classes = [permissions.IsAuthenticated]

    # Temporarily hardcode limits or move to plan_permissions
    STUDENT_LIMITS = {
        'SCHOOL': 5000,
        'COACHING': 1000,
        'INSTITUTE': 10000
    }

    def get(self, request):
        user = request.user

        # SUPER ADMIN
        if user.is_superuser:
            return Response({
                "plan_type": "SUPER_ADMIN",
                "features": PLAN_FEATURES['INSTITUTE'], # Super admin gets all features
                "student_limit": None,
                "current_students": 0,
                "can_add_students": True,
                "feature_descriptions": self.get_feature_descriptions()
            })

        # NORMAL USER
        # Use centralized logic from plan_permissions
        plan_type = get_user_plan(user)
        features = PLAN_FEATURES.get(plan_type, [])
        
        student_limit = self.STUDENT_LIMITS.get(plan_type)
        current_students = Student.objects.filter(created_by=user).count()

        return Response({
            "plan_type": plan_type,
            "features": features,
            "student_limit": student_limit,
            "current_students": current_students,
            "can_add_students": (
                student_limit is None or current_students < student_limit
            ),
            "feature_descriptions": self.get_feature_descriptions()
        })

    def get_feature_descriptions(self):
        return {
            key: meta['name'] 
            for key, meta in FEATURE_META.items()
        }
