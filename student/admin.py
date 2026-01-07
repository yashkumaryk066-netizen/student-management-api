from django.contrib import admin
from .models import (
    Student, Attendence, UserProfile, Payment, Notification,
    Subject, Classroom, ClassSchedule,
    Hostel, Room, HostelAllocation,
    Event, EventParticipant,
    DemoRequest, ClientSubscription
)

@admin.register(ClientSubscription)
class ClientSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan_type', 'status', 'start_date', 'end_date', 'days_remaining']
    list_filter = ['status', 'plan_type', 'end_date']
    search_fields = ['user__username', 'transaction_id']
    actions = ['force_renew_subscription', 'suspend_account', 'reactivate_account', 'reduce_validity_7_days']
    
    def force_renew_subscription(self, request, queryset):
        for sub in queryset:
            sub.activate(days=30)
        self.message_user(request, f"Renewed {queryset.count()} subscriptions for 30 days.")
    force_renew_subscription.short_description = "⚡ Renew for 30 Days"

    def suspend_account(self, request, queryset):
        """Hard Block the Client"""
        cnt = queryset.update(status='SUSPENDED')
        self.message_user(request, f"🚫 Suspended {cnt} accounts. They generally cannot access any feature now.")
    suspend_account.short_description = "🚫 Block/Suspend Access"

    def reactivate_account(self, request, queryset):
        """Unblock"""
        cnt = queryset.update(status='ACTIVE')
        self.message_user(request, f"✅ Reactivated {cnt} accounts.")
    reactivate_account.short_description = "✅ Unblock/Activate"

    def reduce_validity_7_days(self, request, queryset):
        """Penalty: Reduce 7 days"""
        from datetime import timedelta
        success = 0
        for sub in queryset:
            if sub.end_date:
                sub.end_date -= timedelta(days=7)
                sub.save()
                # Sync with UserProfile
                if hasattr(sub.user, 'profile'):
                    sub.user.profile.subscription_expiry = sub.end_date
                    sub.user.profile.save()
                success += 1
        self.message_user(request, f"📉 Reduced 7 days from {success} subscriptions.")
    reduce_validity_7_days.short_description = "📉 Reduce Validity by 7 Days"
    force_renew_subscription.short_description = "Force Renew (30 Days)"


# ==================== STUDENT MANAGEMENT ====================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'roll_number', 'grade', 'institution_type', 'has_photo']
    list_filter = ['grade', 'institution_type', 'blood_group']
    search_fields = ['name', 'roll_number', 'contact_number']
    list_per_page = 50
    ordering = ['-id']
    actions = ['download_id_card', 'download_admission_letter', 'download_admit_card']
    
    def has_photo(self, obj):
        return "✅" if obj.photo else "❌"
    has_photo.short_description = "Photo"

    def download_id_card(self, request, queryset):
        """Generate and download ID cards for selected students"""
        from django.http import HttpResponse
        from .id_card_utils import generate_id_card_pdf
        import zipfile
        from io import BytesIO
        
        # If single student, return PDF directly
        if queryset.count() == 1:
            student = queryset.first()
            if not student.roll_number:
                self.message_user(request, f"⚠️ Roll Number missing for {student.name}", level='error')
                return
                
            pdf_buffer = generate_id_card_pdf(student)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="ID_Card_{student.roll_number}.pdf"'
            return response
            
        # If multiple, return ZIP
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for student in queryset:
                if student.roll_number:
                    pdf_buffer = generate_id_card_pdf(student)
                    zip_file.writestr(f"ID_{student.roll_number}.pdf", pdf_buffer.getvalue())
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Student_ID_Cards.zip"'
        return response
    download_id_card.short_description = "🪪 Download Smart ID Card"

    def download_admission_letter(self, request, queryset):
        """Generate Admission Welcome Letter"""
        from django.http import HttpResponse
        from .admission_letter_utils import generate_admission_letter_pdf
        import zipfile
        from io import BytesIO
        
        # Single Download
        if queryset.count() == 1:
            student = queryset.first()
            pdf_buffer = generate_admission_letter_pdf(student)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Admission_Letter_{student.name}.pdf"'
            return response
            
        # Bulk Download
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for student in queryset:
                pdf_buffer = generate_admission_letter_pdf(student)
                zip_file.writestr(f"Admission_Letter_{student.name}.pdf", pdf_buffer.getvalue())
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Admission_Letters.zip"'
        return response
    download_admission_letter.short_description = "📄 Download Admission Letter"

    def download_admit_card(self, request, queryset):
        """Generate Exam Admit Card (Hall Ticket)"""
        from django.http import HttpResponse
        from .admit_card_utils import generate_admit_card_pdf
        import zipfile
        from io import BytesIO
        
        # Single Download
        if queryset.count() == 1:
            student = queryset.first()
            try:
                pdf_buffer = generate_admit_card_pdf(student)
                response = HttpResponse(pdf_buffer, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="Admit_Card_{student.roll_number or student.name}.pdf"'
                return response
            except Exception as e:
                self.message_user(request, f"Error: {str(e)}", level='error')
                return

        # Bulk Download
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for student in queryset:
                try:
                    pdf_buffer = generate_admit_card_pdf(student)
                    zip_file.writestr(f"Admit_Card_{student.roll_number or student.name}.pdf", pdf_buffer.getvalue())
                except:
                    continue
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="Exam_Admit_Cards.zip"'
        return response
    download_admit_card.short_description = "🎫 Download Exam Admit Card"


@admin.register(Attendence)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'is_present']
    list_filter = ['is_present', 'date']
    search_fields = ['student__name']
    date_hierarchy = 'date'
    list_per_page = 100


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'institution_type', 'subscription_status', 'days_left']
    list_filter = ['role', 'institution_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']

    def subscription_status(self, obj):
        if obj.role == 'CLIENT':
            return "Active" if obj.subscription_expiry and obj.subscription_expiry >= timezone.now().date() else "Expired"
        return "-"
    
    def days_left(self, obj):
        if obj.role == 'CLIENT' and obj.subscription_expiry:
             delta = obj.subscription_expiry - timezone.now().date()
             return f"{delta.days} days"
        return "-"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['get_payment_reference', 'amount', 'status', 'payment_type', 'due_date', 'paid_date']
    list_filter = ['status', 'payment_type', 'due_date']
    search_fields = ['student__name', 'user__username', 'description', 'transaction_id']
    list_editable = ['status']
    date_hierarchy = 'due_date'
    ordering = ['-due_date']
    actions = ['approve_payment_and_renew']

    def get_payment_reference(self, obj):
        if obj.payment_type == 'SUBSCRIPTION' and obj.user:
            return f"{obj.user.username} (Sub Renewal)"
        return obj.student.name if obj.student else "Unknown"
    get_payment_reference.short_description = "Payer"

    def approve_payment_and_renew(self, request, queryset):
        """
        Approve payment and activate/extend subscription
        - Generates PDF Invoice
        - Emails Credentials/Renewal Info + Invoice Attachment
        """
        from django.core.mail import EmailMessage
        from django.conf import settings
        from django.utils import timezone
        from .utils import generate_invoice_pdf
        
        success_count = 0
        for payment in queryset:
            if payment.status == 'APPROVED':
                self.message_user(request, f"⚠️ Payment #{payment.id} already approved.", level='warning')
                continue
            
            # Update Payment Status
            payment.status = 'APPROVED'
            payment.paid_date = timezone.now().date()
            payment.save()
            
            # Process Subscription Payment
            if payment.payment_type == 'SUBSCRIPTION' and payment.user:
                user = payment.user
                
                # Check if renewal or first purchase
                is_renewal = False
                if hasattr(user, 'profile') and user.profile.plan_purchased_at:
                    is_renewal = True
                
                # Extend/Activate Subscription
                if hasattr(user, 'subscription'):
                    user.subscription.activate(days=30)
                    
                    # Sync with UserProfile
                    if hasattr(user, 'profile'):
                        if not user.profile.plan_purchased_at:
                            user.profile.plan_purchased_at = timezone.now()
                        user.profile.subscription_expiry = user.subscription.end_date
                        user.profile.is_active = True
                        user.profile.save()
                
                # Generate Invoice PDF
                try:
                    pdf_buffer = generate_invoice_pdf(payment)
                    pdf_content = pdf_buffer.getvalue()
                    pdf_name = f"Invoice_INV-{payment.id:06d}.pdf"
                except Exception as e:
                    print(f"PDF Gen Error: {e}")
                    pdf_content = None

                # Email Notification
                plan_name = user.profile.institution_type if hasattr(user, 'profile') else 'Standard'
                
                if is_renewal:
                    # RENEWAL
                    subject = f'✅ Subscription Renewed - {plan_name} Plan'
                    message = f"""
Dear {user.get_full_name() or user.username},

Your {plan_name} Plan subscription has been renewed successfully!

🔄 RENEWAL DETAILS:
- Extended: +30 Days
- New Expiry: {user.profile.subscription_expiry if hasattr(user, 'profile') else 'N/A'}
- Amount Paid: ₹{payment.amount}
- Payment Mode: {payment.get_payment_mode_display()}

Please find the TAX INVOICE attached.

Dashboard: https://yashamishra.pythonanywhere.com/dashboard

Thank you for your business!
Y.S.M ADVANCE EDUCATION SYSTEM
                    """
                else:
                    # FIRST PURCHASE
                    login_url = "https://yashamishra.pythonanywhere.com/admin/"
                    subject = f'🎉 Activated: Your {plan_name} Plan is Live!'
                    message = f"""
Dear {user.get_full_name() or user.username},

Welcome to Y.S.M ADVANCE EDUCATION SYSTEM!

Your {plan_name} Plan has been approved and activated.

🔐 LOGIN CREDENTIALS:
URL: {login_url}
Username: {user.username}
Email: {user.email}

⏰ PLAN VALIDITY:
- Type: {plan_name}
- Validity: 30 Days
- Expires On: {user.profile.subscription_expiry if hasattr(user, 'profile') else 'N/A'}

Please find your TAX INVOICE attached to this email.

📌 IMPORTANT:
1. Change password after first login.
2. Renew before expiry to ensure uninterrupted service.

Get Started: {login_url}

Best Regards,
Y.S.M Team
                    """
                
                # Send Email with Attachment
                try:
                    email = EmailMessage(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                    if pdf_content:
                        email.attach(pdf_name, pdf_content, 'application/pdf')
                    
                    email.send(fail_silently=False)
                    self.message_user(request, f"✅ Email sent to {user.email} with Invoice.")
                except Exception as e:
                    self.message_user(request, f"⚠️ Email failed for {user.username}: {str(e)}", level='warning')
            
            success_count += 1
        
        self.message_user(request, f"✅ Successfully processed {success_count} payment(s).")
    approve_payment_and_renew.short_description = "✅ Approve & Send Invoice (Email)"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recipient_type', 'recipient', 'is_read', 'created_at']
    list_filter = ['recipient_type', 'is_read', 'created_at']
    search_fields = ['title', 'message']
    date_hierarchy = 'created_at'
    list_editable = ['is_read']


# ==================== ACADEMICS ====================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'created_at']
    search_fields = ['name', 'code']
    ordering = ['code']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'capacity', 'floor', 'building']
    list_filter = ['room_type', 'floor', 'building']
    search_fields = ['room_number', 'building']
    ordering = ['building', 'floor', 'room_number']


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['section', 'subject', 'teacher', 'classroom', 'day_of_week', 'start_time', 'end_time', 'academic_year']
    list_filter = ['day_of_week', 'academic_year', 'section']
    search_fields = ['section', 'subject__name', 'teacher__username']
    ordering = ['day_of_week', 'start_time']


# ==================== HOSTEL MANAGEMENT ====================

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'hostel_type', 'total_rooms', 'warden']
    list_filter = ['hostel_type']
    search_fields = ['name', 'address']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hostel', 'room_number', 'floor', 'capacity', 'current_occupancy', 'available_beds', 'room_type']
    list_filter = ['hostel', 'floor', 'room_type']
    search_fields = ['room_number']
    ordering = ['hostel', 'floor', 'room_number']
    
    def available_beds(self, obj):
        return obj.available_beds
    available_beds.short_description = 'Available Beds'


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'check_in_date', 'check_out_date', 'status', 'monthly_fee']
    list_filter = ['status', 'check_in_date', 'room__hostel']
    search_fields = ['student__name', 'room__room_number']
    date_hierarchy = 'check_in_date'
    ordering = ['-check_in_date']


# ==================== EVENTS ====================

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'start_date', 'end_date', 'venue', 'organizer', 'is_active']
    list_filter = ['event_type', 'is_active', 'start_date']
    search_fields = ['name', 'description', 'venue']
    date_hierarchy = 'start_date'
    list_editable = ['is_active']
    ordering = ['-start_date']


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'participation_type', 'registration_date', 'attended']
    list_filter = ['participation_type', 'attended', 'registration_date']
    search_fields = ['event__name', 'user__username']
    date_hierarchy = 'registration_date'
    list_editable = ['attended']


# ==================== DEMO REQUESTS ====================

@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'institution_name', 'status', 'created_at']
    list_filter = ['status', 'institution_type', 'created_at']
    search_fields = ['name', 'phone', 'email', 'institution_name']
    date_hierarchy = 'created_at'
    list_editable = ['status']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    actions = ['convert_to_client_and_notify']

    def convert_to_client_and_notify(self, request, queryset):
        """
        Converts a DemoRequest into a full CLIENT User.
        1. Creates User (if not exists)
        2. Assigns CLIENT role
        3. Creates Subscription (based on request)
        4. Emails/WhatsApp credentials
        """
        from django.contrib.auth.models import User
        from .models import UserProfile, ClientSubscription
        from django.utils.crypto import get_random_string
        from django.core.mail import send_mail
        from django.conf import settings
        from django.utils import timezone
        from notifications.whatsapp_service import whatsapp_service
        
        success_count = 0
        
        for demo_req in queryset:
            if demo_req.status == 'CONVERTED':
                continue
                
            # 1. Generate Credentials
            username = demo_req.email.split('@')[0].lower()[:15] + get_random_string(4)
            password = get_random_string(10)
            
            # 2. Create User
            if User.objects.filter(username=username).exists():
                 username = username + get_random_string(3)
            
            user = User.objects.create_user(username=username, email=demo_req.email, password=password)
            user.first_name = demo_req.name.split(' ')[0]
            user.save()
            
            # 3. Create UserProfile (CLIENT Role)
            # Default to SCHOOL if not specified clearly, or parse from institution_type
            inst_type_map = {
                'School': 'SCHOOL',
                'College': 'INSTITUTE',
                'University': 'INSTITUTE',
                'Coaching': 'COACHING'
            }
            # Normalize key
            inst_key = demo_req.institution_type.capitalize()
            plan_type = inst_type_map.get(inst_key, 'SCHOOL')
            
            UserProfile.objects.create(
                user=user, 
                role='CLIENT', 
                institution_type=plan_type,
                phone=demo_req.phone
            )
            
            # 4. Create Active Subscription (Trial 30 Days)
            # Grants access ONLY to the purchased plan features
            ClientSubscription.objects.create(
                user=user,
                plan_type=plan_type,
                status='ACTIVE',
                auto_renew=False
            ).activate(days=30)
            
            # 5. Send Notifications (Email + WhatsApp)
            message_body = f"""
🎉 *Welcome to NextGen ERP!*

Dear {demo_req.name},

Your request for *{plan_type} Management System* has been approved!
You have been granted access for **30 days** starting today.

🔐 *Your Login Credentials:*
URL: https://yashamishra.pythonanywhere.com/admin/
Username: *{username}*
Password: *{password}*

⚠️ *Important:*
- You only have access to **{plan_type}** features.
- Please change your password after logging in.
- To continue using the service after 30 days, please renew your plan from the dashboard.

_Thank you for choosing NextGen ERP!_
            """
            
            # WhatsApp
            whatsapp_service.send_message(demo_req.phone, message_body)
            
            # Email
            try:
                send_mail(
                    subject=f'Approved: {plan_type} Plan Access - NextGen ERP',
                    message=message_body.replace('*', '').replace('⚠️', 'Note:').replace('🔐', ''), 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[demo_req.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Email failed: {e}")
            
            # Update Status
            demo_req.status = 'CONVERTED'
            demo_req.notes += f"\n[System] Converted to {plan_type} Client on {timezone.now()}. User: {username}"
            demo_req.save()
            
            success_count += 1
            
        self.message_user(request, f"Successfully processed {success_count} approvals.")
    
    convert_to_client_and_notify.short_description = "Approve & Send Credentials (Convert to Client)"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Institution Details', {
            'fields': ('institution_name', 'institution_type', 'message')
        }),
        ('Status & Notes', {
            'fields': ('status', 'contacted_at', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== EXAM & GRADING ====================

from .models import Exam, Grade, ResultCard, LibraryBook, BookIssue

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'grade_class', 'total_marks', 'passing_marks', 'exam_date', 'academic_year']
    list_filter = ['exam_type', 'academic_year', 'grade_class', 'exam_date']
    search_fields = ['name', 'subject__name', 'grade_class']
    date_hierarchy = 'exam_date'
    ordering = ['-exam_date']


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'marks_obtained', 'get_total_marks', 'percentage', 'status']
    list_filter = ['status', 'exam__exam_type', 'exam__academic_year']
    search_fields = ['student__name', 'exam__name']
    ordering = ['-exam__exam_date']
    
    def get_total_marks(self, obj):
        return obj.exam.total_marks
    get_total_marks.short_description = 'Total Marks'
    
    def percentage(self, obj):
        return f"{obj.percentage:.2f}%"


@admin.register(ResultCard)
class ResultCardAdmin(admin.ModelAdmin):
    list_display = ['student', 'grade_class', 'semester_term', 'academic_year', 'percentage', 'gpa', 'result_status']
    list_filter = ['result_status', 'academic_year', 'grade_class']
    search_fields = ['student__name']
    ordering = ['-generated_at']


# ==================== LIBRARY ====================

@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ['isbn', 'title', 'author', 'category', 'total_copies', 'available_copies', 'is_available', 'price']
    list_filter = ['category', 'published_year']
    search_fields = ['isbn', 'title', 'author', 'publisher']
    ordering = ['title']
    list_per_page = 50
    
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Available'


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ['book', 'student', 'issue_date', 'due_date', 'return_date', 'status', 'fine_amount']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['book__title', 'student__name']
    date_hierarchy = 'issue_date'
    list_editable = ['status']
    ordering = ['-issue_date']
    
    fieldsets = (
        ('Issue Details', {
            'fields': ('book', 'student', 'due_date')
        }),
        ('Return Details', {
            'fields': ('return_date', 'status', 'fine_amount')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

# ==================== TRANSPORT ====================

from .models import Vehicle, Route, TransportAllocation

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['registration_number', 'vehicle_type', 'capacity', 'driver_name', 'driver_phone', 'is_active']
    list_filter = ['vehicle_type', 'is_active']
    search_fields = ['registration_number', 'driver_name']
    ordering = ['registration_number']

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['route_name', 'start_point', 'end_point', 'vehicle', 'pickup_time', 'monthly_fare']
    list_filter = ['vehicle']
    search_fields = ['route_name', 'stops']
    ordering = ['route_name']

@admin.register(TransportAllocation)
class TransportAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'route', 'pickup_stop', 'start_date', 'end_date', 'is_active']
    list_filter = ['route', 'is_active', 'start_date']
    search_fields = ['student__name', 'route__route_name']
    list_editable = ['is_active']


# ==================== HR & PAYROLL ====================

from .models import Department, Designation, Employee, LeaveRequest, Payroll

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head_of_department']
    search_fields = ['name']

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'designation', 'joining_date', 'contract_type', 'is_active']
    list_filter = ['department', 'designation', 'contract_type', 'is_active', 'joining_date']
    search_fields = ['user__username', 'user__email', 'user__first_name']
    date_hierarchy = 'joining_date'
    list_editable = ['is_active']

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'approved_by']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__user__username']
    list_editable = ['status']
    date_hierarchy = 'start_date'

@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'basic_salary', 'net_salary', 'status', 'payment_date']
    list_filter = ['status', 'month', 'year']
    search_fields = ['employee__user__username', 'transaction_id']
    list_editable = ['status']
    ordering = ['-year', '-month']
