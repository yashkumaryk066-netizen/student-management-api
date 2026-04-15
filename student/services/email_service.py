from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from student.security_utils import validate_email_safe

def send_safe_email(recipient, subject, body, html_body=None, attachments=None):
    """
    SECURITY FIX #11: Safe email sending with header injection protection
    """
    if not validate_email_safe(recipient):
        logger.error(f"❌ Blocked sending email to invalid/insecure recipient: {recipient}")
        return False
        
    # Sanitize subject (remove newlines to prevent header injection)
    subject = subject.replace('\n', ' ').replace('\r', ' ').strip()[:200]
    
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient]
        )
        if html_body:
            email.body = html_body
            email.content_subtype = "html"
            
        if attachments:
            for name, content, mime in attachments:
                email.attach(name, content, mime)
                
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"❌ Safe Email Error: {str(e)}")
        return False
def send_credentials_with_invoice(user, password, plan, invoice_pdf):
    """Legacy/Internal helper for sending credentials with invoice"""
    display_plan = {
        'COACHING': 'Coaching Management System (CMS)',
        'SCHOOL': 'Modern School Management System (SMS)',
        'INSTITUTE': 'Enterprise Institute/University ERP'
    }.get(plan, f"{plan} Plan")

    subject = f"Y.S.M Advance Education — {display_plan} Activated"
    
    if password:
        body = f"""
Greetings from Y.S.M Intelligence,

We are pleased to inform you that your {display_plan} has been successfully activated on our secure architecture.

Your enterprise-grade management portal is now live with full administrative privileges.

ACCESS DETAILS:
------------------------------------------
Portal URL: {settings.SITE_URL}/login/
Username:   {user.username}
Password:   {password}
------------------------------------------

Plan Features Activated:
- Full Module Access (as per {plan} specifications)
- Advance Level Data Security Protocol
- Cloud Instance Synchronization
- Official PDF Invoicing and Reporting

ATTACHMENT:
Please find your official tax invoice attached.

Our AI-driven support system is available 24/7 should you require technical assistance.

Best Regards,

Yash A Mishra
Software Architect | Y.S.M Advance Education System
Telepathy Infotech Intelligence
"""
    else:
        body = f"""
Greetings from Y.S.M Intelligence,

Your {display_plan} subscription has been successfully renewed.

Your current system access, configurations, and data isolation protocols remain intact.

RENEWAL CONFIRMATION:
------------------------------------------
Portal URL: {settings.SITE_URL}/login/
Status:     ACTIVE
------------------------------------------

ATTACHMENT:
Your official renewal tax invoice is attached for your records.

Thank you for continuing your journey with Y.S.M Intelligence.

Best Regards,

Yash A Mishra
Software Architect | Y.S.M Advance Education System
Telepathy Infotech Intelligence
"""

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )

        if invoice_pdf:
            email.attach(
                filename=f"Invoice_{plan}_Plan.pdf",
                content=invoice_pdf.read(),
                mimetype="application/pdf"
            )

        email.send(fail_silently=False)
        logger.info(f"✅ Invoice Email Sent to {user.email}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Failed to send invoice email: {str(e)}")
        return False

def send_approval_email(email, username, password=None, plan_type='COACHING', amount='0', payment_id=None, institution_type=None, invoice_pdf=None, user=None):
    """
    Elite Level Approval Email with HTML Template and Invoice Attachment
    """
    try:
        if not validate_email_safe(email):
            return False

        display_name = email.split('@')[0].title()
        currency = "₹"
        login_url = f"{settings.SITE_URL}/login/"
        is_new_credentials = bool(password)
        
        if is_new_credentials:
            access_block = f"""
                <div style="background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); padding: 25px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #f59e0b; margin-top: 0;">🗝️ SECURE ACCESS KEYS</h3>
                    <p style="margin: 10px 0;"><strong>Username:</strong> <code style="color: #a78bfa;">{username}</code></p>
                    <p style="margin: 10px 0;"><strong>Password:</strong> <code style="color: #a78bfa;">{password}</code></p>
                    <p style="margin: 10px 0;"><strong>Access URL:</strong> <a href="{login_url}" style="color: #3b82f6;">{login_url}</a></p>
                </div>
            """
            guidance_note = """
                <strong>Note:</strong> We recommend changing your primary access key (password) immediately upon first entry.
            """
        else:
            access_block = f"""
                <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); padding: 25px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #3b82f6; margin-top: 0;">🔐 ACCESS DETAILS</h3>
                    <p style="margin: 10px 0;"><strong>Username:</strong> <code style="color: #a78bfa;">{username}</code></p>
                    <p style="margin: 10px 0;"><strong>Password:</strong> Use your existing password</p>
                    <p style="margin: 10px 0;"><strong>Access URL:</strong> <a href="{login_url}" style="color: #3b82f6;">{login_url}</a></p>
                </div>
            """
            guidance_note = """
                <strong>Note:</strong> If you forgot your password, use the password reset option on the login page.
            """
        
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        from datetime import datetime

        # Context for the new premium template
        context = {
            'institution_name': getattr(getattr(user, 'profile', None), 'institution_name', None) or username.title(),
            'plan_type': plan_type,
            'email': email,
            'amount': amount,
            'transaction_id': payment_id or "TXN-INIT",
            'date': datetime.now().strftime('%d %b, %Y %I:%M %p'),
            'is_new_user': bool(password),
            'username': username,
            'password': password,
            'login_url': f"{settings.SITE_URL}/login/"
        }

        subject = "✅ Access Authorized: Your Y.S.M Intelligence Node is Live"
        html_content = render_to_string('emails/invoice_subscription.html', context)
        plain_message = strip_tags(html_content)


        email_obj = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_obj.content_subtype = "html"

        if invoice_pdf:
            invoice_pdf.seek(0)
            email_obj.attach(
                filename=f"Invoice_{username}.pdf",
                content=invoice_pdf.read(),
                mimetype="application/pdf"
            )

        email_obj.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Approval Email Error: {str(e)}")
        return False

def send_payment_received_email(email, institution_name, plan_type, amount, utr):
    """
    Elite Level Notification for Payment Receipt (Verification Pending)
    """
    try:
        subject = "📥 Subscription Received: Verification in Progress"
        
        html_content = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #1e293b;">
            <div style="padding: 40px; background: linear-gradient(135deg, #1e293b, #0f172a); text-align: center; border-bottom: 2px solid #3b82f6;">
                <h1 style="color: #3b82f6; margin: 0; letter-spacing: 2px;">PAYMENT LOGGED</h1>
                <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 10px;">Verification Sequence Initialized</p>
            </div>
            <div style="padding: 40px;">
                <p>Hello <strong>{institution_name}</strong>,</p>
                <p>We have successfully received your subscription request for the <strong>{plan_type}</strong> plan. Our financial curators are currently verifying your transaction.</p>
                
                <div style="background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); padding: 25px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #3b82f6; margin-top: 0;">📊 TRANSACTION DETAILS</h3>
                    <p style="margin: 10px 0;"><strong>UTR / Ref:</strong> <code style="color: #60a5fa;">{utr}</code></p>
                    <p style="margin: 10px 0;"><strong>Amount:</strong> <span style="color: #10b981;">₹{amount}</span></p>
                    <p style="margin: 10px 0;"><strong>Plan:</strong> {plan_type}</p>
                </div>

                <div style="padding: 15px; background: rgba(245, 158, 11, 0.1); border-radius: 8px; font-size: 0.85rem; color: #f59e0b; margin: 25px 0;">
                    ⏳ <strong>Verification Timeline:</strong> Most activations are completed within 2 to 4 hours. You will receive your access credentials via email once authorized.
                </div>

                <p style="color: #94a3b8; font-size: 0.85rem;">
                    Thank you for choosing Y.S.M Intelligence. Your institution is one step closer to the future of education.
                </p>
            </div>
            <div style="padding: 20px; background: rgba(0,0,0,0.2); text-align: center; font-size: 0.75rem; color: #475569;">
                &copy; 2026 Y.S.M Intelligence | Telepathy Infotech
            </div>
        </div>
        """

        email_obj = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_obj.content_subtype = "html"
        email_obj.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Payment Received Email Error: {str(e)}")
        return False

def send_rejection_email(email, plan_type, amount, payment_id, reason="Verification Failure", invoice_pdf=None):
    """
    Elite Level Rejection Email
    """
    try:
        display_name = email.split('@')[0].title()
        currency = "₹"
        
        subject = "⚠️ Security Update: Subscription Protocol Terminated"
        
        html_content = f"""
        <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #f8fafc; border-radius: 12px; overflow: hidden; border: 1px solid #ef4444;">
            <div style="padding: 40px; background: rgba(239, 68, 68, 0.1); text-align: center; border-bottom: 2px solid #ef4444;">
                <h1 style="color: #ef4444; margin: 0;">PROTOCOL DENIED</h1>
                <p style="color: #94a3b8; margin-top: 10px;">Verification Sequence Aborted</p>
            </div>
            <div style="padding: 40px;">
                <p>Greetings <strong>{display_name}</strong>,</p>
                <p>We regret to inform you that your request for the <strong>{plan_type}</strong> protocol has been declined by the system curators.</p>
                
                <div style="background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2); padding: 25px; border-radius: 10px; margin: 25px 0;">
                    <h3 style="color: #ef4444; margin-top: 0;">🔍 REASONING</h3>
                    <p style="color: #f8fafc;">{reason}</p>
                </div>

                <div style="background: rgba(255,255,255,0.03); padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 5px 0; font-size: 0.9rem;"><strong>Transaction ID:</strong> {payment_id}</p>
                    <p style="margin: 5px 0; font-size: 0.9rem;"><strong>Amount Logged:</strong> {currency}{amount}</p>
                </div>

                <p style="color: #94a3b8; font-size: 0.85rem;">
                    If you believe this is a technical error, please contact the High-Altitude Support Terminal or resubmit your request with valid credentials and UTR proof.
                </p>
            </div>
            <div style="padding: 20px; background: rgba(0,0,0,0.2); text-align: center; font-size: 0.75rem; color: #475569;">
                &copy; 2026 Y.S.M Intelligence System
            </div>
        </div>
        """

        email_obj = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_obj.content_subtype = "html"
        if invoice_pdf:
            invoice_pdf.seek(0)
            email_obj.attach(
                filename=f"Invoice_VOID_{payment_id}.pdf",
                content=invoice_pdf.read(),
                mimetype="application/pdf"
            )

        email_obj.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Rejection Email Error: {str(e)}")
        return False

def send_student_welcome_email(email, student_name, username, password, institution_name, institution_type, invoice_pdf=None, invoice_pdf_bytes=None):
    """
    Elite Level Professional Student Admission Welcome Email
    Supports both file-like objects (invoice_pdf) and raw bytes (invoice_pdf_bytes) for async tasks.
    """
    try:
        # Compatibility handling for threaded tasks
        import io
        if invoice_pdf_bytes and not invoice_pdf:
            invoice_pdf = io.BytesIO(invoice_pdf_bytes)
        login_url = f"{settings.SITE_URL}/login/"
        subject = f"✨ Welcome to {institution_name} — Your Academic Portal is Active"
        
        # Color coding based on institution type
        accent_color = "#3b82f6" # Blue for School
        if institution_type == 'COACHING': accent_color = "#10b981" # Green
        if institution_type == 'INSTITUTE': accent_color = "#8b5cf6" # Purple

        html_content = f"""
        <div style="font-family: 'Inter', 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; color: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
            <div style="padding: 50px 40px; background: {accent_color}; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px;">Admission Confirmed</h2>
                <p style="margin-top: 10px; opacity: 0.9; font-size: 16px;">Welcome to the next generation of digital learning.</p>
            </div>
            
            <div style="padding: 40px;">
                <p style="font-size: 18px; color: #0f172a;">Dear <strong>{student_name}</strong>,</p>
                <p style="line-height: 1.6; color: #475569;">
                    Congratulations! Your admission at <strong>{institution_name}</strong> has been successfully processed. 
                    You now have full access to your personalized student portal where you can track attendance, download resources, and view your performance.
                </p>
                
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 30px; border-radius: 12px; margin: 30px 0;">
                    <h3 style="color: {accent_color}; margin-top: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">🔐 Secure Login Credentials</h3>
                    <div style="margin: 20px 0;">
                        <p style="margin: 10px 0; font-family: monospace; font-size: 15px;"><strong>Username:</strong> {username}</p>
                        <p style="margin: 10px 0; font-family: monospace; font-size: 15px;"><strong>Password:</strong> {password}</p>
                    </div>
                    <a href="{login_url}" style="display: inline-block; background: {accent_color}; color: white; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 14px; text-transform: uppercase;">Access Student Portal</a>
                </div>

                <div style="border-left: 4px solid {accent_color}; padding-left: 20px; margin: 30px 0;">
                    <p style="font-size: 14px; color: #64748b; font-style: italic;">
                        "The beautiful thing about learning is that no one can take it away from you."
                    </p>
                </div>

                <p style="font-size: 14px; color: #475569;">
                    {'Please find your digital admission invoice attached for your records.' if invoice_pdf else ''} 
                    If you face any issues while logging in, please contact the institution's administration desk.
                </p>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #f1f5f9;">
                    <p style="margin: 0; font-weight: 700; color: #0f172a;">{institution_name}</p>
                    <p style="margin: 4px 0 0; font-size: 12px; color: #94a3b8;">Digitally Secured by Y.S.M Advance Education System</p>
                </div>
            </div>
            
            <div style="padding: 20px; background: #f8fafc; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #f1f5f9;">
                &copy; 2026 Y.S.M Intelligence | Telepathy Infotech
            </div>
        </div>
        """

        email_obj = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_obj.content_subtype = "html"

        if invoice_pdf:
            invoice_pdf.seek(0)
            email_obj.attach(
                filename=f"Admission_Invoice_{student_name.replace(' ', '_')}.pdf",
                content=invoice_pdf.read(),
                mimetype="application/pdf"
            )

        email_obj.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"❌ Student Welcome Email Error: {str(e)}")
        return False

def send_parent_welcome_email(email, parent_name, student_name, username, password, institution_name, institution_type):
    """
    Elite Level Professional Parent Portal Access Email
    """
    try:
        login_url = f"{settings.SITE_URL}/login/"
        subject = f"👨‍👩‍👧‍👦 Parent Access Activated: Monitoring for {student_name}"
        
        # Color coding
        accent_color = "#3b82f6" 
        if institution_type == 'COACHING': accent_color = "#10b981"
        if institution_type == 'INSTITUTE': accent_color = "#8b5cf6"

        html_content = f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; color: #1e293b; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0,0,0,0.05);">
            <div style="padding: 40px; background: #1e293b; text-align: left; color: white;">
                <h2 style="margin: 0; font-size: 20px;">Parent Observation Portal</h2>
                <p style="margin-top: 5px; opacity: 0.8; font-size: 14px;">Securely monitor <strong>{student_name}'s</strong> academic journey at {institution_name}.</p>
            </div>
            
            <div style="padding: 40px;">
                <p>Dear <strong>{parent_name}</strong>,</p>
                <p style="line-height: 1.6; color: #475569;">
                    Your Parent Account has been successfully provisioned. You can now log in to the portal to track attendance, review exam results, and manage fee payments for <strong>{student_name}</strong>.
                </p>
                
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 25px; border-radius: 12px; margin: 25px 0;">
                    <h3 style="color: {accent_color}; margin-top: 0; font-size: 13px; text-transform: uppercase;">🗝️ Parent Credentials</h3>
                    <div style="margin: 15px 0;">
                        <p style="margin: 8px 0; font-family: monospace;"><strong>Username:</strong> {username}</p>
                        <p style="margin: 8px 0; font-family: monospace;"><strong>Password:</strong> {password}</p>
                    </div>
                    <a href="{login_url}" style="display: inline-block; background: {accent_color}; color: white; padding: 12px 25px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 13px;">Login to Parent Dashboard</a>
                </div>

                <div style="background: rgba(59, 130, 246, 0.05); padding: 20px; border-radius: 8px; font-size: 13px; color: #1e40af;">
                    <strong>Tip:</strong> You can see real-time updates of class routines and important notices directly from the dashboard.
                </div>

                <div style="margin-top: 40px; border-top: 1px solid #f1f5f9; padding-top: 20px; font-size: 12px; color: #94a3b8;">
                    This is an automated security protocol from {institution_name}. 
                    Please do not share these credentials with anyone.
                </div>
            </div>
        </div>
        """

        email_obj = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_obj.content_subtype = "html"
        email_obj.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"❌ Parent Welcome Email Error: {str(e)}")
        return False

def send_leave_status_email(student, leave_request, status, admin_remarks):
    """
    Notify student and parent about leave request approval/rejection
    """
    try:
        user_email = student.user.email if student.user else None
        parent_email = student.parent.email if student.parent else None
        
        recipients = []
        if user_email: recipients.append(user_email)
        if parent_email: recipients.append(parent_email)
        
        if not recipients:
            return False

        status_icon = "✅" if status == 'APPROVED' else "❌"
        subject = f"{status_icon} Leave Request {status.title()}: {student.name}"
        
        accent_color = "#10b981" if status == 'APPROVED' else "#ef4444"

        html_content = f"""
        <div style="font-family: 'Inter', sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; color: #1e293b; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden;">
            <div style="padding: 40px; background: {accent_color}; text-align: center; color: white;">
                <h2 style="margin: 0; font-size: 22px;">Leave Request {status.title()}</h2>
                <p style="margin-top: 5px; opacity: 0.9;">Application for {student.name}</p>
            </div>
            
            <div style="padding: 40px;">
                <div style="background: #f8fafc; padding: 25px; border-radius: 12px; margin-bottom: 25px;">
                    <p style="margin: 5px 0;"><strong>Period:</strong> {leave_request.start_date} to {leave_request.end_date}</p>
                    <p style="margin: 5px 0;"><strong>Type:</strong> {leave_request.leave_type}</p>
                    <p style="margin: 5px 0;"><strong>Reason:</strong> {leave_request.reason}</p>
                </div>

                <div style="border-left: 4px solid {accent_color}; padding-left: 20px; margin: 25px 0;">
                    <h3 style="color: {accent_color}; margin-top: 0; font-size: 14px; text-transform: uppercase;">Admin Remarks</h3>
                    <p style="color: #475569; font-style: italic;">"{admin_remarks or 'No specific remarks provided.'}"</p>
                </div>

                <p style="font-size: 14px; color: #94a3b8; margin-top: 40px; text-align: center;">
                    This is an automated update from the Student Management System.
                </p>
            </div>
        </div>
        """

        email_obj = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email_obj.content_subtype = "html"
        email_obj.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"❌ Leave Status Email Error: {str(e)}")
        return False
