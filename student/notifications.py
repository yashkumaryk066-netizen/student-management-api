from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

import threading

def send_erp_notification(user, title, message, template_name=None, context=None):
    """
    Centralized Sovereign ERP Notification Engine.
    Sends professional, branded emails to users in a NON-BLOCKING way.
    """
    if not user.email:
        return False
        
    def _send():
        subject = f"🔔 {title}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ysmeducation.com')
        to = user.email
        
        # Branded Header & Footer
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
            <div style="background: #1e3a8a; padding: 20px; text-align: center; color: white;">
                <h1 style="margin: 0; font-size: 24px;">Y.S.M ADVANCE EDUCATION</h1>
            </div>
            <div style="padding: 30px; color: #1e293b; line-height: 1.6;">
                <h2 style="color: #1e3a8a;">{title}</h2>
                <p>Dear {user.username},</p>
                <p>{message}</p>
                {f'<div style="margin-top: 20px; padding: 15px; background: #f8fafc; border-radius: 8px;">{render_to_string(template_name, context)}</div>' if template_name else ''}
                <p style="margin-top: 30px;">Best Regards,<br/><strong>Institutional Management Team</strong></p>
            </div>
            <div style="background: #f1f5f9; padding: 15px; text-align: center; font-size: 12px; color: #64748b;">
                This is an official communication from your educational institution powered by Sovereign ERP.
            </div>
        </div>
        """
        
        text_content = strip_tags(html_content)
        
        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            logger.info(f"Successfully sent notification to {to}")
        except Exception as e:
            logger.error(f"Failed to send ERP notification to {to}: {str(e)}")

    # Launch in background thread
    threading.Thread(target=_send).start()
    return True
