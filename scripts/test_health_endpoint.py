#!/usr/bin/env python3
"""
Test /health endpoint
Tests the FastAPI health check endpoint
"""

import sys
import requests
import time

def test_health_endpoint(base_url="http://localhost:8000"):
    """Test the /health endpoint"""
    print(f"Testing health endpoint at {base_url}/health...")
    print()
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            
            print(f"✅ Request successful!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.json()}")
            print()
            
            # Validate response
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    print("✅ Health check passed!")
                    return True
                else:
                    print("⚠️  Health check returned unexpected status")
                    return False
            else:
                print(f"❌ Health check failed with status code {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                print(f"⚠️  Could not connect to server (attempt {attempt + 1}/{max_retries})")
                print(f"   Waiting {retry_delay} seconds before retry...")
                print(f"   Make sure the server is running: uvicorn app.main:app --reload")
                print()
                time.sleep(retry_delay)
            else:
                print("❌ Could not connect to server after multiple attempts")
                print()
                print("Make sure the server is running:")
                print("  source venv/bin/activate")
                print("  uvicorn app.main:app --reload")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    return False

if __name__ == "__main__":
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    success = test_health_endpoint(base_url)
    sys.exit(0 if success else 1)

