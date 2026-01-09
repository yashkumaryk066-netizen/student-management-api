import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from .telegram_service import telegram_service
import requests

logger = logging.getLogger(__name__)

@csrf_exempt
def telegram_webhook(request):
    """
    Advanced Webhook to handle Telegram updates.
    Automatically links users when they click 'Start'.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        
        # We are only interested in "message" updates
        if 'message' not in data:
            return JsonResponse({'status': 'ignored'})
            
        message = data['message']
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        
        # Handle '/start' command
        # Advanced Logic: We expect '/start <username>' to auto-link
        if text.startswith('/start'):
            parts = text.split()
            
            if len(parts) > 1:
                # Deep Linking: User clicked a link with their username/ID
                # Format: https://t.me/MyBot?start=username
                payload = parts[1]
                
                # Try to find the user by username
                try:
                    user = User.objects.filter(username__iexact=payload).first()
                    if user and hasattr(user, 'profile'):
                        # Link/Update the Chat ID
                        user.profile.telegram_chat_id = str(chat_id)
                        user.profile.save()
                        
                        logger.info(f"🔗 Linked Telegram Chat {chat_id} to User {user.username}")
                        
                        # Send Success Message
                        response_msg = (
                            f"✅ *Account Linked Successfully!*\n\n"
                            f"Hello *{user.profile.user_full_name or user.username}*,\n"
                            f"Your Telegram is now connected to the **Y.S.M Advance Education System**.\n\n"
                            f"You will now receive instant alerts for:\n"
                            f"• Credentials & Login Details\n"
                            f"• Performance Reports\n"
                            f"• Subscription Updates\n\n"
                            f"🚀 *Welcome Aboard!*"
                        )
                        telegram_service.send_message(chat_id, response_msg)
                        return JsonResponse({'status': 'linked'})
                        
                except Exception as e:
                    logger.error(f"Linking Error: {e}")
                    telegram_service.send_message(chat_id, "⚠️ Error linking account. Please contact Admin.")
            
            else:
                # Just started without payload
                telegram_service.send_message(chat_id, "👋 Welcome! To connect your account, please ask your Admin for your **Magic Invite Link**.")

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        logger.error(f"Webhook Error: {e}")
        return JsonResponse({'status': 'error'}, status=500)
