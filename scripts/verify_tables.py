#!/usr/bin/env python3
"""
Verify database tables were created
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import settings

# Convert async URL to sync for direct connection
database_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")

def verify_tables():
    """Verify all tables exist"""
    print("Connecting to database...")
    print(f"URL: {database_url[:50]}...")
    print()
    
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Get list of tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            
            print(f"✅ Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table}")
            print()
            
            # Expected tables
            expected_tables = [
                'alembic_version',
                'booster_boxes',
                'box_metrics_unified',
                'ebay_box_metrics_daily',
                'ebay_sales_raw',
                'tcg_box_metrics_daily',
                'tcg_listing_changes',
                'tcg_listings_raw',
                'user_favorites',
                'users'
            ]
            
            print("Checking expected tables...")
            missing = []
            for expected in expected_tables:
                if expected in tables:
                    print(f"   ✅ {expected}")
                else:
                    print(f"   ❌ {expected} - MISSING")
                    missing.append(expected)
            
            if missing:
                print()
                print(f"❌ {len(missing)} tables are missing!")
                return False
            else:
                print()
                print("✅ All expected tables exist!")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_tables()
    sys.exit(0 if success else 1)

