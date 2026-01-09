import requests
import time

BOT_TOKEN = "8384943128:AAH6r2ovKp20XUMSi64asxo4J0lc_lvZvxc"
WEBHOOK_URL = "https://yashamishra.pythonanywhere.com/api/notifications/telegram/webhook/"

def init_webhook():
    print("--------------------------------------------------")
    print("🌐 Setting up Telegram Webhook for Auto-Linking...")
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {'url': WEBHOOK_URL}
    
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            print("✅ SUCCESS: Webhook registered with Telegram!")
            print(f"🔗 URL: {WEBHOOK_URL}")
        else:
            print(f"❌ ERROR: {res.text}")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        
    print("--------------------------------------------------")

if __name__ == "__main__":
    init_webhook()
