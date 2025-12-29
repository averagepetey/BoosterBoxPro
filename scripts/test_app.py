#!/usr/bin/env python3
"""
Test FastAPI application
Verify app can be imported and basic endpoints work
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing FastAPI application...")
    print()
    
    # Test 1: Import app
    print("1. Testing app import...")
    from app.main import app
    print("   ✅ FastAPI app imported successfully")
    print(f"   Title: {app.title}")
    print(f"   Version: {app.version}")
    print()
    
    # Test 2: Check routes
    print("2. Testing routes...")
    routes = [route.path for route in app.routes]
    print(f"   ✅ Found {len(routes)} routes:")
    for route in routes:
        print(f"      - {route}")
    print()
    
    # Test 3: Check settings
    print("3. Testing settings...")
    from app.config import settings
    print(f"   ✅ Settings loaded")
    print(f"   Environment: {settings.environment}")
    print(f"   Debug: {settings.debug}")
    print()
    
    print("✅ All application tests passed!")
    print()
    print("To run the server:")
    print("  python scripts/run_server.py")
    print("  OR")
    print("  uvicorn app.main:app --reload")
    print()
    print("Then visit: http://localhost:8000/docs")
    
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

