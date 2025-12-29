#!/usr/bin/env python3
"""
Test database connection
Run this script to verify your database connection is working
"""

import asyncio
import sys
from sqlalchemy import text

# Add parent directory to path to import app modules
sys.path.insert(0, str(__file__).replace("/scripts/test_db_connection.py", ""))

from app.database import engine, init_db
from app.config import settings


async def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    print(f"Database URL: {settings.database_url[:50]}...")
    print()
    
    try:
        # Test basic connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL!")
            print(f"   Version: {version[:50]}...")
            print()
            
            # Test database exists and is accessible
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"✅ Current database: {db_name}")
            print()
            
            # Test if we can create tables (permissions check)
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"✅ Current user: {user}")
            print()
            
        print("✅ Database connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test FAILED!")
        print(f"   Error: {str(e)}")
        print()
        print("Troubleshooting:")
        print("1. Check that DATABASE_URL in .env is correct")
        print("2. Verify PostgreSQL is running (if local)")
        print("3. Check that the database exists")
        print("4. Verify username/password are correct")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)

