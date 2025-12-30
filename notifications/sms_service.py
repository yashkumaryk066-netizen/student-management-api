"""
SMS Notification Service
Supports multiple Indian SMS gateways
"""
import os
import requests
from typing import Optional, Dict, Any
from datetime import datetime


class SMSService:
    """
    SMS notification service
    Configure with environment variables:
    - SMS_GATEWAY (msg91, twilio, textlocal)
    - SMS_API_KEY
    - SMS_SENDER_ID
    """
    
    def __init__(self):
        self.gateway = os.getenv('SMS_GATEWAY', 'msg91').lower()
        self.api_key = os.getenv('SMS_API_KEY', '')
        self.sender_id = os.getenv('SMS_SENDER_ID', 'NXTERP')
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("SMS service disabled. Configure SMS_API_KEY to enable.")
    
    def send_message(self, to_number: str, message: str, template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Send SMS to a phone number
        
        Args:
            to_number: Recipient phone number (format: 9876543210 or +919876543210)
            message: Message text
            template_id: DLT template ID (required for Indian numbers)
            
        Returns:
            Dict with status and details
        """
        # Clean phone number
        to_number = to_number.replace('+91', '').replace('+', '').replace(' ', '').replace('-', '')
        
        # If service is not enabled, return mock response
        if not self.enabled:
            print(f"[MOCK SMS] To: {to_number}")
            print(f"[MOCK SMS] Message: {message}")
            return {
                'status': 'mock',
                'message_id': f'MOCK_{datetime.now().timestamp()}',
                'to': to_number,
                'message': 'SMS service not configured (mock mode)'
            }
        
        # Send via configured gateway
        if self.gateway == 'msg91':
            return self._send_via_msg91(to_number, message, template_id)
        elif self.gateway == 'twilio':
            return self._send_via_twilio(to_number, message)
        elif self.gateway == 'textlocal':
            return self._send_via_textlocal(to_number, message)
        else:
            return {'status': 'error', 'error': f'Unknown gateway: {self.gateway}'}
    
    def _send_via_msg91(self, to_number: str, message: str, template_id: Optional[str]) -> Dict[str, Any]:
        """Send SMS via MSG91"""
        url = "https://api.msg91.com/api/v5/flow/"
        
        payload = {
            "sender": self.sender_id,
            "mobiles": f"91{to_number}",
            "message": message,
        }
        
        if template_id:
            payload['template_id'] = template_id
        
        headers = {
            "authkey": self.api_key,
            "content-type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return {
                    'status': 'sent',
                    'message_id': response.json().get('request_id'),
                    'to': to_number,
                    'gateway': 'msg91'
                }
            else:
                return {
                    'status': 'error',
                    'error': response.text,
                    'to': to_number
                }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'to': to_number}
    
    def _send_via_twilio(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            from_number = os.getenv('TWILIO_PHONE_NUMBER')
            
            client = Client(account_sid, auth_token)
            message_obj = client.messages.create(
                from_=from_number,
                body=message,
                to=f'+91{to_number}'
            )
            
            return {
                'status': 'sent',
                'message_id': message_obj.sid,
                'to': to_number,
                'gateway': 'twilio'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'to': to_number}
    
    def _send_via_textlocal(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS via TextLocal"""
        url = "https://api.textlocal.in/send/"
        
        payload = {
            'apikey': self.api_key,
            'sender': self.sender_id,
            'numbers': to_number,
            'message': message
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'status': 'sent',
                        'message_id': data.get('messages', [{}])[0].get('id'),
                        'to': to_number,
                        'gateway': 'textlocal'
                    }
                else:
                    return {'status': 'error', 'error': data.get('errors'), 'to': to_number}
            else:
                return {'status': 'error', 'error': response.text, 'to': to_number}
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'to': to_number}
    
    def send_otp(self, to_number: str, otp: str) -> Dict[str, Any]:
        """
        Send OTP for verification
        
        Args:
            to_number: Phone number
            otp: OTP code
            
        Returns:
            Dict with status
        """
        message = f"Your NextGen ERP verification code is: {otp}. Valid for 10 minutes. Do not share this code."
        return self.send_message(to_number, message)
    
    def send_fee_reminder(self, to_number: str, student_name: str, amount: float, due_date: str) -> Dict[str, Any]:
        """Send fee payment reminder"""
        message = f"Fee Reminder: {student_name}'s pending fee of Rs.{amount:.2f} is due on {due_date}. Please pay soon. -NextGen ERP"
        return self.send_message(to_number, message)
    
    def send_attendance_alert(self, to_number: str, student_name: str, date: str) -> Dict[str, Any]:
        """Send attendance alert"""
        message = f"Attendance Alert: {student_name} was absent on {date}. Please contact school if unexpected. -NextGen ERP"
        return self.send_message(to_number, message)


# Singleton instance
sms_service = SMSService()
