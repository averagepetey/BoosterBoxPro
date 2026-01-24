#!/usr/bin/env python3
"""
Simple test script to verify authentication endpoints work
Run this after starting the server: python test_auth_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("\n🧪 Testing Registration Endpoint...")
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": "test@example.com",
        "password": "Test1234",
        "confirm_password": "Test1234"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
            print("⚠️  User already exists (this is OK for testing)")
            return True
        else:
            print(f"❌ Registration failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_login():
    """Test user login"""
    print("\n🧪 Testing Login Endpoint...")
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "test@example.com",
        "password": "Test1234"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            print("✅ Login successful!")
            print(f"Token: {result.get('access_token', '')[:50]}...")
            print(f"Is Admin: {result.get('is_admin', False)}")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {result}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    print("\n🧪 Testing Protected Endpoint (booster-boxes)...")
    url = f"{BASE_URL}/booster-boxes"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Protected endpoint accessible!")
            data = response.json()
            print(f"Found {len(data.get('data', []))} boxes")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - token invalid or expired")
            return False
        else:
            print(f"❌ Unexpected status: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_me_endpoint(token):
    """Test /auth/me endpoint"""
    print("\n🧪 Testing /auth/me Endpoint...")
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ /auth/me successful!")
            print(f"User Info: {response.json()}")
            return True
        else:
            print(f"❌ Failed: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Authentication Endpoints Test")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")
    print("\n⚠️  Make sure the server is running: uvicorn main:app --reload")
    
    # Test registration
    register_success = test_register()
    
    # Test login
    token = test_login()
    
    if token:
        # Test protected endpoint
        test_protected_endpoint(token)
        
        # Test /auth/me
        test_me_endpoint(token)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

