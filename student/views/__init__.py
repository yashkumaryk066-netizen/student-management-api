from .base import *
from .auth import *
from .admin import *
from .students import *
from .attendance import *
from .academic import *
from .modules import *
from .hr import *
from .finance import *
from .ai import *
from .documents import *
from .onboarding import *
from .inventory import *
from .bulk import *
from .chat import *
from .reports import *
from .settings import *
from .sa_views import SuperAdminClientsView, SuperAdminImpersonateView
from .resume_views import DownloadResumeView


# ==========================================
# DASHBOARD TEMPLATE VIEWS (For Frontend)
# ==========================================

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class LandingPageView(TemplateView):
    """Landing page with CSRF cookie enabled for payment forms"""
    template_name = "index.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class LoginPageView(TemplateView):
    template_name = "login.html"

class AdminDashboardTemplateView(TemplateView):
    template_name = "dashboard/admin.html"

class SuperAdminDashboardTemplateView(TemplateView):
    template_name = "dashboard/super_admin.html"

class SuperAdminSubscriptionView(TemplateView):
    template_name = "dashboard/super_admin_subscription.html"

class TeacherDashboardTemplateView(TemplateView):
    template_name = "dashboard/teacher.html"

class StudentDashboardTemplateView(TemplateView):
    template_name = "dashboard/student.html"

class ParentDashboardTemplateView(TemplateView):
    template_name = "dashboard/parent.html"

class DemoPageView(TemplateView):
    template_name = "demo.html"

# Legal Pages
class PrivacyPolicyView(TemplateView):
    template_name = "legal/privacy-policy.html"

class TermsOfServiceView(TemplateView):
    template_name = "legal/terms-of-service.html"

class RefundPolicyView(TemplateView):
    template_name = "legal/refund-policy.html"

class DeveloperProfileView(TemplateView):
    template_name = "developer.html"

class ResumeView(TemplateView):
    template_name = "resume.html"

# ==========================================
# DASHBOARD API VIEWS (Data Aggregation)
# ==========================================

class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'student_profile'):
            return Response({"error": "User does not have a student profile"}, status=403)
            
        student = request.user.student_profile
        owner = get_owner_user(request.user)
        
        # 1. Profile Data
        student_data = {
            "id": student.id,
            "name": student.name,
            "grade": student.student_class or student.grade,
            "roll_no": student.roll_number,
            "dob": student.dob,
            "phone": student.parents_phone,
            "photo_url": request.build_absolute_uri(student.photo.url) if student.photo else None
        }

        # 2. Attendance Stats
        attendance_count = Attendence.objects.filter(student=student, is_present=True).count()
        total_days = Attendence.objects.filter(student=student).count()
        attendance_percentage = int((attendance_count / total_days * 100)) if total_days > 0 else 0
        
        # 3. Recent Notifications
        notifications = Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient_type='STUDENT') | Q(recipient_type='ALL')
        ).filter(created_by=owner).order_by('-created_at')[:5]
        
        notif_data = [{
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "created_at": n.created_at
        } for n in notifications]

        # 4. Payments/Fees
        payments = Payment.objects.filter(student=student).order_by('-due_date')
        total_due = Payment.objects.filter(student=student, status__in=['PENDING', 'OVERDUE']).aggregate(Sum('amount'))['amount__sum'] or 0
        
        payment_data = {
            "total_due": float(total_due),
            "payments": PaymentSerializer(payments[:10], many=True).data
        }

        # 5. Results (Grades)
        grades = Grade.objects.filter(student=student).select_related('exam')[:5]
        results_data = [{
            "exam": g.exam.name,
            "subject": g.exam.subject.name if g.exam.subject else "General",
            "date": g.exam.exam_date,
            "percentage": int(g.percentage),
            "status": g.status
        } for g in grades]

        # 6. Routine (Today)
        # Assuming day_of_week is MON, TUE etc.
        day_map = {0:'MON', 1:'TUE', 2:'WED', 3:'THU', 4:'FRI', 5:'SAT', 6:'SUN'}
        today_code = day_map[timezone.now().weekday()]
        
        routine_qs = ClassRoutine.objects.filter(
            Q(batch__enrollments__student=student) | Q(grade=student.grade),
            day_of_week=today_code
        ).order_by('start_time')
        
        routine_data = [{
            "time": r.start_time.strftime('%I:%M %p'),
            "subject": r.subject,
            "teacher": r.teacher_name,
            "room": r.room_number
        } for r in routine_qs]

        # 7. Assignments
        assignments = LMSAssignment.objects.filter(
            Q(grade_class=student.student_class) | Q(grade_class=str(student.grade))
        ).order_by('-due_date')[:5]
        
        # Cross check with submissions
        submissions = AssignmentSubmission.objects.filter(student=student).values_list('assignment_id', flat=True)
        
        assignment_data = []
        for a in assignments:
            status = 'SUBMITTED' if a.id in submissions else 'PENDING'
            marks = 0
            if status == 'SUBMITTED':
                sub = AssignmentSubmission.objects.get(student=student, assignment=a)
                marks = sub.marks_obtained or 0
                
            assignment_data.append({
                "id": a.id,
                "title": a.title,
                "subject": a.subject.name,
                "due_date": a.due_date,
                "status": status,
                "marks": float(marks)
            })

        # 8. Diary
        diary = StudentDiary.objects.filter(
            Q(batch__enrollments__student=student) | Q(grade_class=str(student.grade))
        ).order_by('-created_at')[:5]
        
        diary_data = [{
            "title": d.task_title,
            "description": d.description,
            "subject": d.subject.name,
            "due_date": d.due_date
        } for d in diary]

        # 9. Live Classes
        live_classes = LiveClass.objects.filter(
            Q(batch__enrollments__student=student) | Q(grade=str(student.grade)),
            start_time__gte=timezone.now(),
            is_active=True
        ).order_by('start_time')[:4]
        
        live_data = [{
            "title": c.title,
            "instructor": c.teacher.get_full_name() or c.teacher.username,
            "platform": c.platform,
            "start_time": c.start_time,
            "duration": c.duration_minutes,
            "url": c.meeting_url
        } for c in live_classes]

        return Response({
            "student": student_data,
            "attendance": {
                "attendance_percentage": attendance_percentage,
                "total_days": total_days,
                "present_days": attendance_count
            },
            "notifications": notif_data,
            "payments": payment_data,
            "results": results_data,
            "routine": routine_data,
            "assignments": assignment_data,
            "diary": diary_data,
            "live_classes": live_data
        })

class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        owner = get_owner_user(request.user)
        
        # 1. My Batches
        my_batches = Batch.objects.filter(primary_teacher=user, is_active=True)
        batch_ids = my_batches.values_list('id', flat=True)
        
        # 2. Total Students
        total_students = Enrollment.objects.filter(batch_id__in=batch_ids, status='ACTIVE').count()
        
        # 3. Attendance Today
        today = timezone.now().date()
        present_today = Attendence.objects.filter(
            student__enrollments__batch_id__in=batch_ids,
            date=today,
            is_present=True
        ).distinct().count()
        
        # 4. Classes Today
        classes_today = ClassRoutine.objects.filter(
            batch_id__in=batch_ids,
            day_of_week=timezone.now().strftime('%a').upper()
        ).count()

        return Response({
            "stats": {
                "total_students": total_students,
                "present_today": present_today,
                "classes_today": classes_today,
                "batch_count": my_batches.count()
            },
            "batches": BatchSerializer(my_batches, many=True).data
        })

class ParentDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Parents are Users with role='PARENT' linked to students via Student.parent
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'PARENT':
             return Response({"error": "Access Denied"}, status=403)
             
        children = Student.objects.filter(parent=request.user)
        
        data = []
        for child in children:
            # Attendance
            attendance_count = Attendence.objects.filter(student=child, is_present=True).count()
            total_days = Attendence.objects.filter(student=child).count()
            attendance_pct = int((attendance_count / total_days * 100)) if total_days > 0 else 0
            
            # Fees
            pending_fees = Payment.objects.filter(student=child, status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
            
            data.append({
                "student": StudentSerializer(child, context={'request': request}).data,
                "attendance_pct": attendance_pct,
                "pending_fees": pending_fees
            })
            
        return Response(data)

class DashboardStatsView(APIView):
    """
    Main Admin Dashboard Stats
    Sync'ed with admin.js requirements.
    """
    permission_classes = [IsAuthenticated]

    @cache_api_response(timeout=300, key_prefix='dashboard_stats')
    def get(self, request):
        user = request.user
        owner = get_owner_user(user)

        # Basic Stats
        students_count = Student.objects.filter(created_by=owner).count()
        teachers_count = Employee.objects.filter(created_by=owner).count()
        
        # Financials
        total_revenue = Payment.objects.filter(
            student__created_by=owner, 
            status='PAID'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        pending_fees = Payment.objects.filter(
            student__created_by=owner, 
            status__in=['PENDING', 'OVERDUE', 'PENDING_VERIFICATION']
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Attendance Today
        today = timezone.now().date()
        present_count = Attendence.objects.filter(
            student__created_by=owner,
            date=today,
            is_present=True
        ).count()
        
        attendance_percentage = int((present_count / students_count * 100)) if students_count > 0 else 0
        
        # ROI Summary for dashboard
        total_expenses = InstitutionExpense.objects.filter(created_by=owner).aggregate(Sum('amount'))['amount__sum'] or 0
        net_profit = float(total_revenue) - float(total_expenses)
        
        # Academic Risk
        students_at_risk = Grade.objects.filter(student__created_by=owner).values(
            'student__id'
        ).annotate(avg=Avg('marks_obtained')).filter(avg__lt=40).count()

        # --- GAMIFICATION LOGIC ---
        streak_info = {"current_streak": 0, "status": "inactive"}
        if hasattr(user, 'profile'):
            profile = user.profile
            today = timezone.now().date()
            last_date = profile.last_activity_date
            
            if last_date == today:
                # Already active today
                pass
            elif last_date == today - timezone.timedelta(days=1):
                # Consecutive day
                profile.streak_count += 1
                profile.last_activity_date = today
                profile.save()
            else:
                # Streak broken or new
                profile.streak_count = 1
                profile.last_activity_date = today
                profile.save()
            
            streak_info = {
                "current_streak": profile.streak_count,
                "status": "active" if profile.streak_count > 0 else "inactive"
            }

        return Response({
            "students_count": students_count,
            "teachers_count": teachers_count,
            "attendance_percentage": attendance_percentage,
            "pending_fees": float(pending_fees),
            "roi_summary": {
                "revenue": float(total_revenue),
                "expense": float(total_expenses),
                "profit": net_profit
            },
            "risk_summary": {
                "students_at_risk": students_at_risk
            },
            "streak_info": streak_info,
            "recent_activity": AuditLogSerializer(AuditLog.objects.filter(created_by=owner).order_by('-created_at')[:5], many=True).data
        })

class SuperAdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"error": "Access Denied"}, status=403)
            
        total_clients = UserProfile.objects.filter(role__in=['CLIENT', 'ADMIN']).count()
        total_revenue = ClientSubscription.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        active_subs = ClientSubscription.objects.filter(status='ACTIVE').count()
        
        recent_clients = UserProfile.objects.filter(role='CLIENT').order_by('-created_at')[:5]
        
        return Response({
            "total_clients": total_clients,
            "total_revenue": total_revenue,
            "active_subscriptions": active_subs,
            "recent_clients": UserProfileSerializer(recent_clients, many=True).data
        })

class SuperAdminAdvancedDashboardView(APIView):
     permission_classes = [permissions.IsAdminUser]
     def get(self, request):
         return Response({"message": "Advanced Stats Placeholder"})


# ==========================================
# MISCELLANEOUS & UTILITY VIEWS
# ==========================================





# SEO / PWA Views
def robots_txt(request):
    from django.conf import settings
    site_url = getattr(settings, 'SITE_URL', 'https://yashamishra.pythonanywhere.com').rstrip('/')
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /schema/",
        "Disallow: /swagger/",
        "Disallow: /media/",
        "Allow: /",
        "",
        f"Sitemap: {site_url}/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def sitemap_xml(request):
    from datetime import date
    from django.conf import settings
    today = date.today().isoformat()
    domain = getattr(settings, 'SITE_URL', 'https://yashamishra.pythonanywhere.com').rstrip('/')

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- ==================== HOME PAGE ==================== -->
  <url>
    <loc>{domain}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
    <image:image>
      <image:loc>{domain}/static/images/yash_profile.jpg</image:loc>
      <image:title>Y.S.M AI - Best School Management System by Yash Ankush Mishra, Naugachiya, Rangra, Bhagalpur, Bihar</image:title>
      <image:caption>Y.S.M AI Education ERP by Yash Ankush Mishra - Developer from Naugachiya, Rangra, Bhagalpur, Katihar, Bihar. Serving Patna, Mumbai, Jaipur. India's #1 School, Coaching &amp; Institute Management System.</image:caption>
    </image:image>
  </url>

  <!-- ==================== DEVELOPER PROFILE (MOST IMPORTANT FOR RANKING) ==================== -->
  <url>
    <loc>{domain}/developer/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
    <xhtml:link rel="alternate" hreflang="hi" href="{domain}/developer/"/>
    <xhtml:link rel="alternate" hreflang="en" href="{domain}/developer/"/>
    <image:image>
      <image:loc>{domain}/static/images/yash_profile.jpg</image:loc>
      <image:title>Yash Ankush Mishra - Top Software Developer from Naugachiya, Rangra, Bhagalpur, Katihar, Bihar | YSM AI Founder</image:title>
      <image:caption>Yash Ankush Mishra (Yash A Mishra) - Founder of YSM AI, Full Stack Developer &amp; AI Architect from Naugachiya, Rangra, Bhagalpur, Katihar, Bihar. Expert in Python, Django, React, AI/ML.</image:caption>
    </image:image>
    <image:image>
      <image:loc>{domain}/static/images/yash_profile.jpg</image:loc>
      <image:title>Naugachiya Developer - Yash Ankush Mishra | Best Developer Bihar | YSM AI</image:title>
      <image:caption>Naugachiya ka developer Yash Ankush Mishra - Bihar ka top software developer jo Naugachiya, Rangra, Bhagalpur, Katihar, Kuhari mein services deta hai.</image:caption>
    </image:image>
  </url>

  <!-- ==================== RESUME ==================== -->
  <url>
    <loc>{domain}/resume/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
    <image:image>
      <image:loc>{domain}/static/images/yash_profile.jpg</image:loc>
      <image:title>Yash Ankush Mishra Resume 2026 - Software Architect CV | Developer from Naugachiya, Rangra, Bihar</image:title>
      <image:caption>Resume and CV of Yash Ankush Mishra, Chief Software Architect from Naugachiya, Rangra, Bhagalpur, Bihar. Founder of YSM AI. MCA from Bengaluru University. Serving Katihar, Patna, Mumbai, Jaipur.</image:caption>
    </image:image>
  </url>

  <!-- ==================== AI CHAT ==================== -->
  <url>
    <loc>{domain}/ai-chat/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- ==================== RANGRAGO ==================== -->
  <url>
    <loc>{domain}/rangrago/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
    <image:image>
      <image:loc>{domain}/static/images/yash_profile.jpg</image:loc>
      <image:title>RangraGo - App by Yash Ankush Mishra from Rangra, Naugachiya, Bhagalpur, Bihar</image:title>
      <image:caption>RangraGo application created by Yash Ankush Mishra - developer from Rangra, near Naugachiya, Bhagalpur, Bihar, India.</image:caption>
    </image:image>
  </url>

  <!-- ==================== GENERAL PAGES ==================== -->
  <url>
    <loc>{domain}/demo/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>{domain}/login/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>{domain}/privacy-policy/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>{domain}/terms-of-service/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>{domain}/refund-policy/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.4</priority>
  </url>

</urlset>"""
    return HttpResponse(xml_content, content_type='application/xml')


def google_verification(request):
    return HttpResponse("google-site-verification: google7ec15807e3134773.html", content_type="text/plain")

def service_worker(request):
    return HttpResponse("console.log('SW Loaded');", content_type="application/javascript")

# Verification Views
class VerifyIdentityView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    def post(self, request):
        from ..models import UserProfile
        name = request.data.get('name')
        if not name:
            return Response({"exists": False, "error": "Name required"}, status=200)
            
        # Sovereign Bypass for Super-Admin Access
        if name.lower() in ['superadmin', 'admin', 'ysm', 'y.s.m', 'central command']:
            return Response({
                "exists": True,
                "name": "Y.S.M CENTRAL COMMAND",
                "welcome_msg": "Sovereign Identity Confirmed. Accessing Central Command Unit.",
                "redirect": "/login/?inst=superadmin"
            })

        profile = UserProfile.objects.filter(institution_name__iexact=name).first()
        
        if profile:
            return Response({
                "exists": True,
                "name": profile.institution_name,
                "welcome_msg": f"Identity confirmed for {profile.institution_name}. Connecting to hub.",
                "redirect": f"/login/?inst={profile.institution_name}"
            })
        else:
            return Response({
                "exists": False, 
                "error": "Institution not found in central registry."
            })

class CheckPublicAvailabilityView(APIView):
     permission_classes = [permissions.AllowAny]
     authentication_classes = []
     def get(self, request):
          return Response({"available": True})
          
     def post(self, request):
          from django.contrib.auth.models import User
          from ..models import UserProfile, DemoRequest
          from django.db.models import Q
          
          email = request.data.get('email')
          phone = request.data.get('phone')
          
          if email:
               # 1. Check if user already exists
               user = User.objects.filter(Q(email=email) | Q(username=email)).first()
               if user:
                    role = getattr(user, 'profile', None).role if hasattr(user, 'profile') else 'USER'
                    return Response({
                         "available": False, 
                         "error": f"This email is already registered as a {role.lower()}. Please use a different email for an institutional account."
                    }, status=200)
               
               # 2. Check if there's a pending demo/subscription request
               if DemoRequest.objects.filter(email=email).exists():
                    return Response({
                         "available": False, 
                         "error": "This email has an active demo or subscription request. Our team will contact you soon."
                    }, status=200)
               
          if phone:
               # 3. Check if phone is linked to any profile
               if UserProfile.objects.filter(phone=phone).exists():
                    return Response({
                         "available": False, 
                         "error": "This phone number is already associated with an existing account."
                    }, status=200)
                    
               # 4. Check if phone is in a demo request
               if DemoRequest.objects.filter(phone=phone).exists():
                    return Response({
                         "available": False, 
                         "error": "This phone number is already associated with an active request."
                    }, status=200)

          return Response({"available": True})

class RequestPasswordResetView(APIView):
     permission_classes = [permissions.AllowAny]
     authentication_classes = []
     from student.throttling import PasswordResetRateThrottle
     throttle_classes = [PasswordResetRateThrottle]

     def post(self, request):
         from datetime import timedelta
         from django.conf import settings
         from django.core.mail import send_mail
         from ..models import PasswordResetOTP, UserProfile

         identifier = (request.data.get('identifier') or '').strip()
         if not identifier:
             return Response({"error": "Identity handle is required"}, status=400)

         user = None
         if '@' in identifier:
             user = User.objects.filter(email__iexact=identifier).first()
         if not user:
             profile = UserProfile.objects.filter(phone=identifier).first()
             if profile:
                 user = profile.user

         if not user:
             return Response({"error": "No portal found with this handle"}, status=404)

         PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
         otp = ''.join(random.choices(string.digits, k=4))
         PasswordResetOTP.objects.create(
             user=user,
             otp_code=otp,
             identifier=identifier,
             expires_at=timezone.now() + timedelta(minutes=10)
         )

         if user.email:
             try:
                 send_mail(
                     subject="Y.S.M Security Recovery OTP",
                     message=f"Your OTP is {otp}. It is valid for 10 minutes.",
                     from_email=settings.DEFAULT_FROM_EMAIL,
                     recipient_list=[user.email],
                     fail_silently=True
                 )
             except Exception:
                 pass

         return Response({"message": "Protocol key transmitted successfully."}, status=200)

class VerifyAndResetPasswordView(APIView):
     permission_classes = [permissions.AllowAny]
     authentication_classes = []
     def post(self, request):
         from ..models import PasswordResetOTP

         identifier = (request.data.get('identifier') or '').strip()
         otp = (request.data.get('otp') or '').strip()
         new_password = request.data.get('new_password') or ''

         if not identifier or not otp or not new_password:
             return Response({"error": "Incomplete data synchronization."}, status=400)

         otp_record = PasswordResetOTP.objects.filter(
             identifier=identifier,
             otp_code=otp,
             is_used=False
         ).order_by('-created_at').first()

         if not otp_record or not otp_record.is_valid():
             return Response({"error": "Invalid or Expired Protocol Key."}, status=400)

         user = otp_record.user
         user.set_password(new_password)
         user.save()

         otp_record.is_used = True
         otp_record.save(update_fields=['is_used'])

         return Response({
             "message": "Security Protocol Overwritten Successfully.",
             "username": user.username,
             "hint": "Please use your new password to log in."
         }, status=200)

class CheckUsernameView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    def post(self, request):
        username = request.data.get('username')
        exists = User.objects.filter(username=username).exists()
        return Response({"exists": exists})

class CheckInstitutionView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    def post(self, request):
        name = request.data.get('name')
        exists = UserProfile.objects.filter(institution_name__iexact=name).exists()
        return Response({"exists": exists})

class SubscriptionStatusView(ClientSubscriptionView):
    """Alias for ClientSubscriptionView required by api.js"""
    pass
