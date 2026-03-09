from .base import *
from student.models import Attendence, Student, UserProfile
from student.serializers import AttendenceSerializer, StudentSerializer
from student.utils import haversine, validate_coordinates
from drf_spectacular.utils import extend_schema

class AttendenceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    @track_performance
    @cache_api_response(timeout=300, key_prefix='attendance_list')
    @extend_schema(operation_id='attendance_list', responses=AttendenceSerializer(many=True))
    def get(self, request):
        qs = Attendence.objects.select_related('student', 'created_by').all()
        qs = filter_by_owner(qs, request.user)
        serializer = AttendenceSerializer(qs, many=True)
        return Response(serializer.data)

    @transaction.atomic
    @extend_schema(operation_id='attendance_create', request=AttendenceSerializer, responses=AttendenceSerializer)
    def post(self, request):
        from student.models import Student, Attendence
        from student.notifications import send_erp_notification
        
        # Handle Bulk Marking (Standard for Teachers)
        if 'records' in request.data:
            records = request.data['records']
            owner = get_owner_user(request.user)
            today = timezone.now().date()
            
            # 1. Extract Data & Validate Structure
            student_ids = [r.get('student') for r in records if r.get('student')]
            status_map = {str(r.get('student')): r.get('is_present', True) for r in records if r.get('student')}
            
            if not student_ids:
                return Response({"error": "No valid student IDs provided"}, status=400)

            # 2. Batch Fetch Students (Security Check)
            # Only fetch students belonging to this owner
            valid_students = Student.objects.filter(id__in=student_ids, created_by=owner)
            valid_student_map = {str(s.id): s for s in valid_students}
            
            # 3. Check for Existing Attendance
            existing_records = Attendence.objects.filter(
                student__id__in=valid_students.values_list('id', flat=True),
                date=today
            ).values_list('student_id', flat=True)
            existing_set = set(map(str, existing_records))

            to_create = []
            absent_students = []
            errors = []
            created_count = 0
            
            # 4. Prepare Objects
            for s_id, is_present in status_map.items():
                if s_id not in valid_student_map:
                    errors.append(f"Student ID {s_id}: Not found or permission denied")
                    continue
                    
                if s_id in existing_set:
                    errors.append(f"Student {valid_student_map[s_id].name}: Already marked for today")
                    continue
                
                student = valid_student_map[s_id]
                attendence = Attendence(
                    student=student,
                    date=today,
                    is_present=is_present,
                    created_by=owner
                )
                to_create.append(attendence)
                
                if not is_present:
                    absent_students.append(student)

            # 5. Bulk Create
            if to_create:
                Attendence.objects.bulk_create(to_create)
                created_count = len(to_create)
                
                # 6. Trigger Notifications (Manually since bulk_create skips save())
                # Fire and forget (or simple loop)
                for student in absent_students:
                     user_to_notify = student.parent if student.parent else student.user
                     if user_to_notify:
                         try:
                             send_erp_notification(
                                user_to_notify,
                                f"Student Absence Alert: {student.name}",
                                f"This is to inform you that <strong>{student.name}</strong> has been marked <strong>ABSENT</strong> for today ({today})."
                             )
                         except Exception as e:
                             logger.error(f"Failed to send absence notification for {student.name}: {e}")

            # Invalidate all relevant caches
            invalidate_cache('attendance_list*')
            invalidate_cache('dashboard_stats*')
            
            return Response({
                "message": f"Successfully processed {created_count} attendance records",
                "count": created_count,
                "errors": errors if errors else None
            }, status=201 if created_count > 0 else 400)

        # Single Record Logic (Legacy/Mobile)
        serializer = AttendenceSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.validated_data['student']
            if not filter_by_owner(Student.objects.filter(id=student.id), request.user).exists():
                return Response({"error": "Permission denied"}, status=403)

            if Attendence.objects.filter(
                student=student,
                date=serializer.validated_data.get('date', timezone.now().date())
            ).exists():
                return Response({"error": "Already marked"}, status=400)

            owner = get_owner_user(request.user)
            serializer.save(created_by=owner)
            
            # Invalidate cache
            invalidate_cache('attendance_list*')
            invalidate_cache('dashboard_stats*')
            invalidate_cache('student_today*')
            
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class AttendenceDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]

    def get_object(self, user, id):
        qs = Attendence.objects.filter(id=id)
        return filter_by_owner(qs, user).first()

    @extend_schema(operation_id='attendance_retrieve', responses=AttendenceSerializer)
    def get(self, request, id):
        # SECURITY FIX #7: IDOR Protection
        attendance = self.get_object(request.user, id)
        if not attendance:
             return Response({"error": "Attendance record not found or access denied"}, status=404)
        return Response(AttendenceSerializer(attendance).data)
    
    @extend_schema(operation_id='attendance_update', request=AttendenceSerializer, responses=AttendenceSerializer)
    def put(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
             return Response({"error": "Not found"}, status=404)
        serializer = AttendenceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @extend_schema(operation_id='attendance_delete')
    def delete(self, request, id):
        attendance = self.get_object(request.user, id)
        if not attendance:
            return Response({"error": "Not found"}, status=404)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AttendanceScanView(APIView):
    """
    Mark attendance via QR Scan
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Support both 'student_id' and 'qr_code' for flexibility
        student_id = request.data.get('student_id') or request.data.get('qr_code')
        
        if not student_id:
            return Response({"error": "Student ID required"}, status=400)
            
        student = get_object_or_404(Student, id=student_id)
        
        # Security: Only Staff members or Institution Admins (CLIENT) can mark attendance
        # Students shouldn't be able to mark their own or others' attendance via scan
        user_profile = getattr(request.user, 'profile', None)
        if user_profile and user_profile.role == 'STUDENT':
             return Response({"error": "Only staff members can mark attendance."}, status=403)
             
        # Verify ownership
        owner = get_owner_user(request.user)
        if not request.user.is_superuser and student.created_by != owner:
            return Response({"error": "Access Denied"}, status=403)

        today = timezone.now().date()
        
        # Mark present
        obj, created = Attendence.objects.get_or_create(
            student=student,
            date=today,
            defaults={
                'is_present': True,
                'created_by': request.user,
                'metadata': {'method': 'QR_SCAN', 'timestamp': str(timezone.now())}
            }
        )
        
        # Prep response data
        response_data = {
            "success": True,
            "student_name": student.name,
            "status_msg": "Attendance Marked" if created else "Already Marked",
            "time": timezone.now().strftime("%I:%M %p"),
            "photo": student.photo.url if student.photo else None
        }

        if not created:
             response_data["success"] = True # Still a success from UI perspective
             return Response(response_data, status=200)
             
        # Invalidate cache
        invalidate_cache('attendance_list*')
        
        return Response(response_data, status=201)

class GeoFencedAttendanceView(APIView):
    """
    Mark attendance securely using Geolocation (Enterprise V4).
    Allowed only if user is within 'attendance_radius' of the institution location.
    """
    from student.throttling import AttendanceRateThrottle
    permission_classes = [IsAuthenticated]
    throttle_classes = [AttendanceRateThrottle]

    def post(self, request):
        user = request.user
        from django.core.exceptions import ObjectDoesNotExist

        try:
            lat = float(request.data.get("lat"))
            lon = float(request.data.get("long"))
            if not validate_coordinates(lat, lon):
                return Response({"error": "Invalid GPS coordinates range"}, status=400)
        except (TypeError, ValueError):
            return Response({"error": "Valid GPS coordinates (lat/long) required"}, status=400)

        target_profile = self.get_institution_profile(user)
        if not target_profile or not target_profile.location_lat or not target_profile.location_long:
            return Response({
                "error": "Institution location not configured by Administrator.",
                "code": "LOCATION_NOT_SET"
            }, status=400)

        distance = haversine(
            lon, lat,
            target_profile.location_long,
            target_profile.location_lat
        )

        if distance > target_profile.attendance_radius:
            logger.warning(f"OUT_OF_RANGE Attendance Attempt: User={user.id}, Dist={int(distance)}m, Limit={target_profile.attendance_radius}m")
            return Response({
                "error": "Out of attendance range",
                "distance": int(distance),
                "limit": target_profile.attendance_radius
            }, status= status.HTTP_403_FORBIDDEN)

        return self.mark_attendance(user, distance, lat, lon)

    def get_institution_profile(self, user):
        """Find the institution profile governing this user"""
        from django.core.exceptions import ObjectDoesNotExist
        try:
            if hasattr(user, 'profile') and user.profile.role == "CLIENT":
                return user.profile
        except ObjectDoesNotExist:
            pass

        try:
            return user.student_profile.created_by.profile
        except Exception:
            pass

        try:
             # If Employee/Teacher: Their creator's profile
            if hasattr(user, 'employee_profile'):
                 return user.employee_profile.created_by.profile
        except Exception:
            pass

        owner = get_owner_user(user)
        return getattr(owner, 'profile', None)

    def mark_attendance(self, user, distance, lat, lon):
        """Atomic Attendance Marking with Role Support"""
        from student.models import Attendence, Employee
        today = timezone.now().date()
        metadata = {
            "distance_meters": int(distance),
            "lat": lat,
            "lon": lon,
            "timestamp": timezone.now().isoformat(),
            "method": "GEOFENCED_SELF"
        }

        try:
            # A. STUDENT LOGIC
            if hasattr(user, 'student_profile'):
                student = user.student_profile
                existing = Attendence.objects.filter(student=student, date=today).first()
                if existing:
                    return Response({"message": "Already marked today"}, status=200)
                
                # Add remarks to metadata
                metadata['remarks'] = f"Geo-Attendance: {int(distance)}m away"
                
                Attendence.objects.create(
                    student=student,
                    date=today,
                    is_present=True,
                    created_by=user, # Self marked
                    metadata=metadata
                )
                return Response({"message": "Attendance Marked Successfully", "distance": int(distance)}, status=201)

            # B. STAFF LOGIC (Secure Employee Attendance)
            if hasattr(user, 'employee_profile'):
                employee = user.employee_profile
                existing = Attendence.objects.filter(employee=employee, date=today).first()
                if existing:
                    return Response({"message": "Staff attendance already marked today"}, status=200)

                # Add remarks to metadata
                metadata['remarks'] = f"Staff Geo-Attendance: {int(distance)}m away"

                Attendence.objects.create(
                    employee=employee,
                    date=today,
                    is_present=True,
                    created_by=user,
                    metadata=metadata
                )
                return Response({"message": "Staff Attendance Marked", "distance": int(distance)}, status=201)

            return Response({"error": "User role not eligible for self-attendance"}, status=400)

        except Exception as e:
            logger.error(f"Attendance Marking Error: {str(e)}")
            return Response({"error": "Internal system error during attendance marking"}, status=500)
