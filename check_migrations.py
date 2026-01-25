"""
Quick migration check - uses existing app database connection
"""
import asyncio
import sys
from sqlalchemy import text
from app.database import AsyncSessionLocal

async def check():
    try:
        async with AsyncSessionLocal() as db:
            # Check if users table exists
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            exists = result.scalar()
            
            if not exists:
                print("❌ Users table does NOT exist")
                print("   Run: alembic upgrade head")
                return False
            
            # Get column count
            result = await db.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns
                WHERE table_name = 'users';
            """))
            col_count = result.scalar()
            
            # Check for key columns
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name = 'users';
            """))
            columns = {row[0] for row in result.fetchall()}
            
            required = {'id', 'email', 'hashed_password', 'role', 'token_version', 
                       'trial_started_at', 'trial_ended_at', 'subscription_status',
                       'stripe_customer_id', 'stripe_subscription_id'}
            missing = required - columns
            
            # Check alembic version
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'alembic_version'
                );
            """))
            alembic_exists = result.scalar()
            
            version = None
            if alembic_exists:
                result = await db.execute(text("SELECT version_num FROM alemic_version;"))
                try:
                    version = result.scalar()
                except:
                    pass
            
            print(f"✅ Users table exists ({col_count} columns)")
            
            if missing:
                print(f"❌ Missing columns: {', '.join(missing)}")
                print("   Run: alembic upgrade head")
                return False
            else:
                print("✅ All required columns present")
            
            if version:
                print(f"✅ Alembic version: {version}")
            else:
                print("⚠️  Could not read alembic version")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(check())
    sys.exit(0 if result else 1)
