#!/usr/bin/env python3
"""
Register Additional Booster Boxes
Adds missing boxes from Excel data (variants, EB series, PRB series)
"""

import sys
import os
import asyncio
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.config import settings

# Additional boxes to register
ADDITIONAL_BOXES = [
    {
        "product_name": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
        "set_name": "Romance Dawn (Blue)",
        "game_type": "One Piece",
        "release_date": "2022-12-02",  # December 2, 2022 (English/global)
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-01-blue.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW",
        "external_product_id": "OP-01-BLUE"
    },
    {
        "product_name": "One Piece - OP-01 Romance Dawn Booster Box (White)",
        "set_name": "Romance Dawn (White)",
        "game_type": "One Piece",
        "release_date": "2022-12-02",  # December 2, 2022 (English/global) - variants share same date
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-01-white.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW",
        "external_product_id": "OP-01-WHITE"
    },
    {
        "product_name": "One Piece - EB-01 Memorial Collection Booster Box",
        "set_name": "Memorial Collection",
        "game_type": "One Piece",
        "release_date": "2024-05-03",  # May 3, 2024 (English/global)
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-eb01.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW",
        "external_product_id": "EB-01"
    },
    {
        "product_name": "One Piece - EB-02 Anime 25th Collection Booster Box",
        "set_name": "Anime 25th Collection",
        "game_type": "One Piece",
        "release_date": "2025-05-09",  # May 9, 2025 (English/global)
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-eb02.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW",
        "external_product_id": "EB-02"
    },
    {
        "product_name": "One Piece - PRB-01 Premium Booster Box (The Best)",
        "set_name": "Premium Booster (The Best)",
        "game_type": "One Piece",
        "release_date": "2024-11-08",  # November 8, 2024 (English/global)
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-prb01.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW",
        "external_product_id": "PRB-01"
    },
    {
        "product_name": "One Piece - PRB-02 Premium Booster Box vol.2",
        "set_name": "Premium Booster vol.2",
        "game_type": "One Piece",
        "release_date": "2025-10-03",  # October 3, 2025 (English/global)
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-prb02.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW",
        "external_product_id": "PRB-02"
    },
]


async def register_additional_boxes(base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
    """Register additional boxes via the admin API"""
    
    # Use provided key, or try to get from settings
    if api_key is None:
        api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print("🚀 Registering additional booster boxes...")
    if api_key:
        masked_key = api_key[:20] + "..." if len(api_key) > 20 else api_key
        print(f"Using API key: {masked_key}")
    else:
        print("No API key (development mode)")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        created = []
        errors = []
        
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        for box_data in ADDITIONAL_BOXES:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/admin/boxes",
                    json=box_data,
                    headers=headers if headers else None
                )
                
                if response.status_code == 201:
                    try:
                        box = response.json()
                        created.append(box)
                        print(f"✅ Created: {box_data['product_name']}")
                        print(f"   ID: {box['id']}")
                    except Exception as json_error:
                        errors.append({"box": box_data["product_name"], "error": f"JSON parse error: {json_error}, Response: {response.text[:200]}"})
                        print(f"❌ Failed: {box_data['product_name']}")
                        print(f"   Status: {response.status_code}")
                        print(f"   Response: {response.text[:200]}")
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("detail", "Unknown error")
                    except Exception:
                        error_msg = f"Status {response.status_code}: {response.text[:200]}"
                    errors.append({"box": box_data["product_name"], "error": error_msg})
                    print(f"❌ Failed: {box_data['product_name']}")
                    print(f"   Status: {response.status_code}")
                    print(f"   Error: {error_msg}")
                
            except Exception as e:
                errors.append({"box": box_data["product_name"], "error": str(e)})
                print(f"❌ Error registering {box_data['product_name']}: {e}")
            
            print()
        
        print("=" * 60)
        print(f"✅ Successfully created: {len(created)} boxes")
        print(f"❌ Errors: {len(errors)} boxes")
        print()
        
        if errors:
            print("Errors:")
            for error in errors:
                print(f"  - {error['box']}: {error['error']}")
            print()
        
        return len(created) == len(ADDITIONAL_BOXES)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Register additional booster boxes")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default=None, help="Admin API key (defaults to ADMIN_API_KEY from .env if set)")
    
    args = parser.parse_args()
    
    success = asyncio.run(register_additional_boxes(base_url=args.url, api_key=args.api_key))
    sys.exit(0 if success else 1)

