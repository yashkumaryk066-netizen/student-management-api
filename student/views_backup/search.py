from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from student.models import Student, Course, Batch
from student.conf import CURRENCY_SYMBOL
from .base import filter_by_owner

class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query or len(query) < 2:
            return Response([])

        user = request.user
        results = []

        # 1. Search Students
        students = Student.objects.select_related('parent').filter(
            Q(name__icontains=query) | 
            Q(roll_number__icontains=query) |
            Q(parent__username__icontains=query)
        )
        # Apply Isolation
        students = filter_by_owner(students, user)[:5]
        
        for s in students:
            results.append({
                'type': 'Student',
                'title': s.name,
                'subtitle': f"Roll: {s.roll_number} | Class: {s.grade}",
                'url': f"#students/{s.id}",
                'icon': '👤'
            })

        # 2. Search Courses/Batches (Coaching/Institute)
        if hasattr(user, 'profile') and user.profile.institution_type != 'SCHOOL':
            courses = Course.objects.filter(name__icontains=query)
            courses = filter_by_owner(courses, user)[:3]
            for c in courses:
                results.append({
                    'type': 'Course',
                    'title': c.name,
                    'subtitle': f"Fee: {CURRENCY_SYMBOL}{c.fee}",
                    'url': f"#courses/{c.id}",
                    'icon': '📚'
                })

        # 3. Search Batches
        batches = Batch.objects.select_related('course').filter(name__icontains=query)
        batches = filter_by_owner(batches, user)[:3]
        for b in batches:
             results.append({
                'type': 'Batch',
                'title': b.name,
                'subtitle': f"Course: {b.course.name if b.course else 'N/A'}",
                'url': f"#batches",
                'icon': '👥'
            })
        
        return Response(results)
