import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        # Professional Setup: Fetch token from settings, fallback or error if missing
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, chat_id, message, parse_mode='Markdown'):
        """
        Send a notification message to a specific Telegram Chat ID.
        """
        if not self.bot_token:
            logger.warning("Telegram Bot Token is not configured.")
            return False

        if not chat_id:
            logger.warning("No Chat ID provided for Telegram notification.")
            return False

        try:
            url = f"{self.api_base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent to {chat_id}")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram Service Error: {e}")
            return False

    def send_credentials_notification(self, user, password, role):
        """
        Advanced Template for Sending Credentials
        """
        try:
            profile = getattr(user, 'profile', None)
            chat_id = profile.telegram_chat_id if profile else None
            
            if not chat_id:
                # Fallback: Try to print logic for now (User requested "Send to mobile's telegram")
                # Since we can't map Phone -> ChatID automatically without user interaction,
                # we log this limitation.
                # Ideally, we would look up by phone if we had a database of mapped users from a previous bot interaction.
                logger.info(f"User {user.username} (Phone: {profile.phone if profile else '-'}) has no linked Telegram Chat ID.")
                return False

            message = (
                f"🔐 *Welcome to Y.S.M Advance Education*\n\n"
                f"Hello *{user.username}*,\n"
                f"Your account has been created successfully.\n\n"
                f"📋 *Role:* {role}\n"
                f"👤 *Username:* `{user.username}`\n"
                f"🔑 *Password:* `{password}`\n\n"
                f"Please login and change your password immediately.\n"
                f"[Click Here to Login](https://yashamishra.pythonanywhere.com/)"
            )
            return self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Error preparing credential message: {e}")
            return False

    def send_renewal_alert(self, user, days_remaining):
        """
        Advanced Renewal Notification
        """
        try:
            profile = getattr(user, 'profile', None)
            chat_id = profile.telegram_chat_id if profile else None
            
            if not chat_id: return False

            urgency = "⚠️" if days_remaining <= 3 else "ℹ️"
            
            message = (
                f"{urgency} *Subscription Renewal Alert*\n\n"
                f"Dear *{user.username}*,\n"
                f"Your *{profile.institution_type}* plan expires in *{days_remaining} days*.\n\n"
                f"To ensure uninterrupted access to your data and services, please renew your subscription.\n\n"
                f"[Renew Now](https://yashamishra.pythonanywhere.com/#finance)"
            )
            return self.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"Error preparing renewal message: {e}")
            return False

# Singleton Instance
telegram_service = TelegramService()
