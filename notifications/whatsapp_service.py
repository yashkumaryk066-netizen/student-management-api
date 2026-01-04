"""
WhatsApp Notification Service using Twilio API
Handles sending WhatsApp messages to students, parents, and admin
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime


class WhatsAppService:
    """
    WhatsApp notification service
    Configure with environment variables:
    - TWILIO_ACCOUNT_SID
    - TWILIO_AUTH_TOKEN
    - TWILIO_WHATSAPP_NUMBER (format: whatsapp:+14155238886)
    """
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
        self.enabled = bool(self.account_sid and self.auth_token)
        
        if self.enabled:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
            except ImportError:
                print("Twilio SDK not installed. Run: pip install twilio")
                self.enabled = False
        else:
            self.client = None
            print("WhatsApp service disabled. Configure TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to enable.")
    
    def send_message(self, to_number: str, message: str, template_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send WhatsApp message to a phone number
        
        Args:
            to_number: Recipient phone number (format: +919876543210)
            message: Message text
            template_vars: Optional template variables for message formatting
            
        Returns:
            Dict with status and message_sid or error
        """
        # Format phone number for WhatsApp
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        # Format message with template variables if provided
        if template_vars:
            try:
                message = message.format(**template_vars)
            except KeyError as e:
                return {'status': 'error', 'error': f'Missing template variable: {e}'}
        
        if not self.enabled:
            # --- INTERNAL SIMULATION FOR "ADVANCE LEVEL" DEMO ---
            # Save to Database so it appears in Admin Panel as a "System Alert"
            try:
                from student.models import Notification, User
                # Attempt to find user by phone number (reverse lookup) - simplified logic
                recipient_user = None
                
                # If sending to Admin
                from django.conf import settings
                if to_number == settings.ADMIN_WHATSAPP_NUMBER or to_number == f"whatsapp:{settings.ADMIN_WHATSAPP_NUMBER}":
                    recipient_user = User.objects.filter(is_superuser=True).first()
                    title = "WhatsApp (Admin Alert)"
                    
                # Store in DB
                if recipient_user:
                    Notification.objects.create(
                        recipient=recipient_user,
                        recipient_type='ADMIN',
                        title=title,
                        message=message
                    )
                else:
                    # Generic logging for unknown numbers (or client phones) purely for debug/demo
                    # We might not have a clean way to link phone -> user here without more queries
                    pass
                    
            except Exception as e:
                print(f"Mock Notification DB Error: {e}")
                
            print(f"[MOCK WhatsApp] To: {to_number}")
            print(f"[MOCK WhatsApp] Message: {message}")
            return {
                'status': 'mock',
                'message_sid': f'MOCK_{datetime.now().timestamp()}',
                'to': to_number,
                'message': 'WhatsApp service not configured (mock mode)'
            }
        
        # Send actual WhatsApp message
        try:
            message_obj = self.client.messages.create(
                from_=self.from_number,
                body=message,
                to=to_number
            )
            
            # Record Successful Verification in DB too for consistency
            try:
                from student.models import Notification, User
                from django.conf import settings
                if to_number == settings.ADMIN_WHATSAPP_NUMBER:
                     recipient_user = User.objects.filter(is_superuser=True).first()
                     if recipient_user:
                        Notification.objects.create(
                            recipient=recipient_user, recipient_type='ADMIN',
                            title="WhatsApp Sent", message=message
                        )
            except:
                pass
            
            return {
                'status': 'sent',
                'message_sid': message_obj.sid,
                'to': to_number,
                'message': 'WhatsApp sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'to': to_number
            }
    
    def send_demo_request_notification(self, requester_name: str, requester_phone: str, 
                                      requester_email: str, institution_name: str = '') -> Dict[str, Any]:
        """
        Send demo request notification to admin (8356926231)
        
        Args:
            requester_name: Name of person requesting demo
            requester_phone: Their phone number
            requester_email: Their email
            institution_name: Name of their institution (optional)
            
        Returns:
            Dict with status
        """
        admin_number = '+918356926231'
        
        message = f"""🎓 *New Demo Request - NextGen ERP*

👤 Name: {requester_name}
📞 Phone: {requester_phone}
✉️ Email: {requester_email}"""
        
        if institution_name:
            message += f"\n🏫 Institution: {institution_name}"
        
        message += f"\n\n⏰ Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        message += "\n\n_Please contact them to schedule a personalized demo._"
        
        return self.send_message(admin_number, message)
    
    def send_fee_reminder(self, student_name: str, parent_number: str, 
                         amount: float, due_date: str) -> Dict[str, Any]:
        """
        Send fee payment reminder to parent
        
        Args:
            student_name: Student name
            parent_number: Parent's WhatsApp number
            amount: Fee amount
            due_date: Due date string
            
        Returns:
            Dict with status
        """
        message = f"""📢 *Fee Payment Reminder*

Dear Parent,

This is a reminder for {student_name}'s pending fee payment:

💰 Amount: ₹{amount:,.2f}
📅 Due Date: {due_date}

Please make the payment at your earliest convenience to avoid late fees.

For any queries, contact the accounts department.

_NextGen ERP - Institute Management System_"""
        
        return self.send_message(parent_number, message)
    
    def send_attendance_alert(self, student_name: str, parent_number: str, date: str) -> Dict[str, Any]:
        """
        Send attendance alert to parent when student is absent
        
        Args:
            student_name: Student name
            parent_number: Parent's WhatsApp number  
            date: Date of absence
            
        Returns:
            Dict with status
        """
        message = f"""⚠️ *Attendance Alert*

Dear Parent,

{student_name} was marked ABSENT on {date}.

If this is unexpected, please contact the class teacher immediately.

_NextGen ERP - Institute Management System_"""
        
        return self.send_message(parent_number, message)


# Singleton instance
whatsapp_service = WhatsAppService()
