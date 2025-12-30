#!/usr/bin/env python3
"""
Process Screenshot for AI Extraction
Helper script to upload a screenshot and get processing ID for AI-assisted extraction
"""

import sys
import os
import asyncio
import httpx
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


async def upload_screenshot_for_ai(
    image_path: str,
    box_name: str = None,
    metric_date: str = None
):
    """
    Upload a screenshot and return processing ID for AI extraction
    
    Usage: Share the processing_id with Cursor AI, then use confirm_extraction_ai()
    """
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return None
    
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print(f"📷 Uploading screenshot: {image_path}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {}
            if box_name:
                data['box_name'] = box_name
            if metric_date:
                data['metric_date'] = metric_date
            
            try:
                response = await client.post(
                    f"{API_BASE}/admin/screenshot/upload",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    processing_id = result.get('processing_id')
                    print(f"\n✅ Screenshot uploaded successfully!")
                    print(f"📋 Processing ID: {processing_id}")
                    print(f"\n💡 Next steps:")
                    print(f"   1. Share this processing_id with Cursor AI: {processing_id}")
                    print(f"   2. Share the screenshot image in the chat")
                    print(f"   3. Cursor will extract the data and create the entry")
                    print(f"\n📸 View screenshot at: {BASE_URL}/api/v1/admin/screenshot/{processing_id}")
                    return processing_id
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   {response.text}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error uploading screenshot: {e}")
                return None


async def confirm_extraction_ai(
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
    Confirm extracted values and create metrics entry
    
    This is called after AI extraction to save the metrics
    """
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "metric_date": metric_date,
        "floor_price_usd": floor_price_usd,
        "active_listings_count": active_listings_count,
    }
    
    if daily_volume_usd is not None:
        payload["daily_volume_usd"] = daily_volume_usd
    if units_sold_count is not None:
        payload["units_sold_count"] = units_sold_count
    if visible_market_cap_usd is not None:
        payload["visible_market_cap_usd"] = visible_market_cap_usd
    
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
                print(f"\n✅ Metrics saved successfully!")
                print(f"   Box ID: {result['booster_box_id']}")
                print(f"   Date: {result['metric_date']}")
                print(f"   Floor Price: ${result.get('floor_price_usd')}")
                print(f"   Listings: {result.get('active_listings_count')}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error saving metrics: {e}")
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload screenshot for AI extraction")
    parser.add_argument("image_path", help="Path to screenshot image file")
    parser.add_argument("--box-name", help="Optional box name")
    parser.add_argument("--date", help="Optional date (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    processing_id = asyncio.run(upload_screenshot_for_ai(
        args.image_path,
        box_name=args.box_name,
        metric_date=args.date
    ))
    
    if processing_id:
        print(f"\n🎯 Share this with Cursor AI:")
        print(f"   Processing ID: {processing_id}")
        sys.exit(0)
    else:
        sys.exit(1)

