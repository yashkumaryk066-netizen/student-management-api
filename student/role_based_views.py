# Role-Based Dashboard and New Feature Views
# Add these to existing views.py

from .models import UserProfile, Payment, Notification
from .Serializer import UserProfileSerializer, PaymentSerializer, NotificationSerializer
from .permissions import IsStudent, IsTeacher, IsParent, IsAdminRole, IsTeacherOrAdmin
from django.db.models import Count, Q
from datetime import date, timedelta

# ==================== ROLE-BASED DASHBOARDS ====================

class StudentDashboardView(APIView):
    """Dashboard for students - own attendance, fees, notifications"""
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get(self, request):
        try:
            student = Student.objects.get(user=request.user)
            
            # Get attendance records
            total_days = Attendence.objects.filter(student=student).count()
            present_days = Attendence.objects.filter(student=student, is_present=True).count()
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
            
            # Get payment info
            pending_payments = Payment.objects.filter(student=student, status__in=['PENDING', 'OVERDUE'])
            total_due = sum(p.amount for p in pending_payments)
            
            # Get recent notifications
            notifications = Notification.objects.filter(
                Q(recipient=request.user) | Q(recipient_type='STUDENT') | Q(recipient_type='ALL'),
                is_read=False
            )[:5]
            
            return Response({
                'role': 'STUDENT',
                'student': StudentSerializer(student).data,
                'attendance': {
                    'total_days': total_days,
                    'present_days': present_days,
                    'attendance_percentage': round(attendance_percentage, 2)
                },
                'payments': {
                    'total_due': float(total_due),
                    'pending_count': pending_payments.count(),
                    'payments': PaymentSerializer(pending_payments, many=True).data
                },
                'notifications': NotificationSerializer(notifications, many=True).data
            }, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)

class TeacherDashboardView(APIView):
    """Dashboard for teachers - all students, mark attendance, send notifications"""
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get(self, request):
        today = timezone.now().date()
        
        # Get all students
        total_students = Student.objects.count()
        
        # Today's attendance
        today_attendance = Attendence.objects.filter(date=today)
        present_today = today_attendance.filter(is_present=True).count()
        absent_today = today_attendance.filter(is_present=False).count()
        
        # Pending payments count
        overdue_payments = Payment.objects.filter(status='OVERDUE').count()
        
        # Unread notifications
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='TEACHER') | Q(recipient_type='ALL'),
            is_read=False
        )[:5]
        
        return Response({
            'role': 'TEACHER',
            'stats': {
                'total_students': total_students,
                'present_today': present_today,
                'absent_today': absent_today,
                'not_marked': total_students - present_today - absent_today,
                'overdue_payments': overdue_payments
            },
            'notifications': NotificationSerializer(notifications, many=True).data
        }, status=status.HTTP_200_OK)

class ParentDashboardView(APIView):
    """Dashboard for parents - children's data, payments, notifications"""
    permission_classes = [IsAuthenticated, IsParent]
    
    def get(self, request):
        # Get all children linked to this parent
        children = Student.objects.filter(parent=request.user)
        
        if not children.exists():
            return Response({'error': 'No children linked to this account'}, status=status.HTTP_404_NOT_FOUND)
        
        children_data = []
        total_due = 0
        
        for child in children:
            # Get attendance
            total_days = Attendence.objects.filter(student=child).count()
            present_days = Attendence.objects.filter(student=child, is_present=True).count()
            
            # Get payments
            pending_payments = Payment.objects.filter(student=child, status__in=['PENDING', 'OVERDUE'])
            child_due = sum(p.amount for p in pending_payments)
            total_due += child_due
            
            children_data.append({
                'student': StudentSerializer(child).data,
                'attendance': {
                    'total_days': total_days,
                    'present_days': present_days,
                    'percentage': round((present_days / total_days * 100) if total_days > 0 else 0, 2)
                },
                'payments': {
                    'due_amount': float(child_due),
                    'pending_count': pending_payments.count()
                }
            })
        
        # Get notifications
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='PARENT') | Q(recipient_type='ALL'),
            is_read=False
        )[:5]
        
        return Response({
            'role': 'PARENT',
            'children': children_data,
            'total_due': float(total_due),
            'notifications': NotificationSerializer(notifications, many=True).data
        }, status=status.HTTP_200_OK)

# ==================== PAYMENT VIEWS ====================

class PaymentListCreateView(APIView):
    """List and create payments"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'ADMIN'
        
        if user_role == 'PARENT':
            # Parents see only their children's payments
            children = Student.objects.filter(parent=request.user)
            payments = Payment.objects.filter(student__in=children)
        elif user_role == 'STUDENT':
            # Students see only their own payments
            try:
                student = Student.objects.get(user=request.user)
                payments = Payment.objects.filter(student=student)
            except Student.DoesNotExist:
                return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Teachers and admins see all
            payments = Payment.objects.all()
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        # Only admin and teachers can create payments
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['ADMIN', 'TEACHER']:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            
            # Create notification for parent
            student = payment.student
            if student.parent:
                Notification.objects.create(
                    recipient_type='PARENT',
                    recipient=student.parent,
                    title=f'New Payment Due for {student.name}',
                    message=f'A payment of ₹{payment.amount} is due on {payment.due_date.strftime("%d-%b-%Y")}. {payment.description}'
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentDetailsView(APIView):
    """View and update specific payment"""
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id):
        try:
            payment = Payment.objects.get(id=id)
            
            # Mark as paid
            if request.data.get('mark_paid'):
                payment.status = 'PAID'
                payment.paid_date = timezone.now().date()
                payment.save()
                
                # Notify parent
                if payment.student.parent:
                    Notification.objects.create(
                        recipient_type='PARENT',
                        recipient=payment.student.parent,
                        title='Payment Confirmed',
                        message=f'Payment of ₹{payment.amount} for {payment.student.name} has been confirmed. Thank you!'
                    )
                
                return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
            
            # Update payment details
            serializer = PaymentSerializer(payment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

# ==================== NOTIFICATION VIEWS ====================

class NotificationListView(APIView):
    """Get notifications for current user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_role = request.user.profile.role if hasattr(request.user, 'profile') else 'ADMIN'
        
        # Get notifications for this user's role or specifically for them
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | 
            Q(recipient_type=user_role) | 
            Q(recipient_type='ALL')
        )
        
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationMarkReadView(APIView):
    """Mark notification as read"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        try:
            notification = Notification.objects.get(id=id)
            notification.is_read = True
            notification.save()
            return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

class NotificationCreateView(APIView):
    """Create notification (admin/teacher only)"""
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    
    def post(self, request):
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
