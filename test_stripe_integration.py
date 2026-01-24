#!/usr/bin/env python3
"""
Test Stripe Integration
Tests the Stripe payment endpoints
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if backend is running"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("   Start with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_checkout_session():
    """Test creating a checkout session"""
    print("\n🔍 Testing checkout session creation...")
    
    url = f"{BASE_URL}/api/v1/payment/create-checkout-session"
    payload = {
        "email": "test@example.com",
        "tier": "pro+",
        "trial_days": 7
    }
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Checkout session created successfully!")
            print(f"   Session ID: {data.get('session_id', 'N/A')}")
            print(f"   Checkout URL: {data.get('url', 'N/A')}")
            print("\n📝 Next steps:")
            print("   1. Open the checkout URL in your browser")
            print("   2. Complete the test payment")
            print("   3. Check webhook events in your Stripe CLI terminal")
            return True
        else:
            print(f"❌ Failed to create checkout session")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_verify_subscription():
    """Test subscription verification endpoint"""
    print("\n🔍 Testing subscription verification...")
    print("   (This requires a session_id from a completed checkout)")
    print("   Skipping for now - use after completing a checkout")
    return True

def main():
    print("=" * 60)
    print("STRIPE INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        sys.exit(1)
    
    # Test 2: Create checkout session
    if not test_create_checkout_session():
        print("\n⚠️  Checkout session creation failed")
        print("   Make sure:")
        print("   - Backend is running")
        print("   - Stripe keys are set in .env")
        print("   - Price ID is configured for 'pro+' tier")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ BASIC TESTS PASSED")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("   1. Complete a test checkout in Stripe")
    print("   2. Monitor webhook events in Stripe CLI")
    print("   3. Verify user subscription in database")

if __name__ == "__main__":
    main()
