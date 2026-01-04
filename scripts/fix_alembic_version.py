"""
Fix Alembic Version Table
Directly update the alembic_version table to fix the migration chain issue
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from sqlalchemy import text


async def fix_alembic_version():
    """Fix the alembic_version table by setting it to revision '002'"""
    async with AsyncSessionLocal() as db:
        try:
            # Check current version
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar_one_or_none()
            print(f"Current alembic_version in database: {current_version}")
            
            # Update to revision '002'
            await db.execute(text("UPDATE alembic_version SET version_num = '002'"))
            await db.commit()
            
            print("✅ Successfully updated alembic_version to '002'")
            print("\nNow you can run: alembic upgrade head")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error: {e}")
            print("\nTrying to insert if table is empty...")
            try:
                await db.execute(text("INSERT INTO alembic_version (version_num) VALUES ('002')"))
                await db.commit()
                print("✅ Successfully inserted alembic_version '002'")
            except Exception as e2:
                await db.rollback()
                print(f"❌ Error inserting: {e2}")


if __name__ == "__main__":
    asyncio.run(fix_alembic_version())

