import requests
import time

SITEMAP_URL = "https://yashamishra.pythonanywhere.com/static/sitemap.xml"
GOOGLE_PING_URL = f"http://www.google.com/ping?sitemap={SITEMAP_URL}"
BING_PING_URL = f"http://www.bing.com/ping?sitemap={SITEMAP_URL}"

def ping_search_engines():
    print(f"🚀 Starting Instant Indexing Trigger for: {SITEMAP_URL}")
    print("-" * 50)

    # 1. Ping Google
    try:
        print("📡 Contacting Google...")
        response = requests.get(GOOGLE_PING_URL)
        if response.status_code == 200:
            print("✅ Google Successfully Notified! (Crawler summoned)")
        else:
            print(f"⚠️ Google Response: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach Google: {e}")

    # 2. Ping Bing
    try:
        print("📡 Contacting Bing...")
        response = requests.get(BING_PING_URL)
        if response.status_code == 200:
            print("✅ Bing Successfully Notified!")
        else:
            print(f"⚠️ Bing Response: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to reach Bing: {e}")

    print("-" * 50)
    print("🎉 Instant Indexing Trigger Complete!")
    print("ℹ️ Note: Googlebot will visit your site within a few hours.")

if __name__ == "__main__":
    ping_search_engines()
