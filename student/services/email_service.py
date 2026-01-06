from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_credentials_with_invoice(user, password, plan, invoice_pdf):
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
Portal URL: https://yashamishra.pythonanywhere.com/login/
Username:   {user.username}
Password:   {password}
------------------------------------------

Plan Features Activated:
- Full Module Access (as per {plan} specifications)
- Advance Level Data Security Protocol
- Cloud Instance Synchronization
- Official PDF Invoicing and Reporting

ATTACHMENT:
Please find your official tax invoice (INV-{user.id:05d}) attached.

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
Portal URL: https://yashamishra.pythonanywhere.com/login/
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

        # Attach PDF
        # invoice_pdf is a BytesIO object
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
