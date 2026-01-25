"""
Verify Database Migrations
Checks if the users table exists and has all required columns
"""

import asyncio
from sqlalchemy import text, inspect
from app.database import AsyncSessionLocal, engine
from app.models.user import User
from app.models import Base


async def check_users_table():
    """Check if users table exists and has required columns"""
    print("🔍 Checking database migrations...")
    print()
    
    required_columns = {
        'id': 'UUID',
        'email': 'String',
        'hashed_password': 'String',
        'is_active': 'Boolean',
        'is_superuser': 'Boolean',
        'role': 'String',
        'token_version': 'Integer',
        'created_at': 'DateTime',
        'updated_at': 'DateTime',
        'trial_started_at': 'DateTime',
        'trial_ended_at': 'DateTime',
        'subscription_status': 'String',
        'stripe_customer_id': 'String',
        'stripe_subscription_id': 'String',
        'last_login_at': 'DateTime',
    }
    
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
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ Users table does NOT exist!")
                print("   Run: alembic upgrade head")
                return False
            
            print("✅ Users table exists")
            
            # Get all columns in users table
            result = await db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'users'
                ORDER BY column_name;
            """))
            columns = {row[0]: row[1] for row in result.fetchall()}
            
            print(f"   Found {len(columns)} columns")
            print()
            
            # Check for required columns
            missing_columns = []
            found_columns = []
            
            for col_name, col_type in required_columns.items():
                if col_name in columns:
                    found_columns.append(col_name)
                    print(f"   ✅ {col_name} ({columns[col_name]})")
                else:
                    missing_columns.append(col_name)
                    print(f"   ❌ {col_name} - MISSING")
            
            if missing_columns:
                print()
                print(f"❌ Missing {len(missing_columns)} required columns:")
                for col in missing_columns:
                    print(f"   - {col}")
                print()
                print("   Run: alembic upgrade head")
                return False
            
            # Check alembic version
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """))
            alembic_table_exists = result.scalar()
            
            if alembic_table_exists:
                result = await db.execute(text("SELECT version_num FROM alembic_version;"))
                current_version = result.scalar()
                print()
                print(f"✅ Alembic version table exists")
                print(f"   Current migration version: {current_version}")
            else:
                print()
                print("⚠️  Alembic version table does not exist")
                print("   This might mean migrations haven't been initialized")
            
            # Check indexes
            result = await db.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'users' 
                AND schemaname = 'public';
            """))
            indexes = [row[0] for row in result.fetchall()]
            
            print()
            print(f"✅ Found {len(indexes)} indexes on users table:")
            for idx in indexes:
                print(f"   - {idx}")
            
            # Check for unique constraint on email
            result = await db.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'users' 
                AND constraint_type = 'UNIQUE'
                AND constraint_name LIKE '%email%';
            """))
            email_unique = result.scalar()
            
            if email_unique:
                print()
                print(f"✅ Email unique constraint exists: {email_unique}")
            else:
                print()
                print("⚠️  Email unique constraint not found")
            
            print()
            print("=" * 60)
            print("✅ All required columns are present!")
            print("✅ Users table is ready for authentication")
            print("=" * 60)
            return True
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_sample_user():
    """Check if any users exist in the database"""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM users;"))
            count = result.scalar()
            print()
            print(f"📊 Users in database: {count}")
            if count > 0:
                result = await db.execute(text("""
                    SELECT email, subscription_status, role, is_active
                    FROM users 
                    LIMIT 5;
                """))
                users = result.fetchall()
                print("   Sample users:")
                for user in users:
                    print(f"   - {user[0]} (status: {user[1]}, role: {user[2]}, active: {user[3]})")
    except Exception as e:
        print(f"⚠️  Could not check users: {e}")


async def main():
    """Main verification function"""
    success = await check_users_table()
    await check_sample_user()
    
    if success:
        print()
        print("🎉 Migration verification complete!")
        return 0
    else:
        print()
        print("⚠️  Some issues found. Please run migrations:")
        print("   alembic upgrade head")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
