#!/usr/bin/env python3
"""
List all booster boxes with their IDs for selection
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv

from app.models.booster_box import BoosterBox

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    sys.exit(1)

async def list_boxes():
    """List all boxes with IDs"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(BoosterBox).order_by(BoosterBox.product_name))
        all_boxes = result.scalars().all()
        
        print(f"\n📦 Total boxes in database: {len(all_boxes)}\n")
        print("=" * 80)
        print("All Booster Boxes (sorted by product name)")
        print("=" * 80)
        
        for idx, box in enumerate(all_boxes, 1):
            print(f"\n{idx}. {box.product_name}")
            print(f"   ID: {box.id}")
            print(f"   Set Name: {box.set_name or 'N/A'}")
            print(f"   Game Type: {box.game_type or 'N/A'}")
            print(f"   Release Date: {box.release_date or 'N/A'}")
            if box.external_product_id:
                print(f"   External ID: {box.external_product_id}")
        
        print("\n" + "=" * 80)
        print(f"Total: {len(all_boxes)} boxes")
        print("=" * 80)
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_boxes())

