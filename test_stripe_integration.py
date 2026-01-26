#!/usr/bin/env python3
"""
Test Stripe Integration
Quick test to verify Stripe checkout session creation works
"""

import os
import sys
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Make sure you're in the virtual environment: source venv/bin/activate")
    sys.exit(1)


def test_backend_running():
    """Check if backend server is running"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=2)
        return True, "✅ Backend is running"
    except requests.exceptions.ConnectionError:
        return False, "❌ Backend is not running. Start it with: python main.py"
    except Exception as e:
        return False, f"❌ Error checking backend: {str(e)}"


def test_checkout_session():
    """Test creating a checkout session"""
    if not settings.stripe_secret_key:
        return False, "❌ STRIPE_SECRET_KEY not set"
    
    if not settings.stripe_price_id_pro_plus:
        return False, "❌ STRIPE_PRICE_ID_PRO_PLUS not set"
    
    try:
        # Test checkout session creation
        response = requests.post(
            "http://localhost:8000/api/v1/payment/create-checkout-session",
            json={
                "email": "test@example.com",
                "tier": "pro+",
                "trial_days": 7
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Checkout session created successfully!\n   Session ID: {data.get('session_id', 'N/A')[:20]}...\n   Checkout URL: {data.get('url', 'N/A')[:50]}..."
        else:
            return False, f"❌ Failed to create checkout session: {response.status_code}\n   {response.text}"
    
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to backend. Make sure it's running on port 8000"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def main():
    """Main test function"""
    print("=" * 60)
    print("Stripe Integration Test")
    print("=" * 60)
    print()
    
    # Test 1: Backend running
    print("1️⃣  Checking if backend is running...")
    backend_check = test_backend_running()
    print(f"   {backend_check[1]}")
    if not backend_check[0]:
        print()
        print("   Please start the backend server first:")
        print("   source venv/bin/activate")
        print("   python main.py")
        sys.exit(1)
    
    print()
    
    # Test 2: Checkout session
    print("2️⃣  Testing checkout session creation...")
    checkout_check = test_checkout_session()
    print(f"   {checkout_check[1]}")
    if not checkout_check[0]:
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Stripe integration test passed!")
    print()
    print("Next steps:")
    print("  1. Open the checkout URL in your browser")
    print("  2. Use test card: 4242 4242 4242 4242")
    print("  3. Complete checkout to test webhook")
    print("  4. Make sure Stripe CLI is running:")
    print("     stripe listen --forward-to localhost:8000/api/v1/payment/webhook")
    print("=" * 60)


if __name__ == "__main__":
    main()
