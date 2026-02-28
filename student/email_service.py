"""
Y.S.M System - Email Service Utilities
Professional email notifications for approval/rejection
"""

from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Email configuration check
def is_email_configured():
    """Check if email backend is properly configured"""
    return bool(settings.EMAIL_HOST and settings.EMAIL_PORT)


def send_approval_email(email, username, password, plan_type, institution_type, amount, payment_id):
    """
    Send professional approval email with login credentials
    """
    try:
        institution_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        currency = getattr(settings, 'CURRENCY_SYMBOL', '$')
        login_url = f"{settings.FRONTEND_URL}/login/" if hasattr(settings, 'FRONTEND_URL') else "http://localhost:8000/login/"
        
        subject = "✅ Welcome to Y.S.M Education System - Account Activated!"
        
        message = f"""
Dear {institution_name},

Congratulations! Your subscription request has been APPROVED and your account is now ACTIVE.

🎉 Your Login Credentials:
━━━━━━━━━━━━━━━━━━━━━━━━
📧 Email/Username: {username}
🔑 Password: {password}
🌐 Login URL: {login_url}
━━━━━━━━━━━━━━━━━━━━━━━━

📦 Plan Details:
• Plan Type: {plan_type}
• Institution Type: {institution_type}
• Amount Paid: {currency}{amount}
• Payment ID: {payment_id}
• Activation Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

⚡ Quick Start Guide:
1. Visit {login_url}
2. Login with credentials above
3. Change your password (Settings → Security)
4. Complete your institution profile
5. Start adding students & staff

🔒 Security Recommendations:
• Change your password immediately after first login
• Enable two-factor authentication
• Never share your credentials

📞 Need Help?
• Support Email: support@ysm.education
• Documentation: {login_url}docs/
• Video Tutorials: {login_url}tutorials/

Thank you for choosing Y.S.M Education System!

Best Regards,
Y.S.M Team
Enterprise Education Management Platform

━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated email. Please do not reply.
"""
        
        # HTML version for better formatting
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f3f4f6; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .credentials {{ background: #f8fafc; border-left: 4px solid #3b82f6; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .btn {{ display: inline-block; background: #3b82f6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin: 10px 0; font-weight: 600; }}
        .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px; }}
        .info-box {{ background: #e0f2fe; border: 1px solid #3b82f6; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; font-size: 28px;">✅ Account Activated!</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Welcome to Y.S.M Education System</p>
        </div>
        
        <div class="content">
            <p>Dear <strong>{institution_name}</strong>,</p>
            <p>Congratulations! Your subscription request has been <strong style="color: #10b981;">APPROVED</strong> and your account is now active.</p>
            
            <div class="credentials">
                <h3 style="margin-top: 0; color: #1f2937;">🎉 Your Login Credentials</h3>
                <p><strong>📧 Email/Username:</strong> {username}</p>
                <p><strong>🔑 Password:</strong> <code style="background: #e5e7eb; padding: 4px 8px; border-radius: 4px;">{password}</code></p>
                <p><strong>🌐 Login URL:</strong> <a href="{login_url}" style="color: #3b82f6;">{login_url}</a></p>
                <a href="{login_url}" class="btn">Login Now →</a>
            </div>
            
            <div class="info-box">
                <h4 style="margin-top: 0; color: #1f2937;">📦 Plan Details</h4>
                <ul style="list-style: none; padding: 0;">
                    <li>• <strong>Plan Type:</strong> {plan_type}</li>
                    <li>• <strong>Institution Type:</strong> {institution_type}</li>
                    <li>• <strong>Amount Paid:</strong> {currency}{amount}</li>
                    <li>• <strong>Payment ID:</strong> {payment_id}</li>
                    <li>• <strong>Activation Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</li>
                </ul>
            </div>
            
            <h3>⚡ Quick Start Guide</h3>
            <ol>
                <li>Visit the login URL above</li>
                <li>Login with your credentials</li>
                <li>Change your password (Settings → Security)</li>
                <li>Complete your institution profile</li>
                <li>Start adding students & staff</li>
            </ol>
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p style="margin: 0;"><strong>🔒 Security Recommendation:</strong> Please change your password immediately after first login.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>Thank you for choosing Y.S.M Education System!</p>
            <p>Need help? Email us at <a href="mailto:support@ysm.education" style="color: #3b82f6;">support@ysm.education</a></p>
            <p style="margin-top: 15px; color: #6b7280;">© 2026 Y.S.M Enterprise. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"✅ Approval email sent successfully to {email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send approval email to {email}: {str(e)}")
        return False


def send_rejection_email(email, plan_type, amount, payment_id, reason=None):
    """
    Send professional rejection email with next steps
    """
    try:
        institution_name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
        currency = getattr(settings, 'CURRENCY_SYMBOL', '$')
        
        subject = "❌ Subscription Request Update - Y.S.M Education System"
        
        reason_text = f"\n🔍 Reason: {reason}\n" if reason else ""
        
        message = f"""
Dear {institution_name},

Thank you for your interest in Y.S.M Education System.

After reviewing your subscription request, we regret to inform you that it could not be approved at this time.
{reason_text}
📋 Request Details:
━━━━━━━━━━━━━━━━━━━━━━━━
• Plan Type: {plan_type}
• Amount: {currency}{amount}
• Payment ID: {payment_id}
• Submission Date: {datetime.now().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Common Reasons for Rejection:
• Invalid/unclear payment proof
• Incorrect payment amount
• Missing required information
• Payment not received in our account

🔄 What's Next?
If you believe this is an error or need clarification:
1. Reply to this email with additional details
2. Contact our support team
3. Resubmit with correct information

📞 Contact Support:
• Email: support@ysm.education
• Business Hours: 9 AM - 6 PM IST

We appreciate your understanding and look forward to serving you in the future.

Best Regards,
Y.S.M Team
Enterprise Education Management Platform

━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated email. Please do not reply.
"""
        
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f3f4f6; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 30px; text-align: center; }}
        .content {{ padding: 30px; }}
        .footer {{ background: #1f2937; color: #9ca3af; padding: 20px; text-align: center; font-size: 12px; }}
        .info-box {{ background: #fee2e2; border: 1px solid #ef4444; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; font-size: 28px;">❌ Request Update</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Y.S.M Education System</p>
        </div>
        
        <div class="content">
            <p>Dear <strong>{institution_name}</strong>,</p>
            <p>Thank you for your interest in Y.S.M Education System.</p>
            <p>After reviewing your subscription request, we regret to inform you that it could not be approved at this time.</p>
            {f'<div class="info-box"><p style="margin: 0;"><strong>Reason:</strong> {reason}</p></div>' if reason else ''}
            
            <div style="background: #f8fafc; border-left: 4px solid #6b7280; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin-top: 0;">📋 Request Details</h4>
                <ul style="list-style: none; padding: 0;">
                    <li>• <strong>Plan Type:</strong> {plan_type}</li>
                    <li>• <strong>Amount:</strong> {currency}{amount}</li>
                    <li>• <strong>Payment ID:</strong> {payment_id}</li>
                    <li>• <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</li>
                </ul>
            </div>
            
            <h3>🔄 What's Next?</h3>
            <p>If you believe this is an error or need clarification:</p>
            <ol>
                <li>Reply to this email with additional details</li>
                <li>Contact our support team</li>
                <li>Resubmit with correct information</li>
            </ol>
            
            <p style="background: #e0f2fe; border-left: 4px solid #3b82f6; padding: 15px; border-radius: 8px;">
                <strong>📞 Support:</strong> Email us at <a href="mailto:support@ysm.education" style="color: #3b82f6;">support@ysm.education</a>
            </p>
        </div>
        
        <div class="footer">
            <p>We appreciate your understanding and look forward to serving you.</p>
            <p style="margin-top: 15px; color: #6b7280;">© 2026 Y.S.M Enterprise. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"📧 Rejection email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send rejection email to {email}: {str(e)}")
        return False
