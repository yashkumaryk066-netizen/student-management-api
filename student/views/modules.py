from .base import *
from student.models import (
    LibraryBook, BookIssue, Hostel, Room, HostelAllocation,
    Vehicle, Route, TransportAllocation, Employee, LeaveRequest,
    Notification, DemoRequest, Student, Course, Batch
)
from student.serializers import (
    LibraryBookSerializer, BookIssueSerializer, HostelSerializer, RoomSerializer,
    HostelAllocationSerializer, VehicleSerializer, RouteSerializer,
    TransportAllocationSerializer, EmployeeSerializer, LeaveRequestSerializer,
    NotificationSerializer
)
from student.permissions import IsStaffWithPermission, IsTeacherOrAdmin

# --- LIBRARY ---

class LibraryBookListCreateView(generics.ListCreateAPIView):
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return filter_by_owner(LibraryBook.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class LibraryBookDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_queryset(self):
        return filter_by_owner(LibraryBook.objects.all(), self.request.user)

class BookIssueListCreateView(generics.ListCreateAPIView):
    serializer_class = BookIssueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            BookIssue.objects.select_related('book', 'student'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- HOSTEL ---

class HostelListCreateView(generics.ListCreateAPIView):
    serializer_class = HostelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Hostel.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Room.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class HostelAllocationListCreateView(generics.ListCreateAPIView):
    serializer_class = HostelAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            HostelAllocation.objects.select_related('student', 'room', 'room__hostel'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class HostelAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owner = get_owner_user(request.user)
        hostels = Hostel.objects.filter(created_by=owner)
        rooms = Room.objects.filter(hostel__in=hostels)
        
        total_beds = rooms.aggregate(Sum('capacity'))['capacity__sum'] or 0
        
        # Count active allocations
        occupied_beds = HostelAllocation.objects.filter(
            room__hostel__in=hostels,
            status='ACTIVE'
        ).count()
        
        vacant_beds = max(0, total_beds - occupied_beds)
        
        # Room Status Breakdown
        return Response({
            "total_hostels": hostels.count(),
            "total_rooms": rooms.count(),
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "vacant_beds": vacant_beds,
            "occupancy_rate": round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0
        })

# --- TRANSPORT ---

class VehicleListCreateView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(Vehicle.objects.all(), self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class RouteListCreateView(generics.ListCreateAPIView):
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            Route.objects.select_related('vehicle'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

class TransportAllocationListCreateView(generics.ListCreateAPIView):
    serializer_class = TransportAllocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            TransportAllocation.objects.select_related('student', 'route'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- HR / STAFF ---

class EmployeeListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffWithPermission]
    required_permission = 'staff.view'

    def get_queryset(self):
         return filter_by_owner(
             Employee.objects.select_related('user', 'user__profile', 'department', 'designation').all(), 
             self.request.user
         )

    def perform_create(self, serializer):
        owner = get_owner_user(self.request.user)
        serializer.save(created_by=owner)

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return filter_by_owner(
            LeaveRequest.objects.select_related('employee', 'employee__user', 'approved_by'), 
            self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(created_by=get_owner_user(self.request.user))

# --- COMMUNICATION / NOTIFICATIONS ---

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = getattr(getattr(request.user, 'profile', None), 'role', None) or 'STUDENT'
        qs = Notification.objects.filter(
            Q(recipient=request.user) |
            Q(recipient_type=role) |
            Q(recipient_type='ALL')
        ).order_by('-created_at')
        # Isolation: owner-specific notifications + system/global (created_by is null)
        if not request.user.is_superuser:
            owner = get_owner_user(request.user)
            if owner:
                qs = qs.filter(Q(created_by=owner) | Q(created_by__isnull=True))
            else:
                qs = qs.filter(created_by__isnull=True)
        return Response(NotificationSerializer(qs, many=True).data)

class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        notification = Notification.objects.filter(id=id).first()
        if not notification:
            return Response({"error": "Not found"}, status=404)

        allowed = (
            notification.recipient_id == request.user.id or
            notification.recipient_type == 'ALL'
        )
        if not allowed:
            return Response({"error": "Forbidden"}, status=403)

        notification.is_read = True
        notification.save()
        return Response({"message": "Marked as read"})

class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = getattr(getattr(request.user, 'profile', None), 'role', None) or 'STUDENT'
        
        # Mark all unread notifications for this user as read
        Notification.objects.filter(
            Q(recipient=request.user) |
            Q(recipient_type=role) |
            Q(recipient_type='ALL'),
            is_read=False
        ).update(is_read=True)
        
        return Response({"message": "All notifications marked as read"})

class NotificationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            owner = get_owner_user(request.user)
            serializer.save(created_by=owner)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class DemoRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request):
        data = request.data
        try:
            demo = DemoRequest.objects.create(
                name=data.get('name'),
                phone=data.get('phone'),
                email=data.get('email'),
                institution_name=data.get('institution_name', ''),
                institution_type=data.get('institution_type', ''),
                message=data.get('message', '')
            )
            return Response({"message": "Demo request submitted successfully", "id": demo.id}, status=201)
        except Exception as e:
             return Response({"error": str(e)}, status=400)

# --- GLOBAL SEARCH ---

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
                    'subtitle': f"Fee: {c.fee}",
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

        # 4. Search Staff/Employees
        staff = Employee.objects.select_related('user', 'designation').filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__username__icontains=query)
        )
        staff = filter_by_owner(staff, user)[:3]
        for e in staff:
            results.append({
                'type': 'Staff',
                'title': e.user.get_full_name() or e.user.username,
                'subtitle': f"{e.designation.title if e.designation else 'Staff'}",
                'url': f"#team",
                'icon': '👔'
            })

        # 5. Search Library Books
        books = LibraryBook.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query)
        )
        books = filter_by_owner(books, user)[:3]
        for b in books:
            results.append({
                'type': 'Book',
                'title': b.title,
                'subtitle': f"Author: {b.author}",
                'url': f"#library/books/{b.id}",
                'icon': '📖'
            })

        return Response(results)
