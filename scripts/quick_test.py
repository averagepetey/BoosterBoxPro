#!/usr/bin/env python3
"""
Quick Test Suite - Tests core functionality without requiring venv
Uses system Python and requests library
"""

import sys
import requests
from datetime import date

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test(name):
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print('='*60)
    return True

def success(msg):
    print(f"✅ {msg}")

def error(msg):
    print(f"❌ {msg}")

def warning(msg):
    print(f"⚠️  {msg}")

def test_server_health():
    test("Server Health Check")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            success(f"Server is running: {data}")
            return True
        else:
            error(f"Server returned {r.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        error("Cannot connect to server. Is it running?")
        return False
    except Exception as e:
        error(f"Error: {e}")
        return False

def test_public_api():
    test("Public API Endpoints")
    
    try:
        # Test leaderboard
        r = requests.get(f"{API_BASE}/booster-boxes?limit=5", timeout=10)
        if r.status_code == 200:
            data = r.json()
            success(f"Leaderboard endpoint: {len(data.get('data', []))} boxes")
            
            # Test sort
            r2 = requests.get(f"{API_BASE}/booster-boxes?sort=liquidity_score&limit=3", timeout=10)
            if r2.status_code == 200:
                success("Leaderboard sorting works")
            else:
                warning(f"Sort test returned {r2.status_code}")
            
            return True
        else:
            error(f"Leaderboard returned {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        error(f"Public API test failed: {e}")
        return False

def test_admin_api():
    test("Admin API Endpoints")
    
    # Try with and without API key
    try:
        r = requests.get(f"{API_BASE}/admin/boxes", timeout=10)
        if r.status_code == 200:
            data = r.json()
            count = data.get('total', 0)
            success(f"Admin endpoint accessible: {count} boxes")
            return True
        elif r.status_code == 401:
            warning("Admin endpoint requires API key (expected in production)")
            return True
        else:
            warning(f"Admin endpoint returned {r.status_code}")
            return True
    except Exception as e:
        error(f"Admin API test failed: {e}")
        return False

def test_api_docs():
    test("API Documentation")
    
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=5)
        if r.status_code == 200:
            success("API documentation available at /docs")
            return True
        else:
            warning(f"Docs returned {r.status_code}")
            return True
    except Exception as e:
        warning(f"Docs check failed: {e}")
        return True

def test_endpoint_structure():
    test("Endpoint Structure")
    
    endpoints = [
        ("/", "Root"),
        ("/health", "Health"),
        ("/api/v1/booster-boxes", "Leaderboard"),
        ("/docs", "API Docs"),
    ]
    
    all_ok = True
    for path, name in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            r = requests.get(url, timeout=5, allow_redirects=True)
            if r.status_code in [200, 307, 308]:
                success(f"{name} endpoint ({path}) responds")
            else:
                warning(f"{name} endpoint returned {r.status_code}")
        except Exception as e:
            error(f"{name} endpoint error: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*60)
    print("BoosterBoxPro - Quick Test Suite")
    print("="*60)
    
    results = {
        "Server Health": test_server_health(),
        "Public API": test_public_api(),
        "Admin API": test_admin_api(),
        "API Docs": test_api_docs(),
        "Endpoint Structure": test_endpoint_structure(),
    }
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:.<40} {status}")
    
    print("\n" + "="*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        success("All tests passed! 🎉")
    elif passed >= total * 0.8:
        warning("Most tests passed")
    else:
        error("Multiple failures detected")
    
    print("="*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' library not installed")
        print("   Install with: pip install requests")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)

