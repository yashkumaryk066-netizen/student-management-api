import requests
try:
    r = requests.get('http://127.0.0.1:8000/api/profile/')
    print(f"Status: {r.status_code}")
    print(f"Content: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
