#!/usr/bin/env python3
"""
Test Script for Phase 8 Authentication
Tests the complete authentication and subscription flow
"""
import sys
import asyncio
import httpx
from datetime import datetime
from pathlib import Path

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


async def test_authentication_flow():
    """Test complete authentication flow"""
    print("=" * 60)
    print("Phase 8 Authentication Test")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Generate unique email for testing
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_email = f"test_{timestamp}@example.com"
        test_password = "testpassword123"
        
        print(f"\n1. Testing User Registration...")
        print(f"   Email: {test_email}")
        
        try:
            # Register user
            register_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/auth/register",
                json={
                    "email": test_email,
                    "password": test_password,
                    "username": "testuser"
                }
            )
            
            if register_response.status_code == 201:
                user_data = register_response.json()
                print(f"   ✅ Registration successful!")
                print(f"   User ID: {user_data['id']}")
                print(f"   Status: {user_data['subscription_status']}")
                print(f"   Trial ends: {user_data.get('trial_ended_at', 'N/A')}")
            else:
                print(f"   ❌ Registration failed: {register_response.status_code}")
                print(f"   Response: {register_response.text}")
                return False
        
        except Exception as e:
            print(f"   ❌ Registration error: {e}")
            return False
        
        print(f"\n2. Testing User Login...")
        
        try:
            # Login
            login_response = await client.post(
                f"{BASE_URL}{API_PREFIX}/auth/login",
                json={
                    "email": test_email,
                    "password": test_password
                }
            )
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                access_token = login_data['access_token']
                print(f"   ✅ Login successful!")
                print(f"   Token type: {login_data['token_type']}")
                print(f"   Trial days remaining: {login_data.get('trial_days_remaining', 'N/A')}")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                return False
        
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
        
        print(f"\n3. Testing Protected Endpoint (with token)...")
        
        try:
            # Access protected endpoint with token
            headers = {"Authorization": f"Bearer {access_token}"}
            leaderboard_response = await client.get(
                f"{BASE_URL}{API_PREFIX}/booster-boxes?limit=5",
                headers=headers
            )
            
            if leaderboard_response.status_code == 200:
                data = leaderboard_response.json()
                print(f"   ✅ Protected endpoint accessible!")
                print(f"   Boxes returned: {len(data.get('data', []))}")
            else:
                print(f"   ❌ Protected endpoint failed: {leaderboard_response.status_code}")
                print(f"   Response: {leaderboard_response.text}")
                return False
        
        except Exception as e:
            print(f"   ❌ Protected endpoint error: {e}")
            return False
        
        print(f"\n4. Testing Protected Endpoint (without token)...")
        
        try:
            # Try without token (should fail)
            no_auth_response = await client.get(
                f"{BASE_URL}{API_PREFIX}/booster-boxes?limit=5"
            )
            
            if no_auth_response.status_code == 403 or no_auth_response.status_code == 401:
                print(f"   ✅ Correctly rejected request without token!")
                print(f"   Status: {no_auth_response.status_code}")
            else:
                print(f"   ⚠️  Unexpected status: {no_auth_response.status_code}")
                print(f"   Response: {no_auth_response.text}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print(f"\n5. Testing Get Current User...")
        
        try:
            # Get current user info
            user_info_response = await client.get(
                f"{BASE_URL}{API_PREFIX}/auth/me",
                headers=headers
            )
            
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                print(f"   ✅ User info retrieved!")
                print(f"   Email: {user_info['email']}")
                print(f"   Status: {user_info['subscription_status']}")
                print(f"   Has active access: {user_info['has_active_access']}")
            else:
                print(f"   ❌ Failed to get user info: {user_info_response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print(f"\n6. Testing Subscription Status...")
        
        try:
            # Get subscription status
            sub_status_response = await client.get(
                f"{BASE_URL}{API_PREFIX}/users/me/subscription",
                headers=headers
            )
            
            if sub_status_response.status_code == 200:
                sub_status = sub_status_response.json()
                print(f"   ✅ Subscription status retrieved!")
                print(f"   Status: {sub_status['subscription_status']}")
                print(f"   Trial active: {sub_status['trial_active']}")
                print(f"   Days remaining: {sub_status.get('trial_days_remaining', 'N/A')}")
                print(f"   Has active access: {sub_status['has_active_access']}")
            else:
                print(f"   ❌ Failed to get subscription status: {sub_status_response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print(f"\n" + "=" * 60)
        print("✅ All authentication tests completed!")
        print("=" * 60)
        
        return True


async def main():
    """Main test function"""
    try:
        # Test if server is running
        async with httpx.AsyncClient(timeout=5.0) as client:
            health_response = await client.get(f"{BASE_URL}/health")
            if health_response.status_code != 200:
                print("❌ Server is not responding. Make sure FastAPI is running.")
                print("   Start server: ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000")
                return
        
        await test_authentication_flow()
    
    except httpx.ConnectError:
        print("❌ Cannot connect to server. Make sure FastAPI is running.")
        print("   Start server: ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

