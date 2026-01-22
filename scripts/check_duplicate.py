"""
Check for duplicate data before adding
Use this to verify if data already exists for a box/date combination
"""

import asyncio
import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select


async def check_duplicate_data(
    box_name: str,
    metric_date: str,
    floor_price: float = None,
    listings: int = None,
    sold: int = None,
    volume: float = None,
    market_cap: float = None,
    added: int = None,
) -> dict:
    """
    Check if data already exists and compare values
    
    Returns:
        {
            "exists": bool,
            "is_duplicate": bool,
            "existing_data": {...},
            "differences": {...},
            "message": str
        }
    """
    async with AsyncSessionLocal() as db:
        # Find box
        stmt = select(BoosterBox).where(BoosterBox.product_name.ilike(f"%{box_name}%"))
        result = await db.execute(stmt)
        box = result.scalar_one_or_none()
        
        if not box:
            return {
                "exists": False,
                "is_duplicate": False,
                "message": f"Box '{box_name}' not found in database"
            }
        
        # Parse date
        try:
            date_obj = date.fromisoformat(metric_date)
        except ValueError:
            return {
                "exists": False,
                "is_duplicate": False,
                "message": f"Invalid date format: {metric_date}"
            }
        
        # Check for existing metrics
        stmt = select(UnifiedBoxMetrics).where(
            UnifiedBoxMetrics.booster_box_id == box.id,
            UnifiedBoxMetrics.metric_date == date_obj
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if not existing:
            return {
                "exists": False,
                "is_duplicate": False,
                "message": f"No existing data for {box.product_name} on {metric_date}. Safe to add."
            }
        
        # Compare values
        existing_data = {
            "floor_price_usd": float(existing.floor_price_usd) if existing.floor_price_usd else None,
            "active_listings_count": existing.active_listings_count,
            "boxes_sold_per_day": float(existing.boxes_sold_per_day) if existing.boxes_sold_per_day else None,
            "unified_volume_usd": float(existing.unified_volume_usd) if existing.unified_volume_usd else None,
            "visible_market_cap_usd": float(existing.visible_market_cap_usd) if existing.visible_market_cap_usd else None,
            "boxes_added_today": existing.boxes_added_today,
        }
        
        new_data = {
            "floor_price_usd": floor_price,
            "active_listings_count": listings,
            "boxes_sold_per_day": sold,
            "unified_volume_usd": volume,
            "visible_market_cap_usd": market_cap,
            "boxes_added_today": added,
        }
        
        differences = {}
        is_duplicate = True
        tolerance = 0.01
        
        comparison_fields = {
            "floor_price_usd": ("floor_price_usd", tolerance),
            "active_listings_count": ("active_listings_count", 0),
            "boxes_sold_today": ("boxes_sold_per_day", 0),
            "daily_volume_usd": ("unified_volume_usd", tolerance),
            "visible_market_cap_usd": ("visible_market_cap_usd", tolerance),
            "boxes_added_today": ("boxes_added_today", 0),
        }
        
        for new_key, (existing_key, tol) in comparison_fields.items():
            new_value = new_data.get(new_key)
            existing_value = existing_data.get(existing_key)
            
            # Skip if both are None
            if new_value is None and existing_value is None:
                continue
            
            # If one is None and the other isn't, it's different
            if new_value is None or existing_value is None:
                differences[new_key] = {
                    "existing": existing_value,
                    "new": new_value,
                    "changed": True
                }
                is_duplicate = False
                continue
            
            # Compare numeric values with tolerance
            if isinstance(new_value, (int, float)) and isinstance(existing_value, (int, float)):
                diff = abs(new_value - existing_value)
                if diff > tol:
                    differences[new_key] = {
                        "existing": existing_value,
                        "new": new_value,
                        "difference": diff,
                        "changed": True
                    }
                    is_duplicate = False
        
        if is_duplicate:
            message = f"✅ Data already exists and matches exactly for {box.product_name} on {metric_date}. No update needed."
        else:
            changed_fields = list(differences.keys())
            message = f"⚠️  Data exists but differs in: {', '.join(changed_fields)}"
        
        return {
            "exists": True,
            "is_duplicate": is_duplicate,
            "existing_data": existing_data,
            "differences": differences,
            "message": message,
            "box_name": box.product_name
        }


async def main():
    """CLI for checking duplicates"""
    if len(sys.argv) < 3:
        print("Usage: python check_duplicate.py <box_name> <date> [floor_price] [listings] [sold] [volume] [market_cap] [added]")
        print("Example: python check_duplicate.py OP-01 2024-12-29 120.50 45 3 361.50 5422.50 2")
        sys.exit(1)
    
    box_name = sys.argv[1]
    metric_date = sys.argv[2]
    
    floor_price = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else None
    listings = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None
    sold = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] else None
    volume = float(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6] else None
    market_cap = float(sys.argv[7]) if len(sys.argv) > 7 and sys.argv[7] else None
    added = int(sys.argv[8]) if len(sys.argv) > 8 and sys.argv[8] else None
    
    result = await check_duplicate_data(
        box_name=box_name,
        metric_date=metric_date,
        floor_price=floor_price,
        listings=listings,
        sold=sold,
        volume=volume,
        market_cap=market_cap,
        added=added,
    )
    
    print("\n" + "=" * 60)
    print("Duplicate Check Result")
    print("=" * 60)
    print(result["message"])
    
    if result.get("existing_data"):
        print("\nExisting Data:")
        for key, value in result["existing_data"].items():
            if value is not None:
                print(f"  {key}: {value}")
    
    if result.get("differences"):
        print("\nDifferences:")
        for key, diff in result["differences"].items():
            print(f"  {key}:")
            print(f"    Existing: {diff['existing']}")
            print(f"    New: {diff['new']}")
            if 'difference' in diff:
                print(f"    Difference: {diff['difference']}")
    
    if result["is_duplicate"]:
        print("\n❌ DUPLICATE - Will NOT add this data")
    elif result["exists"]:
        print("\n⚠️  DIFFERENT - Will UPDATE existing data")
    else:
        print("\n✅ NEW - Safe to add this data")


if __name__ == "__main__":
    asyncio.run(main())





