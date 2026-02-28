#!/usr/bin/env python
"""
LOGIN SYSTEM - COMPREHENSIVE TEST SUITE
Tests all login endpoints and security features
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, passed, details=""):
    icon = f"{GREEN}✅" if passed else f"{RED}❌"
    print(f"{icon} {name}{RESET}")
    if details:
        print(f"   {YELLOW}{details}{RESET}")

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{RESET}\n")

# Test Data
TEST_CREDENTIALS = {
    "valid": {"username": "admin", "password": "admin123"},  # Update with your credentials
    "invalid_password": {"username": "admin", "password": "wrong"},
    "invalid_username": {"username": "nonexistent", "password": "any"}
}

def test_username_check():
    print_header("TEST 1: Username Existence Check")
    
    # Valid username
    try:
        res = requests.post(f"{BASE_URL}/auth/check-username/", 
                          json={"username": TEST_CREDENTIALS["valid"]["username"]})
        data = res.json()
        print_test("Valid Username Check", 
                  res.status_code == 200 and data.get("exists") == True,
                  f"Response: {data}")
    except Exception as e:
        print_test("Valid Username Check", False, str(e))
    
    # Invalid username
    try:
        res = requests.post(f"{BASE_URL}/auth/check-username/", 
                          json={"username": "nonexistent_user_12345"})
        data = res.json()
        print_test("Invalid Username Check", 
                  data.get("exists") == False,
                  f"Response: {data}")
    except Exception as e:
        print_test("Invalid Username Check", False, str(e))

def test_login_success():
    print_header("TEST 2: Successful Login")
    
    try:
        res = requests.post(f"{BASE_URL}/auth/login/", 
                          json=TEST_CREDENTIALS["valid"])
        data = res.json()
        
        has_tokens = "access" in data and "refresh" in data
        print_test("Login Success", 
                  res.status_code == 200 and has_tokens,
                  f"Tokens received: {list(data.keys())}")
        
        if has_tokens:
            return data["access"]
        
    except Exception as e:
        print_test("Login Success", False, str(e))
    
    return None

def test_login_failures():
    print_header("TEST 3: Login Failure Scenarios")
    
    # Wrong password
    try:
        res = requests.post(f"{BASE_URL}/auth/login/", 
                          json=TEST_CREDENTIALS["invalid_password"])
        print_test("Wrong Password Rejection", 
                  res.status_code == 401,
                  f"Status: {res.status_code}")
    except Exception as e:
        print_test("Wrong Password Rejection", False, str(e))
    
    # Invalid username
    try:
        res = requests.post(f"{BASE_URL}/auth/login/", 
                          json=TEST_CREDENTIALS["invalid_username"])
        print_test("Invalid Username Rejection", 
                  res.status_code == 401,
                  f"Status: {res.status_code}")
    except Exception as e:
        print_test("Invalid Username Rejection", False, str(e))

def test_rate_limiting():
    print_header("TEST 4: Rate Limiting")
    
    print(f"{YELLOW}   Attempting 11 rapid login requests...{RESET}")
    
    for i in range(11):
        try:
            res = requests.post(f"{BASE_URL}/auth/login/", 
                              json=TEST_CREDENTIALS["invalid_password"])
            if i == 10:
                print_test("Rate Limit Triggered", 
                          res.status_code == 429,
                          f"11th attempt status: {res.status_code}")
        except Exception as e:
            if i == 10:
                print_test("Rate Limit Triggered", False, str(e))

def test_token_refresh(access_token):
    print_header("TEST 5: Token Refresh")
    
    # Get refresh token first
    try:
        login_res = requests.post(f"{BASE_URL}/auth/login/", 
                                 json=TEST_CREDENTIALS["valid"])
        refresh_token = login_res.json().get("refresh")
        
        # Test refresh
        refresh_res = requests.post(f"{BASE_URL}/auth/token/refresh/", 
                                   json={"refresh": refresh_token})
        data = refresh_res.json()
        
        print_test("Token Refresh", 
                  refresh_res.status_code == 200 and "access" in data,
                  f"New access token received: {bool(data.get('access'))}")
        
    except Exception as e:
        print_test("Token Refresh", False, str(e))

def test_profile_access(access_token):
    print_header("TEST 6: Authenticated Profile Access")
    
    if not access_token:
        print_test("Profile Access", False, "No token available")
        return
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(f"{BASE_URL}/profile/", headers=headers)
        data = res.json()
        
        print_test("Profile Fetch", 
                  res.status_code == 200 and "role" in data,
                  f"User role: {data.get('role')}")
        
    except Exception as e:
        print_test("Profile Fetch", False, str(e))

def test_csrf_protection():
    print_header("TEST 7: CSRF Protection")
    
    try:
        # Attempt login without CSRF token (should still work for API)
        res = requests.post(f"{BASE_URL}/auth/login/", 
                          json=TEST_CREDENTIALS["valid"])
        print_test("API Login (No CSRF needed)", 
                  res.status_code == 200,
                  "JWT API endpoints exempt from CSRF")
        
    except Exception as e:
        print_test("CSRF Protection", False, str(e))

def test_cors_headers():
    print_header("TEST 8: CORS Configuration")
    
    try:
        res = requests.options(f"{BASE_URL}/auth/login/")
        cors_header = res.headers.get('Access-Control-Allow-Origin')
        
        print_test("CORS Headers Present", 
                  cors_header is not None,
                  f"CORS Origin: {cors_header}")
        
    except Exception as e:
        print_test("CORS Headers", False, str(e))

def main():
    print(f"\n{BLUE}{'#'*60}")
    print(f"#  LOGIN SYSTEM - COMPREHENSIVE TEST SUITE")
    print(f"#  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"#  Target: {BASE_URL}")
    print(f"{'#'*60}{RESET}\n")
    
    print(f"{YELLOW}⚠️  Update TEST_CREDENTIALS in script before running!{RESET}\n")
    
    # Run all tests
    test_username_check()
    access_token = test_login_success()
    test_login_failures()
    test_rate_limiting()
    test_token_refresh(access_token)
    test_profile_access(access_token)
    test_csrf_protection()
    test_cors_headers()
    
    print_header("TEST SUITE COMPLETE")
    print(f"{GREEN}All critical login functionalities tested!{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Tests interrupted by user{RESET}\n")
    except Exception as e:
        print(f"\n{RED}Fatal error: {e}{RESET}\n")
