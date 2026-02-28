from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from student.models import Holiday, ClassRoutine, Batch
from .base import filter_by_owner, get_owner_user

class HolidayListCreateView(generics.ListCreateAPIView):
    serializer_class = None # We'll build response manually for speed or add serializer later
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Strict Isolation
        holidays = Holiday.objects.filter(owner=user.profile.get_owner() if hasattr(user, 'profile') else user)
        # Also include owner's own holidays (if user is owner)
        holidays |= Holiday.objects.filter(owner=user)
        
        holidays = holidays.distinct().order_by('date')
        
        data = [{
            'id': h.id,
            'title': h.name,
            'start': h.date,
            'end': h.end_date, 
            'type': h.type,
            'description': h.description,
            'className': f"holiday-{h.type.lower()}" # CSS class for fullcalendar
        } for h in holidays]
        
        return Response(data)

    def post(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'CLIENT']:
             return Response({"error": "Permission Denied"}, status=403)
             
        data = request.data
        Holiday.objects.create(
            owner=request.user,
            name=data.get('name'),
            date=data.get('date'),
            type=data.get('type', 'ACADEMIC'),
            description=data.get('description')
        )
        return Response({"message": "Holiday Created"}, status=201)

class RoutineListCreateView(generics.ListCreateAPIView):
    serializer_class = None 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # Strict Isolation - Assuming profile structure
        owner = get_owner_user(user)
        routines = ClassRoutine.objects.filter(owner=owner)
        
        # Filter by specific context
        batch_id = request.query_params.get('batch_id')
        grade = request.query_params.get('grade')
        
        if batch_id:
            routines = routines.filter(batch_id=batch_id)
        if grade:
            routines = routines.filter(grade=grade)
            
        data = [{
            'id': r.id,
            'day': r.day_of_week,
            'subject': r.subject,
            'teacher': r.teacher_name,
            'start': r.start_time.strftime('%H:%M'),
            'end': r.end_time.strftime('%H:%M'),
            'room': r.room_number,
            'batch_name': r.batch.name if r.batch else (f"Class {r.grade}" if r.grade else "General")
        } for r in routines]
        
        return Response(data)

    def post(self, request):
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'CLIENT']:
             return Response({"error": "Permission Denied"}, status=403)
             
        data = request.data
        b_id = data.get('batch_id')
        batch = Batch.objects.get(id=b_id) if b_id else None
        
        ClassRoutine.objects.create(
            owner=request.user,
            batch=batch,
            grade=data.get('grade'),
            subject=data.get('subject'),
            teacher_name=data.get('teacher'),
            day_of_week=data.get('day'),
            start_time=data.get('start'),
            end_time=data.get('end'),
            room_number=data.get('room')
        )
        return Response({"message": "Routine Added"}, status=201)
