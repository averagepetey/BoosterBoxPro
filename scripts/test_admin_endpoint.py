#!/usr/bin/env python3
"""
Test admin endpoint authentication
"""

import sys
import os
import asyncio
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

async def test_admin_endpoint():
    """Test admin endpoint with different API key scenarios"""
    
    print(f"Admin API Key from settings: {repr(settings.admin_api_key)}")
    print(f"Type: {type(settings.admin_api_key)}")
    print(f"Is None: {settings.admin_api_key is None}")
    print(f"Not truthy: {not settings.admin_api_key}")
    print()
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: No API key
        print("Test 1: Request without API key header")
        try:
            response = await client.post(
                f"{base_url}/api/v1/admin/boxes",
                json={"product_name": "Test Box", "set_name": "Test"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
        print()
        
        # Test 2: With API key
        print("Test 2: Request with API key header (dev-key)")
        try:
            response = await client.post(
                f"{base_url}/api/v1/admin/boxes",
                json={"product_name": "Test Box", "set_name": "Test"},
                headers={"X-API-Key": "dev-key"}
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
        except Exception as e:
            print(f"Error: {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_admin_endpoint())

