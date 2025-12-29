#!/usr/bin/env python3
"""
Test Migration Setup
Verify that Alembic configuration is correct
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    print("Testing migration setup...")
    print()
    
    # Test 1: Import settings
    print("1. Testing settings import...")
    from app.config import settings
    print(f"   ✅ Settings loaded")
    print(f"   Database URL: {settings.database_url[:50]}...")
    print()
    
    # Test 2: Check URL conversion
    print("2. Testing URL conversion for Alembic...")
    database_url = settings.database_url
    if "postgresql+asyncpg://" in database_url:
        sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        print(f"   ✅ Async URL detected")
        print(f"   Original: {database_url[:50]}...")
        print(f"   Converted: {sync_url[:50]}...")
        if sync_url.startswith("postgresql://"):
            print(f"   ✅ URL conversion correct")
        else:
            print(f"   ❌ URL conversion failed")
            sys.exit(1)
    else:
        print(f"   ℹ️  URL is already sync (no conversion needed)")
    print()
    
    # Test 3: Import models
    print("3. Testing model imports...")
    from app.models import Base, BoosterBox, UnifiedBoxMetrics
    print(f"   ✅ Models imported successfully")
    print(f"   Base metadata: {Base.metadata}")
    print()
    
    # Test 4: Check if psycopg2 is available
    print("4. Testing psycopg2 (sync driver) availability...")
    try:
        import psycopg2
        print(f"   ✅ psycopg2 available (version: {psycopg2.__version__})")
    except ImportError:
        print(f"   ⚠️  psycopg2 not found - you may need to install it:")
        print(f"      pip install psycopg2-binary")
    print()
    
    # Test 5: Check alembic env.py can be imported
    print("5. Testing alembic env.py import...")
    try:
        # This is tricky because env.py uses alembic context
        # Just check if file exists and has correct structure
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations", "env.py")
        with open(env_path) as f:
            content = f.read()
            if "postgresql+asyncpg://" in content and "replace" in content.lower():
                print(f"   ✅ env.py has URL conversion logic")
            else:
                print(f"   ⚠️  env.py may not have URL conversion")
    except Exception as e:
        print(f"   ⚠️  Could not check env.py: {e}")
    print()
    
    print("✅ Migration setup tests complete!")
    print()
    print("Next steps:")
    print("1. If psycopg2 is missing: pip install psycopg2-binary")
    print("2. Run migration: alembic upgrade head")
    
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

