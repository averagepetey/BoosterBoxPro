"""
Manual Data Entry Script
Enter data extracted from screenshots into the database
"""

import json
import sys
from pathlib import Path
from datetime import date
from typing import Optional

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_box_by_name(db: AsyncSession, product_name: str) -> Optional[BoosterBox]:
    """Find a box by product name (fuzzy match)"""
    stmt = select(BoosterBox).where(BoosterBox.product_name.ilike(f"%{product_name}%"))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def check_before_add(
    db: AsyncSession,
    box_name: str,
    metric_date: str,
    floor_price_usd: Optional[float] = None,
    active_listings_count: Optional[int] = None,
    boxes_sold_today: Optional[int] = None,
    daily_volume_usd: Optional[float] = None,
    visible_market_cap_usd: Optional[float] = None,
    boxes_added_today: Optional[int] = None,
) -> dict:
    """
    Check for duplicates before adding (used by AI assistant)
    Returns duplicate check result
    """
    from scripts.check_duplicate import check_duplicate_data
    return await check_duplicate_data(
        box_name=box_name,
        metric_date=metric_date,
        floor_price=floor_price_usd,
        listings=active_listings_count,
        sold=boxes_sold_today,
        volume=daily_volume_usd,
        market_cap=visible_market_cap_usd,
        added=boxes_added_today,
    )


async def add_metrics(
    db: AsyncSession,
    box_name: str,
    metric_date: str,
    floor_price_usd: Optional[float] = None,
    active_listings_count: Optional[int] = None,
    boxes_sold_today: Optional[int] = None,
    daily_volume_usd: Optional[float] = None,
    visible_market_cap_usd: Optional[float] = None,
    boxes_added_today: Optional[int] = None,
    skip_duplicate_check: bool = False,
) -> dict:
    """
    Add metrics for a box on a specific date
    
    Args:
        db: Database session
        box_name: Product name (e.g., "OP-01", "One Piece OP-02")
        metric_date: Date in YYYY-MM-DD format
        floor_price_usd: Floor price in USD
        active_listings_count: Number of active listings
        boxes_sold_today: Boxes sold today
        daily_volume_usd: Daily volume in USD
        visible_market_cap_usd: Visible market cap in USD
        boxes_added_today: Boxes added today
        
    Returns:
        Dictionary with success status and message
    """
    # Find the box
    box = await get_box_by_name(db, box_name)
    if not box:
        return {
            "success": False,
            "error": f"Box '{box_name}' not found. Available boxes: {await list_all_boxes(db)}"
        }
    
    # Parse date
    try:
        date_obj = date.fromisoformat(metric_date)
    except ValueError:
        return {"success": False, "error": f"Invalid date format: {metric_date}. Use YYYY-MM-DD"}
    
    # Check for duplicates first (unless explicitly skipped)
    if not skip_duplicate_check:
        duplicate_check = await check_before_add(
            db=db,
            box_name=box_name,
            metric_date=metric_date,
            floor_price_usd=floor_price_usd,
            active_listings_count=active_listings_count,
            boxes_sold_today=boxes_sold_today,
            daily_volume_usd=daily_volume_usd,
            visible_market_cap_usd=visible_market_cap_usd,
            boxes_added_today=boxes_added_today,
        )
        
        # If exact duplicate, don't add
        if duplicate_check.get("is_duplicate"):
            return {
                "success": False,
                "error": "DUPLICATE_DATA",
                "message": duplicate_check["message"],
                "is_duplicate": True
            }
    
    # Check if data already exists
    stmt = select(UnifiedBoxMetrics).where(
        UnifiedBoxMetrics.booster_box_id == box.id,
        UnifiedBoxMetrics.metric_date == date_obj
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing record
        if floor_price_usd is not None:
            existing.floor_price_usd = floor_price_usd
        if active_listings_count is not None:
            existing.active_listings_count = active_listings_count
        if boxes_sold_today is not None:
            existing.boxes_sold_per_day = boxes_sold_today
        if daily_volume_usd is not None:
            existing.unified_volume_usd = daily_volume_usd
        if visible_market_cap_usd is not None:
            existing.visible_market_cap_usd = visible_market_cap_usd
        if boxes_added_today is not None:
            existing.boxes_added_today = boxes_added_today
        
        await db.commit()
        return {
            "success": True,
            "message": f"Updated existing metrics for {box.product_name} on {metric_date}",
            "action": "updated"
        }
    else:
        # Create new record
        new_metrics = UnifiedBoxMetrics(
            booster_box_id=box.id,
            metric_date=date_obj,
            floor_price_usd=floor_price_usd,
            active_listings_count=active_listings_count,
            boxes_sold_per_day=boxes_sold_today,
            unified_volume_usd=daily_volume_usd,
            visible_market_cap_usd=visible_market_cap_usd,
            boxes_added_today=boxes_added_today,
        )
        
        db.add(new_metrics)
        await db.commit()
        return {
            "success": True,
            "message": f"Added new metrics for {box.product_name} on {metric_date}",
            "action": "created"
        }


async def list_all_boxes(db: AsyncSession) -> list:
    """List all available boxes"""
    stmt = select(BoosterBox).order_by(BoosterBox.product_name)
    result = await db.execute(stmt)
    boxes = result.scalars().all()
    return [{"id": str(box.id), "name": box.product_name} for box in boxes]


async def main():
    """Interactive CLI for entering data"""
    print("=" * 60)
    print("Manual Data Entry Tool")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        # List available boxes
        print("Available boxes:")
        boxes = await list_all_boxes(db)
        for i, box in enumerate(boxes, 1):
            print(f"  {i}. {box['name']}")
        print()
        
        # Get input
        box_name = input("Enter box name (or number from list): ").strip()
        
        # If number, get name
        try:
            box_num = int(box_name)
            if 1 <= box_num <= len(boxes):
                box_name = boxes[box_num - 1]["name"]
        except ValueError:
            pass
        
        metric_date = input("Enter date (YYYY-MM-DD): ").strip()
        
        print("\nEnter metrics (press Enter to skip):")
        floor_price = input("Floor Price ($): ").strip()
        floor_price = float(floor_price) if floor_price else None
        
        active_listings = input("Active Listings: ").strip()
        active_listings = int(active_listings) if active_listings else None
        
        boxes_sold = input("Boxes Sold Today: ").strip()
        boxes_sold = int(boxes_sold) if boxes_sold else None
        
        daily_volume = input("Daily Volume ($): ").strip()
        daily_volume = float(daily_volume) if daily_volume else None
        
        market_cap = input("Market Cap ($): ").strip()
        market_cap = float(market_cap) if market_cap else None
        
        boxes_added = input("Boxes Added Today: ").strip()
        boxes_added = int(boxes_added) if boxes_added else None
        
        # Add metrics
        result = await add_metrics(
            db=db,
            box_name=box_name,
            metric_date=metric_date,
            floor_price_usd=floor_price,
            active_listings_count=active_listings,
            boxes_sold_today=boxes_sold,
            daily_volume_usd=daily_volume,
            visible_market_cap_usd=market_cap,
            boxes_added_today=boxes_added,
        )
        
        if result["success"]:
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ Error: {result['error']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

