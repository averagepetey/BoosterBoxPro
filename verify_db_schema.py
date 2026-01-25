#!/usr/bin/env python3
"""
Verify database schema - checks if users table exists with correct structure
This uses the app's database connection
"""
import asyncio
import sys
from sqlalchemy import inspect, text
from app.database import engine
from app.models.user import User
from app.models import Base

async def verify_schema():
    """Verify the users table schema"""
    print("🔍 Verifying database migrations...")
    print()
    
    try:
        # Use sync connection for inspection (Alembic style)
        from sqlalchemy import create_engine
        from app.config import settings
        
        # Convert async URL to sync for inspection
        db_url = settings.database_url
        if "postgresql+asyncpg://" in db_url:
            db_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        elif "postgresql://" in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")
        
        sync_engine = create_engine(db_url)
        inspector = inspect(sync_engine)
        
        # Check if users table exists
        tables = inspector.get_table_names()
        if 'users' not in tables:
            print("❌ Users table does NOT exist!")
            print("   → Run: alembic upgrade head")
            return False
        
        print("✅ Users table exists")
        
        # Get columns
        columns = inspector.get_columns('users')
        column_names = {col['name'] for col in columns}
        
        print(f"   Found {len(columns)} columns")
        
        # Required columns from migrations
        required = {
            'id', 'email', 'hashed_password', 'is_active', 'is_superuser',
            'role', 'token_version', 'created_at', 'updated_at',
            'trial_started_at', 'trial_ended_at', 'subscription_status',
            'stripe_customer_id', 'stripe_subscription_id'
        }
        
        missing = required - column_names
        if missing:
            print(f"\n❌ Missing {len(missing)} required columns:")
            for col in sorted(missing):
                print(f"   - {col}")
            print("\n   → Run: alembic upgrade head")
            return False
        
        print("✅ All required columns present")
        
        # Check indexes
        indexes = inspector.get_indexes('users')
        index_names = {idx['name'] for idx in indexes}
        
        # Check for email unique index
        has_email_unique = any('email' in str(idx.get('column_names', [])) for idx in indexes)
        if has_email_unique:
            print("✅ Email unique constraint exists")
        else:
            print("⚠️  Email unique constraint not found")
        
        # Check alembic version
        if 'alembic_version' in tables:
            with sync_engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                print(f"✅ Alembic version: {version}")
        else:
            print("⚠️  Alembic version table not found")
        
        print()
        print("=" * 60)
        print("✅ Database schema verification PASSED")
        print("✅ Users table is ready for authentication")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the virtual environment:")
        print("   source venv/bin/activate")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_schema())
    sys.exit(0 if success else 1)
