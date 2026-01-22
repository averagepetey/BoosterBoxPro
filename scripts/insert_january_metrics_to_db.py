"""
Insert January 20-21, 2026 metrics into the database
This updates the unified_box_metrics table for live dashboard display
"""

import asyncio
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from app.database import AsyncSessionLocal, engine
from app.models.booster_box import BoosterBox
from app.models.unified_box_metrics import UnifiedBoxMetrics


# Data collected from screenshots - January 20, 2026
january_20_data = {
    "OP-13": {
        "floor_price_usd": 541.95,
        "active_listings_count": 49,
        "boxes_sold_per_day": 26,
        "daily_volume_usd": 14848.86,
    },
    "OP-09": {
        "floor_price_usd": 622.62,
        "active_listings_count": 73,
        "boxes_sold_per_day": 18,
        "daily_volume_usd": 11207.10,
    },
    "EB-01": {
        "floor_price_usd": 847.31,
        "active_listings_count": 12,
        "boxes_sold_per_day": 3,
        "daily_volume_usd": 2541.94,
    },
    "OP-11": {
        "floor_price_usd": 418.01,
        "active_listings_count": 105,
        "boxes_sold_per_day": 25,
        "daily_volume_usd": 10450.37,
    },
    "OP-01 Blue": {
        "floor_price_usd": 6510.97,
        "active_listings_count": 11,
        "boxes_sold_per_day": 0,
        "daily_volume_usd": 0,
    },
    "PRB-01": {
        "floor_price_usd": 946.99,
        "active_listings_count": 40,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 1893.98,
    },
    "OP-01 White": {
        "floor_price_usd": 2041.93,
        "active_listings_count": 11,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 4083.85,
    },
    "OP-05": {
        "floor_price_usd": 1037.50,
        "active_listings_count": 18,
        "boxes_sold_per_day": 4,
        "daily_volume_usd": 4150.00,
    },
    "OP-10": {
        "floor_price_usd": 229.96,
        "active_listings_count": 520,
        "boxes_sold_per_day": 13,
        "daily_volume_usd": 2989.52,
    },
    "PRB-02": {
        "floor_price_usd": 332.73,
        "active_listings_count": 64,
        "boxes_sold_per_day": 23,
        "daily_volume_usd": 7652.78,
    },
    "OP-07": {
        "floor_price_usd": 306.41,
        "active_listings_count": 71,
        "boxes_sold_per_day": 4,
        "daily_volume_usd": 1225.62,
    },
    "OP-12": {
        "floor_price_usd": 212.60,
        "active_listings_count": 87,
        "boxes_sold_per_day": 52,
        "daily_volume_usd": 11054.95,
    },
    "OP-04": {
        "floor_price_usd": 605.42,
        "active_listings_count": 22,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 1210.84,
    },
    "OP-06": {
        "floor_price_usd": 342.22,
        "active_listings_count": 48,
        "boxes_sold_per_day": 24,
        "daily_volume_usd": 8213.31,
    },
    "EB-02": {
        "floor_price_usd": 541.72,
        "active_listings_count": 36,
        "boxes_sold_per_day": 16,
        "daily_volume_usd": 8667.55,
    },
    "OP-02": {
        "floor_price_usd": 637.48,
        "active_listings_count": 22,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 1274.95,
    },
    "OP-08": {
        "floor_price_usd": 206.67,
        "active_listings_count": 42,
        "boxes_sold_per_day": 18,
        "daily_volume_usd": 3720.12,
    },
    "OP-03": {
        "floor_price_usd": 795.59,
        "active_listings_count": 30,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 1591.18,
    },
}

# Data collected from screenshots - January 21, 2026
january_21_data = {
    "OP-13": {
        "floor_price_usd": 570.58,
        "active_listings_count": 49,
        "boxes_sold_per_day": 12,
        "daily_volume_usd": 6846.93,
    },
    "OP-09": {
        "floor_price_usd": 622.62,
        "active_listings_count": 73,
        "boxes_sold_per_day": 0,
        "daily_volume_usd": 0,
    },
    "EB-01": {
        "floor_price_usd": 847.31,
        "active_listings_count": 12,
        "boxes_sold_per_day": 0,
        "daily_volume_usd": 0,
    },
    "OP-11": {
        "floor_price_usd": 402.50,
        "active_listings_count": 105,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 805.00,
    },
    "OP-01 Blue": {
        "floor_price_usd": 6510.97,
        "active_listings_count": 11,
        "boxes_sold_per_day": 0,
        "daily_volume_usd": 0,
    },
    "PRB-01": {
        "floor_price_usd": 840.00,
        "active_listings_count": 40,
        "boxes_sold_per_day": 1,
        "daily_volume_usd": 840.00,
    },
    "OP-01 White": {
        "floor_price_usd": 2113.38,
        "active_listings_count": 11,
        "boxes_sold_per_day": 1,
        "daily_volume_usd": 2113.38,
    },
    "OP-05": {
        "floor_price_usd": 1097.45,
        "active_listings_count": 18,
        "boxes_sold_per_day": 11,
        "daily_volume_usd": 12071.91,
    },
    "OP-10": {
        "floor_price_usd": 232.18,
        "active_listings_count": 520,
        "boxes_sold_per_day": 4,
        "daily_volume_usd": 928.73,
    },
    "PRB-02": {
        "floor_price_usd": 332.33,
        "active_listings_count": 64,
        "boxes_sold_per_day": 3,
        "daily_volume_usd": 997.00,
    },
    "OP-07": {
        "floor_price_usd": 306.33,
        "active_listings_count": 71,
        "boxes_sold_per_day": 3,
        "daily_volume_usd": 919.00,
    },
    "OP-12": {
        "floor_price_usd": 214.95,
        "active_listings_count": 87,
        "boxes_sold_per_day": 6,
        "daily_volume_usd": 1289.70,
    },
    "OP-04": {
        "floor_price_usd": 555.00,
        "active_listings_count": 22,
        "boxes_sold_per_day": 1,
        "daily_volume_usd": 555.00,
    },
    "OP-06": {
        "floor_price_usd": 339.88,
        "active_listings_count": 48,
        "boxes_sold_per_day": 1,
        "daily_volume_usd": 339.88,
    },
    "EB-02": {
        "floor_price_usd": 649.49,
        "active_listings_count": 36,
        "boxes_sold_per_day": 1,
        "daily_volume_usd": 649.49,
    },
    "OP-02": {
        "floor_price_usd": 560.00,
        "active_listings_count": 22,
        "boxes_sold_per_day": 1,
        "daily_volume_usd": 560.00,
    },
    "OP-08": {
        "floor_price_usd": 343.33,
        "active_listings_count": 42,
        "boxes_sold_per_day": 3,
        "daily_volume_usd": 1029.99,
    },
    "OP-03": {
        "floor_price_usd": 763.33,
        "active_listings_count": 30,
        "boxes_sold_per_day": 2,
        "daily_volume_usd": 1526.65,
    },
}


def match_box_to_key(product_name: str) -> str:
    """Match a product name to our data key"""
    import re
    
    # Check for OP-01 variants first
    if "OP-01" in product_name.upper() or "OP01" in product_name.upper():
        if "Blue" in product_name:
            return "OP-01 Blue"
        elif "White" in product_name:
            return "OP-01 White"
    
    # Extract set code
    match = re.search(r'(OP|EB|PRB)-?(\d+)', product_name.upper())
    if match:
        prefix = match.group(1)
        number = match.group(2)
        return f"{prefix}-{number.zfill(2)}"
    
    return None


async def insert_metrics():
    """Insert metrics into the database"""
    
    async with AsyncSessionLocal() as db:
        # Get all booster boxes from the database
        stmt = select(BoosterBox)
        result = await db.execute(stmt)
        db_boxes = result.scalars().all()
        
        print(f"Found {len(db_boxes)} boxes in database")
        
        # Process both dates
        for metric_date, day_data in [
            (date(2026, 1, 20), january_20_data),
            (date(2026, 1, 21), january_21_data)
        ]:
            print(f"\n📅 Processing {metric_date}...")
            
            for db_box in db_boxes:
                # Skip test boxes
                if "(Test)" in db_box.product_name:
                    continue
                
                # Match box to our data key
                key = match_box_to_key(db_box.product_name)
                if not key or key not in day_data:
                    continue
                
                box_data = day_data[key]
                
                # Check if entry already exists
                check_stmt = select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.booster_box_id == db_box.id,
                    UnifiedBoxMetrics.metric_date == metric_date
                )
                existing = await db.execute(check_stmt)
                existing_entry = existing.scalar_one_or_none()
                
                if existing_entry:
                    # Update existing entry
                    existing_entry.floor_price_usd = Decimal(str(box_data["floor_price_usd"]))
                    existing_entry.active_listings_count = box_data["active_listings_count"]
                    existing_entry.boxes_sold_per_day = Decimal(str(box_data["boxes_sold_per_day"]))
                    existing_entry.unified_volume_usd = Decimal(str(box_data["daily_volume_usd"]))
                    existing_entry.unified_volume_7d_ema = Decimal(str(box_data["daily_volume_usd"]))  # Use same as daily for now
                    print(f"  🔄 Updated {key}")
                else:
                    # Create new entry
                    new_metrics = UnifiedBoxMetrics(
                        booster_box_id=db_box.id,
                        metric_date=metric_date,
                        floor_price_usd=Decimal(str(box_data["floor_price_usd"])),
                        floor_price_1d_change_pct=Decimal("0"),
                        active_listings_count=box_data["active_listings_count"],
                        boxes_sold_per_day=Decimal(str(box_data["boxes_sold_per_day"])),
                        unified_volume_usd=Decimal(str(box_data["daily_volume_usd"])),
                        unified_volume_7d_ema=Decimal(str(box_data["daily_volume_usd"])),
                        liquidity_score=Decimal("0.5"),
                        days_to_20pct_increase=Decimal(str(box_data["active_listings_count"] / max(box_data["boxes_sold_per_day"], 0.1))),
                    )
                    db.add(new_metrics)
                    print(f"  ✅ Created {key}")
            
            await db.commit()
        
        print("\n✅ Database updated successfully!")


if __name__ == "__main__":
    print("=" * 60)
    print("📊 Inserting January 20-21, 2026 Metrics to Database")
    print("=" * 60)
    
    asyncio.run(insert_metrics())
    
    print("\n" + "=" * 60)
    print("✅ Database import complete!")
    print("=" * 60)

