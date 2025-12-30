#!/usr/bin/env python3
"""
Extract Individual Sale from Screenshot
Helper script for AI to extract and save individual sale data
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


async def extract_and_save_sale(
    processing_id: str,
    box_id: str,
    sale_date: str,
    sold_price_usd: float,
    quantity: int = 1,
    seller_id: str = None,
    listing_type: str = None
):
    """Extract individual sale and save to database"""
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print(f"💰 Extracting sale data...")
    print(f"   Processing ID: {processing_id}")
    print(f"   Box ID: {box_id}")
    print(f"   Sale Date: {sale_date}")
    print(f"   Sold Price: ${sold_price_usd}")
    print(f"   Quantity: {quantity}")
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "sale_date": sale_date,
        "sold_price_usd": sold_price_usd,
        "quantity": quantity,
    }
    
    if seller_id:
        payload["seller_id"] = seller_id
    if listing_type:
        payload["listing_type"] = listing_type
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-API-Key"] = api_key
        
        try:
            response = await client.post(
                f"{API_BASE}/admin/screenshot/sales/extract",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"\n✅ Sale saved successfully!")
                print(f"   Sale ID: {result.get('id')}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"\n❌ Error saving sale: {error_msg}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def extract_bulk_sales(
    processing_id: str,
    box_id: str,
    sales: list
):
    """Extract multiple sales from a single screenshot"""
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print(f"💰 Extracting {len(sales)} sales...")
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "sales": sales,
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
                print(f"\n✅ Saved {result.get('total_processed', 0)} sales!")
                print(f"   Successful: {len(result.get('saved', []))}")
                print(f"   Errors: {len(result.get('errors', []))}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"\n❌ Error: {error_msg}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def extract_listings(
    processing_id: str,
    box_id: str,
    snapshot_date: str,
    listings: list
):
    """Extract listing data from screenshot"""
    api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print(f"📋 Extracting {len(listings)} listings...")
    
    payload = {
        "processing_id": processing_id,
        "booster_box_id": box_id,
        "snapshot_date": snapshot_date,
        "listings": listings,
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
                print(f"\n✅ Saved {len(result.get('saved', []))} listings!")
                print(f"   Total processed: {result.get('total_processed', 0)}")
                print(f"   Errors: {len(result.get('errors', []))}")
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('detail', response.text)
                print(f"\n❌ Error: {error_msg}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract sales or listings from screenshot")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Single sale extraction
    sale_parser = subparsers.add_parser('sale', help='Extract single sale')
    sale_parser.add_argument('processing_id', help='Processing ID')
    sale_parser.add_argument('box_id', help='Box UUID')
    sale_parser.add_argument('sale_date', help='Sale date (YYYY-MM-DD)')
    sale_parser.add_argument('sold_price', type=float, help='Sold price in USD')
    sale_parser.add_argument('--quantity', type=int, default=1, help='Quantity')
    sale_parser.add_argument('--seller-id', help='Seller ID')
    sale_parser.add_argument('--listing-type', help='Listing type')
    
    args = parser.parse_args()
    
    if args.command == 'sale':
        success = asyncio.run(extract_and_save_sale(
            args.processing_id,
            args.box_id,
            args.sale_date,
            args.sold_price,
            quantity=args.quantity,
            seller_id=args.seller_id,
            listing_type=args.listing_type
        ))
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)

