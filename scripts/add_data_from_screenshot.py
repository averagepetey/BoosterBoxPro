"""
Quick script to add data from screenshot analysis
Usage: python scripts/add_data_from_screenshot.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.manual_data_entry import add_metrics, AsyncSessionLocal


async def quick_add(
    box_name: str,
    date: str,
    floor_price: float = None,
    listings: int = None,
    sold: int = None,
    volume: float = None,
    market_cap: float = None,
    added: int = None,
):
    """Quick function to add data"""
    async with AsyncSessionLocal() as db:
        result = await add_metrics(
            db=db,
            box_name=box_name,
            metric_date=date,
            floor_price_usd=floor_price,
            active_listings_count=listings,
            boxes_sold_today=sold,
            daily_volume_usd=volume,
            visible_market_cap_usd=market_cap,
            boxes_added_today=added,
        )
        print(result["message"] if result["success"] else f"Error: {result['error']}")


# Example usage:
# asyncio.run(quick_add("OP-01", "2024-12-29", floor_price=120.50, listings=45))

if __name__ == "__main__":
    print("=" * 60)
    print("Quick Data Entry from Screenshot")
    print("=" * 60)
    print()
    print("Edit this file and call quick_add() with your data,")
    print("or use the interactive tool: python scripts/manual_data_entry.py")
    print()





