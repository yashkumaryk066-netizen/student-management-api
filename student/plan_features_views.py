from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .permissions import HasPlanAccess

class UserPlanFeaturesView(APIView):
    """
    Returns list of features available to authenticated user based on their plan
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_superuser:
            # Super admin gets all features
            features = HasPlanAccess.PLAN_FEATURES['INSTITUTE']
            plan_type = 'SUPER_ADMIN'
            student_limit = None
        else:
            try:
                plan_type = user.profile.institution_type
                features = HasPlanAccess.PLAN_FEATURES.get(plan_type, [])
                
                # Get student limit
                from .permissions import StudentLimitPermission
                student_limit = StudentLimitPermission.STUDENT_LIMITS.get(plan_type)
                
                # Count current students
                from .models import Student
                current_students = Student.objects.filter(created_by=user).count()
                
            except:
                return Response({
                    "error": "No active subscription found"
                }, status=400)
        
        # Get current student count
        from .models import Student
        current_students = Student.objects.filter(created_by=user).count() if not user.is_superuser else 0
        
        return Response({
            "plan_type": plan_type,
            "features": features,
            "student_limit": student_limit,
            "current_students": current_students,
            "can_add_students": student_limit is None or current_students < student_limit,
            "feature_descriptions": {
                "students": "Student Management",
                "school_exams": "School Examinations",
                "coaching_classes": "Coaching Classes",
                "test_series": "Test Series & Mock Tests",
                "attendance": "Advanced Attendance System",
                "basic_attendance": "Basic Attendance",
                "transport": "Transport Management",
                "hostel": "Hostel Management",
                "parents": "Parent Portal",
                "teachers": "Teacher Management",
                "reports": "Reports & Analytics",
                "payments": "Payment Tracking",
                "study_material": "Study Material",
                "lab": "Lab Management",
                "library": "Library Management"
            }
        })
