from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_credentials_with_invoice(user, password, plan, invoice_pdf):
    subject = "Subscription Activated with Invoice"
    
    if password:
        body = f"""
Hello,

Your {plan} subscription has been successfully activated.

Login Details:
URL: https://yashamishra.pythonanywhere.com/dashboard/login
Username: {user.username}
Password: {password}

Please find your tax invoice attached with this email.

Regards,
NextGen ERP Team
"""
    else:
        body = f"""
Hello,

Your {plan} subscription has been successfully renewed.

Your login credentials remain the same.

Please find your tax invoice attached with this email.

Regards,
NextGen ERP Team
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
