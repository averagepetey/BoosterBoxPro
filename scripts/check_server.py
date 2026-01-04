"""
Quick diagnostic script to check server and database connectivity
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import init_db, engine
from sqlalchemy import text


async def check_database():
    """Check database connection"""
    print("=" * 60)
    print("DATABASE CHECK")
    print("=" * 60)
    print(f"Database URL: {settings.database_url[:50]}...")
    print()
    
    try:
        await init_db()
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection: FAILED")
        print(f"   Error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Verify database credentials are correct")
        return False


async def check_server():
    """Check if server is accessible"""
    print()
    print("=" * 60)
    print("SERVER CHECK")
    print("=" * 60)
    
    import httpx
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Server is running and responding")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return False
    except httpx.ConnectError:
        print("❌ Cannot connect to server at http://localhost:8000")
        print("   Server may not be running")
        print()
        print("To start the server, run:")
        print("   python main.py")
        print("   or")
        print("   uvicorn main:app --reload --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False


async def main():
    """Run all checks"""
    print("\n🔍 BoosterBoxPro Server Diagnostics\n")
    
    db_ok = await check_database()
    server_ok = await check_server()
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Database: {'✅ OK' if db_ok else '❌ FAILED'}")
    print(f"Server:   {'✅ OK' if server_ok else '❌ FAILED'}")
    
    if not db_ok or not server_ok:
        print()
        print("⚠️  Some checks failed. See troubleshooting above.")
        sys.exit(1)
    else:
        print()
        print("✅ All checks passed!")


if __name__ == "__main__":
    asyncio.run(main())

