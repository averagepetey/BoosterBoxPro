"""
Add Migration 002 Columns
Manually add columns from migration 002 to the database
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def add_migration_002_columns():
    """Add columns from migration 002"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if columns already exist
            result = await db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'box_metrics_unified'
            """))
            existing_columns = {row[0] for row in result}
            
            print("Checking existing columns...")
            print(f"Existing columns: {sorted(existing_columns)}")
            print()
            
            # Add columns if they don't exist
            columns_to_add = {
                'unified_volume_30d_sma': 'NUMERIC(12, 2)',
                'volume_mom_change_pct': 'NUMERIC(6, 2)',
                'avg_boxes_added_per_day': 'NUMERIC(8, 2)'
            }
            
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    print(f"Adding column: {col_name} ({col_type})")
                    await db.execute(text(f"""
                        ALTER TABLE box_metrics_unified 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    print(f"  ✅ Added {col_name}")
                else:
                    print(f"  ℹ️  Column {col_name} already exists")
            
            await db.commit()
            print("\n✅ Successfully added columns!")
            print("\nNext step: Run 'alembic stamp 002' to mark migration 002 as complete")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(add_migration_002_columns())

