#!/usr/bin/env python3
"""
Test Listing Extraction from Screenshot
Extracts listing data from OP-11 screenshot and saves to database
"""

import sys
import os
import asyncio
import httpx
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


async def get_box_id_by_name(box_name: str):
    """Get box UUID by name"""
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        try:
            response = await client.get(
                f"{API_BASE}/admin/boxes",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                boxes = data.get("boxes", [])
                print(f"   Found {len(boxes)} boxes in database")
                for box in boxes:
                    product_name = box.get("product_name", "").lower()
                    if box_name.lower() in product_name:
                        print(f"   ✅ Match found: {box.get('product_name')}")
                        return box.get("id")
                    print(f"   Checking: {box.get('product_name')} (ID: {box.get('id')})")
                print(f"   ⚠️  No box matching '{box_name}' found")
                return None
            else:
                print(f"   ❌ API returned status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return None
        except httpx.ConnectError as e:
            print(f"   ❌ Connection error: Cannot connect to server at {API_BASE}")
            print(f"   Make sure the FastAPI server is running: python scripts/run_server.py")
            return None
        except Exception as e:
            print(f"   ❌ Error getting box: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_listing_extraction():
    """Test extracting listing data from OP-11 screenshot"""
    
    print("🧪 Testing Listing Extraction from OP-11 Screenshot")
    print("=" * 60)
    
    # Step 1: Get OP-11 box ID
    print("\n1️⃣ Finding OP-11 box in database...")
    box_id = await get_box_id_by_name("OP-11")
    
    if not box_id:
        print("❌ OP-11 box not found in database!")
        print("\n   🔧 Troubleshooting:")
        print("   1. Check if server is running: python scripts/run_server.py")
        print("   2. Check if boxes are registered: python scripts/diagnose_box_search.py")
        print("   3. Register boxes if needed: python scripts/register_boxes.py")
        return False
    
    print(f"✅ Found box: {box_id}")
    
    # Step 2: Create a mock processing_id (or use real one if screenshot uploaded)
    # For testing, we'll use a test processing_id
    processing_id = "test_op11_listings_" + str(int(asyncio.get_event_loop().time()))
    
    # Step 3: Extract listing data from screenshot description
    print("\n2️⃣ Extracting listing data from screenshot...")
    
    # Listing data extracted from screenshot
    listings = [
        {
            "listing_id": "multimonster_deals_1",
            "listed_price_usd": 279.51,
            "quantity": 8,
            "seller_id": "MultiMonster Deals"
        },
        {
            "listing_id": "halfastar_tcg_1",
            "listed_price_usd": 279.52,
            "quantity": 4,
            "seller_id": "Halfastar TCG"
        },
        {
            "listing_id": "kearneyscardexchange_1",
            "listed_price_usd": 270.00,
            "quantity": 1,
            "seller_id": "KearneysCardExchange"
        },
        {
            "listing_id": "wildcardcyclone_1",
            "listed_price_usd": 290.00,
            "quantity": 6,
            "seller_id": "WildCardCyclone"
        },
        {
            "listing_id": "bmc_collectibles_1",
            "listed_price_usd": 298.98,
            "quantity": 1,
            "seller_id": "BMC Collectibles TCG"
        },
        {
            "listing_id": "krave_cardz_1",
            "listed_price_usd": 298.99,
            "quantity": 1,
            "seller_id": "KraVe CarDz LLC"
        }
    ]
    
    print(f"   Extracted {len(listings)} listings:")
    for listing in listings:
        print(f"   - {listing['seller_id']}: ${listing['listed_price_usd']:.2f} (Qty: {listing['quantity']})")
    
    # Calculate floor price (lowest listing)
    floor_price = min(l["listed_price_usd"] for l in listings)
    total_listings = sum(l["quantity"] for l in listings)
    
    print(f"\n   Floor Price: ${floor_price:.2f}")
    print(f"   Total Available: {total_listings} boxes")
    
    # Step 4: Save listings using the extraction endpoint
    print("\n3️⃣ Saving listings to database...")
    
    api_key = settings.admin_api_key if settings.admin_api_key else None
    snapshot_date = date.today().isoformat()
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "snapshot_date": snapshot_date,
        "listings": listings
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        
        try:
            response = await client.post(
                f"{API_BASE}/admin/screenshot/listings/extract",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"\n✅ Successfully saved listings!")
                print(f"   Saved: {len(result.get('saved', []))} listings")
                print(f"   Errors: {len(result.get('errors', []))}")
                print(f"   Snapshot Date: {snapshot_date}")
                
                if result.get('errors'):
                    print(f"\n⚠️  Errors:")
                    for error in result['errors']:
                        print(f"   - {error}")
                
                # Step 5: Verify data was saved
                print("\n4️⃣ Verifying saved data...")
                await verify_saved_listings(box_id, snapshot_date)
                
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"\n❌ Error saving listings: {error_msg}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def verify_saved_listings(box_id: str, snapshot_date: str):
    """Verify the listings were saved correctly"""
    from sqlalchemy import text
    from app.database import engine
    from datetime import date
    
    print("\n   Querying database...")
    
    # Convert string date to date object
    date_obj = date.fromisoformat(snapshot_date) if isinstance(snapshot_date, str) else snapshot_date
    
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT 
                    COUNT(*) as total_listings,
                    SUM(quantity) as total_quantity,
                    MIN(listed_price_usd) as floor_price,
                    MAX(listed_price_usd) as max_price,
                    AVG(listed_price_usd) as avg_price
                FROM tcg_listings_raw
                WHERE booster_box_id = :box_id
                AND snapshot_date = :snapshot_date
            """),
            {"box_id": box_id, "snapshot_date": date_obj}
        )
        
        row = result.fetchone()
        if row:
            print(f"\n   ✅ Database Verification:")
            print(f"      Total Listings: {row[0]}")
            print(f"      Total Quantity: {row[1]}")
            print(f"      Floor Price: ${float(row[2]):.2f}")
            print(f"      Max Price: ${float(row[3]):.2f}")
            print(f"      Avg Price: ${float(row[4]):.2f}")
        else:
            print("   ⚠️  No listings found in database")


if __name__ == "__main__":
    success = asyncio.run(test_listing_extraction())
    sys.exit(0 if success else 1)

