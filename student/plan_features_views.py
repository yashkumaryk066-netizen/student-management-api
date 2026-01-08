from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .permissions import HasPlanAccess, StudentLimitPermission
from .plan_permissions import PLAN_FEATURES  # Import centralized plan features
from .models import Student


class UserPlanFeaturesView(APIView):
    """
    Returns list of features available to authenticated user based on their plan
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # SUPER ADMIN
        if user.is_superuser:
            return Response({
                "plan_type": "SUPER_ADMIN",
                "features": list(PLAN_FEATURES['INSTITUTE']), # Super admin gets all features
                "student_limit": None,
                "current_students": 0,
                "can_add_students": True,
                "feature_descriptions": self.get_feature_descriptions()
            })

        # NORMAL USER
        profile = getattr(user, "profile", None)
        if not profile or not profile.institution_type:
            return Response(
                {"error": "No active subscription found"},
                status=400
            )

        plan_type = profile.institution_type
        # Use centralized PLAN_FEATURES
        features = list(PLAN_FEATURES.get(plan_type, []))
        student_limit = StudentLimitPermission.STUDENT_LIMITS.get(plan_type)

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
            "dashboard": "Main Dashboard",
            "students": "Student Management",
            "exams": "Exams & Grading",
            "courses": "Courses & Batches",
            "attendance": "Attendance System",
            "transport": "Transport Management",
            "hostel": "Hostel Management",
            "parents": "Parent Portal",
            "teachers": "Teacher Management",
            "reports": "Reports & Analytics",
            "payments": "Payment & Fees",
            "lab": "Lab Management",
            "library": "Library Management",
            "hr": "HR & Payroll",
            "events": "Events & Calendar",
            "settings": "Settings",
            "subscription": "Plan & Subscription",
            "users": "Team & Permissions",
            "logs": "System Logs",
            "live_classes": "Live Virtual Classes"
        }
