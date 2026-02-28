import requests
import sys

BASE_URL = "https://yashamishra.pythonanywhere.com/api"

def test_system():
    print(f"Testing API at: {BASE_URL}")
    
    # 1. Login
    print("\n1. Testing Login...")
    try:
        login_res = requests.post(f"{BASE_URL}/auth/login/", json={
            "username": "admin",
            "password": "adminpassword123"
        })
        
        if login_res.status_code != 200:
            print(f"❌ Login Failed: {login_res.status_code} - {login_res.text}")
            return
            
        data = login_res.json()
        token = data.get('access')
        print("✅ Login Successful! Token received.")
    except Exception as e:
        print(f"❌ Login Connection Error: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Batches
    print("\n2. Testing /batches/ endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/batches/", headers=headers)
        if res.status_code == 200:
            print(f"✅ /batches/ working. Found {len(res.json())} batches.")
        else:
            print(f"❌ /batches/ Failed: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ /batches/ Error: {e}")

    # 3. Test Students
    print("\n3. Testing /students/ endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/students/", headers=headers)
        if res.status_code == 200:
            print(f"✅ /students/ working. Found {len(res.json())} students.")
        else:
            print(f"❌ /students/ Failed: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ /students/ Error: {e}")
        
    # 4. Test Exams
    print("\n4. Testing /exams/ endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/exams/", headers=headers)
        if res.status_code == 200:
            print(f"✅ /exams/ working. Found {len(res.json())} exams.")
        else:
            print(f"❌ /exams/ Failed: {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"❌ /exams/ Error: {e}")

if __name__ == "__main__":
    test_system()
