from django.test import TestCase
from notifications.sms_service import sms_service
from notifications.whatsapp_service import whatsapp_service
from notifications.telegram_service import telegram_service
from unittest.mock import patch, MagicMock

class NotificationServicesTest(TestCase):
    
    def test_sms_disabled_mode(self):
        """Test that SMS service handles disabled mode gracefully"""
        service = sms_service
        # Force state for test
        original_enabled = service.enabled
        service.enabled = False
        result = service.send_message("+918356926231", "Test SMS")
        self.assertEqual(result['status'], 'mock')
        service.enabled = original_enabled

    def test_whatsapp_disabled_mode(self):
        """Test that WhatsApp service handles disabled mode gracefully"""
        service = whatsapp_service
        original_enabled = service.enabled
        service.enabled = False
        result = service.send_message("+918356926231", "Test WhatsApp")
        self.assertEqual(result['status'], 'mock')
        service.enabled = original_enabled

    def test_telegram_disabled_mode(self):
        """Test that Telegram service handles disabled mode gracefully"""
        service = telegram_service
        original_token = service.bot_token
        service.bot_token = None
        result = service.send_message("12345", "Test Alert")
        self.assertFalse(result)
        service.bot_token = original_token
