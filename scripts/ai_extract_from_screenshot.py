#!/usr/bin/env python3
"""
AI-Assisted Screenshot Extraction
After viewing a screenshot, this script can be used to submit extracted values
"""

import sys
import os
import asyncio
import httpx
from uuid import UUID

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


async def extract_and_save(
    processing_id: str,
    box_id: str,
    metric_date: str,
    floor_price_usd: float,
    active_listings_count: int,
    daily_volume_usd: float = None,
    units_sold_count: int = None,
    visible_market_cap_usd: float = None
):
    """
    Extract data from screenshot and save metrics entry
    
    This function is called by the AI after analyzing a screenshot
    """
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print(f"📊 Extracting and saving metrics...")
    print(f"   Processing ID: {processing_id}")
    print(f"   Box ID: {box_id}")
    print(f"   Date: {metric_date}")
    print(f"   Floor Price: ${floor_price_usd}")
    print(f"   Active Listings: {active_listings_count}")
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "metric_date": metric_date,
        "floor_price_usd": floor_price_usd,
        "active_listings_count": active_listings_count,
    }
    
    if daily_volume_usd is not None:
        payload["daily_volume_usd"] = daily_volume_usd
        print(f"   Daily Volume: ${daily_volume_usd}")
    if units_sold_count is not None:
        payload["units_sold_count"] = units_sold_count
        print(f"   Units Sold: {units_sold_count}")
    if visible_market_cap_usd is not None:
        payload["visible_market_cap_usd"] = visible_market_cap_usd
        print(f"   Market Cap: ${visible_market_cap_usd}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        
        try:
            response = await client.post(
                f"{API_BASE}/admin/screenshot/confirm",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"\n✅ Metrics saved and calculated successfully!")
                print(f"   Metric ID: {result['id']}")
                print(f"   ✅ All derived metrics calculated (EMA, liquidity score, etc.)")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"\n❌ Error saving metrics: {error_msg}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-assisted screenshot extraction")
    parser.add_argument("processing_id", help="Processing ID from screenshot upload")
    parser.add_argument("box_id", help="Booster box UUID")
    parser.add_argument("metric_date", help="Date (YYYY-MM-DD)")
    parser.add_argument("floor_price", type=float, help="Floor price in USD")
    parser.add_argument("active_listings", type=int, help="Active listings count")
    parser.add_argument("--volume", type=float, help="Daily volume in USD")
    parser.add_argument("--units-sold", type=int, help="Units sold count")
    parser.add_argument("--market-cap", type=float, help="Visible market cap in USD")
    
    args = parser.parse_args()
    
    success = asyncio.run(extract_and_save(
        args.processing_id,
        args.box_id,
        args.metric_date,
        args.floor_price,
        args.active_listings,
        daily_volume_usd=args.volume,
        units_sold_count=args.units_sold,
        visible_market_cap_usd=args.market_cap
    ))
    
    sys.exit(0 if success else 1)

