import requests
import logging
from django.conf import settings
import os

logger = logging.getLogger(__name__)

def send_telegram_notification(chat_id, message, invoice_pdf=None, invoice_filename="Invoice.pdf"):
    """
    Sends a text message and optionally a PDF file to a Telegram user.
    Uses requests directly to avoid dependency issues with python-telegram-bot in some environments.
    """
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '8384943128:AAH6r2ovKp20XUMSi64asxo4J0lc_lvZvxc')
    
    if not token or not chat_id:
        logger.error("Telegram Token or Chat ID missing.")
        return

    # 1. Send Text Message
    text_url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        res = requests.post(text_url, data=data)
        if not res.ok:
            logger.error(f"Telegram Message Failed: {res.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

    # 2. Send Invoice PDF (if provided)
    if invoice_pdf:
        doc_url = f"https://api.telegram.org/bot{token}/sendDocument"
        try:
            files = {
                'document': (invoice_filename, invoice_pdf, 'application/pdf')
            }
            data = {
                "chat_id": chat_id,
                "caption": "✅ Payment Invoice"
            }
            res = requests.post(doc_url, data=data, files=files)
            if not res.ok:
                 logger.error(f"Telegram Document Failed: {res.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram document: {e}")
