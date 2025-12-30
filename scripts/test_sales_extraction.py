#!/usr/bin/env python3
"""
Test Sales Extraction from Screenshot
Extracts individual sales data from OP-11 sales history screenshot and saves to database
"""

import sys
import os
import asyncio
import httpx

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


async def test_sales_extraction():
    """Test extracting sales data from OP-11 sales history screenshot"""
    
    print("💰 Testing Sales Extraction from OP-11 Sales History")
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
    
    # Step 2: Create a mock processing_id
    processing_id = "test_op11_sales_" + str(int(asyncio.get_event_loop().time()))
    
    # Step 3: Extract sales data from screenshot
    print("\n2️⃣ Extracting sales data from screenshot...")
    
    # Sales data extracted from Sales History Snapshot
    # Dates need to be converted: 12/29/25 -> 2025-12-29
    sales = [
        {"sale_date": "2025-12-29", "sold_price_usd": 279.51, "quantity": 1},
        {"sale_date": "2025-12-29", "sold_price_usd": 279.51, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 279.57, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 279.99, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 279.60, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 299.00, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 275.00, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 273.99, "quantity": 1},
        {"sale_date": "2025-12-28", "sold_price_usd": 279.69, "quantity": 2},
        {"sale_date": "2025-12-28", "sold_price_usd": 264.99, "quantity": 1},
        {"sale_date": "2025-12-27", "sold_price_usd": 264.98, "quantity": 1},
        {"sale_date": "2025-12-27", "sold_price_usd": 264.98, "quantity": 1},
        {"sale_date": "2025-12-27", "sold_price_usd": 264.99, "quantity": 1},
    ]
    
    print(f"   Extracted {len(sales)} sales:")
    print(f"   - 12/27/25: {len([s for s in sales if '2025-12-27' in s['sale_date']])} sales")
    print(f"   - 12/28/25: {len([s for s in sales if '2025-12-28' in s['sale_date']])} sales")
    print(f"   - 12/29/25: {len([s for s in sales if '2025-12-29' in s['sale_date']])} sales")
    
    total_boxes_sold = sum(s["quantity"] for s in sales)
    avg_price = sum(s["sold_price_usd"] for s in sales) / len(sales)
    min_price = min(s["sold_price_usd"] for s in sales)
    max_price = max(s["sold_price_usd"] for s in sales)
    
    print(f"\n   Summary:")
    print(f"   Total Boxes Sold: {total_boxes_sold}")
    print(f"   Average Price: ${avg_price:.2f}")
    print(f"   Min Price: ${min_price:.2f}")
    print(f"   Max Price: ${max_price:.2f}")
    
    # Step 4: Save sales using the bulk extraction endpoint
    print("\n3️⃣ Saving sales to database...")
    
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "sales": sales
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        
        try:
            response = await client.post(
                f"{API_BASE}/admin/screenshot/sales/bulk-extract",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"\n✅ Successfully saved sales!")
                print(f"   Saved: {len(result.get('saved', []))} sales")
                print(f"   Errors: {len(result.get('errors', []))}")
                
                if result.get('errors'):
                    print(f"\n⚠️  Errors:")
                    for error in result['errors']:
                        print(f"   - {error}")
                
                # Step 5: Verify data was saved
                print("\n4️⃣ Verifying saved data...")
                await verify_saved_sales(box_id)
                
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"\n❌ Error saving sales: {error_msg}")
                print(f"   Status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def verify_saved_sales(box_id: str):
    """Verify the sales were saved correctly"""
    from sqlalchemy import text
    from app.database import engine
    
    print("\n   Querying database...")
    
    async with engine.begin() as conn:
        # Get sales by date
        result = await conn.execute(
            text("""
                SELECT 
                    sale_date,
                    COUNT(*) as sales_count,
                    SUM(quantity) as total_quantity,
                    MIN(sold_price_usd) as min_price,
                    MAX(sold_price_usd) as max_price,
                    AVG(sold_price_usd) as avg_price,
                    SUM(sold_price_usd * quantity) as total_volume
                FROM ebay_sales_raw
                WHERE booster_box_id = :box_id
                GROUP BY sale_date
                ORDER BY sale_date DESC
            """),
            {"box_id": box_id}
        )
        
        rows = result.fetchall()
        if rows:
            print(f"\n   ✅ Database Verification:")
            print(f"   {'Date':<12} {'Sales':<8} {'Qty':<6} {'Min Price':<12} {'Max Price':<12} {'Avg Price':<12} {'Volume':<12}")
            print(f"   {'-'*80}")
            
            total_sales = 0
            total_qty = 0
            total_volume = 0
            
            for row in rows:
                date_str = str(row[0])
                sales_count = row[1]
                qty = row[2]
                min_p = float(row[3]) if row[3] else 0
                max_p = float(row[4]) if row[4] else 0
                avg_p = float(row[5]) if row[5] else 0
                volume = float(row[6]) if row[6] else 0
                
                print(f"   {date_str:<12} {sales_count:<8} {qty:<6} ${min_p:<11.2f} ${max_p:<11.2f} ${avg_p:<11.2f} ${volume:<11.2f}")
                
                total_sales += sales_count
                total_qty += qty
                total_volume += volume
            
            print(f"   {'-'*80}")
            print(f"   {'TOTAL':<12} {total_sales:<8} {total_qty:<6} {'':<12} {'':<12} {'':<12} ${total_volume:<11.2f}")
        else:
            print("   ⚠️  No sales found in database")


if __name__ == "__main__":
    success = asyncio.run(test_sales_extraction())
    sys.exit(0 if success else 1)

