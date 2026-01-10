"""
AI Assistant Data Entry Helper
Use this when the AI assistant extracts data from screenshots
Automatically checks for duplicates before adding
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.manual_data_entry import add_metrics, AsyncSessionLocal
from scripts.check_duplicate import check_duplicate_data


async def ai_add_data(
    box_name: str,
    date: str,
    floor_price: float = None,
    listings: int = None,
    sold: int = None,
    volume: float = None,
    market_cap: float = None,
    added: int = None,
    force: bool = False,
) -> dict:
    """
    AI Assistant helper to add data with automatic duplicate checking
    
    Args:
        box_name: Box name (e.g., "OP-01", "One Piece OP-02")
        date: Date in YYYY-MM-DD format
        floor_price: Floor price in USD
        listings: Active listings count
        sold: Boxes sold today
        volume: Daily volume in USD
        market_cap: Visible market cap in USD
        added: Boxes added today
        force: If True, skip duplicate check and force add/update
        
    Returns:
        Result dictionary with success status and message
    """
    print(f"\n{'='*60}")
    print(f"Adding data for {box_name} on {date}")
    print(f"{'='*60}\n")
    
    # First, check for duplicates
    if not force:
        print("🔍 Checking for duplicates...")
        duplicate_check = await check_duplicate_data(
            box_name=box_name,
            metric_date=date,
            floor_price=floor_price,
            listings=listings,
            sold=sold,
            volume=volume,
            market_cap=market_cap,
            added=added,
        )
        
        print(duplicate_check["message"])
        
        if duplicate_check.get("is_duplicate"):
            print("\n❌ DUPLICATE DETECTED - Not adding data")
            return {
                "success": False,
                "is_duplicate": True,
                "message": duplicate_check["message"],
                "existing_data": duplicate_check.get("existing_data")
            }
        
        if duplicate_check.get("differences"):
            print("\n⚠️  Differences found:")
            for key, diff in duplicate_check["differences"].items():
                print(f"  {key}: {diff.get('existing')} → {diff.get('new')}")
            print("\nWill update existing data with new values...")
    
    # Add/update the data
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
            skip_duplicate_check=True,  # Already checked above
        )
        
        if result["success"]:
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        
        return result


# Example usage (AI assistant will call this):
# asyncio.run(ai_add_data("OP-01", "2024-12-29", floor_price=120.50, listings=45, sold=3))

if __name__ == "__main__":
    print("AI Assistant Data Entry Helper")
    print("=" * 60)
    print("\nThis script is designed to be called by the AI assistant")
    print("when extracting data from screenshots.")
    print("\nThe AI will automatically:")
    print("  1. Check for duplicates")
    print("  2. Compare existing vs new data")
    print("  3. Only add if new or different")
    print("  4. Update if data differs")
    print()




