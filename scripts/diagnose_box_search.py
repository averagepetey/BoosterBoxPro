#!/usr/bin/env python3
"""
Diagnostic script to check box registration and server connection
"""

import sys
import os
import asyncio
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


async def diagnose():
    """Diagnose box registration and server issues"""
    
    print("🔍 Diagnostic Check")
    print("=" * 60)
    
    # Check 1: Server connection
    print("\n1️⃣ Checking server connection...")
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try health endpoint first (doesn't need auth)
            try:
                response = await client.get(f"{BASE_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    print("   ✅ Server is running")
                    print(f"   Health: {response.json()}")
                else:
                    print(f"   ⚠️  Server responded with status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
            except httpx.ConnectError as e:
                print(f"   ❌ Cannot connect to server at {BASE_URL}")
                print(f"   Error type: {type(e).__name__}")
                print(f"   Error details: {str(e)}")
                print(f"   → Make sure server is running: python scripts/run_server.py")
                print(f"   → Or check if server is on a different port")
                return False
            except httpx.TimeoutException as e:
                print(f"   ❌ Connection timed out")
                print(f"   → Server might be slow or unresponsive")
                return False
            except Exception as e:
                print(f"   ❌ Unexpected error: {type(e).__name__}")
                print(f"   Error: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
            # Check 2: Boxes endpoint
            print("\n2️⃣ Checking boxes endpoint...")
            headers = {}
            if api_key:
                headers["X-API-Key"] = api_key
            else:
                print("   ⚠️  No API key configured (this is OK for dev mode)")
            
            try:
                response = await client.get(f"{API_BASE}/admin/boxes", headers=headers, timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    boxes = data.get("boxes", [])
                    total = data.get("total", 0)
                    
                    print(f"   ✅ API endpoint working")
                    print(f"   Total boxes in database: {total}")
                    
                    if boxes:
                        print(f"\n   📦 Registered boxes:")
                        for i, box in enumerate(boxes[:20], 1):  # Show first 20
                            name = box.get("product_name", "Unknown")
                            box_id = box.get("id", "Unknown")
                            print(f"   {i:2d}. {name[:60]}")
                            print(f"       ID: {box_id}")
                        
                        if total > 20:
                            print(f"   ... and {total - 20} more")
                        
                        # Check for OP-11 specifically
                        print(f"\n3️⃣ Searching for OP-11...")
                        op11_found = False
                        for box in boxes:
                            name = box.get("product_name", "").lower()
                            if "op-11" in name or "op11" in name or "fist of divine speed" in name:
                                print(f"   ✅ Found: {box.get('product_name')}")
                                print(f"      ID: {box.get('id')}")
                                op11_found = True
                                break
                        
                        if not op11_found:
                            print(f"   ❌ OP-11 not found in database")
                            print(f"   → Run: python scripts/register_boxes.py")
                    else:
                        print(f"   ⚠️  No boxes found in database")
                        print(f"   → Run: python scripts/register_boxes.py")
                else:
                    print(f"   ❌ API returned status {response.status_code}")
                    print(f"   Response: {response.text[:500]}")
                    if response.status_code == 401:
                        print(f"   → Check your ADMIN_API_KEY in .env file")
                    return False
                    
            except httpx.TimeoutException:
                print(f"   ❌ Request timed out")
                print(f"   → Server might be slow or unresponsive")
                return False
            except Exception as e:
                print(f"   ❌ Error: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✅ Diagnostic complete!")
    return True


if __name__ == "__main__":
    success = asyncio.run(diagnose())
    sys.exit(0 if success else 1)

