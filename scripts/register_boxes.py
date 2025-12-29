#!/usr/bin/env python3
"""
Register 10 One Piece Booster Boxes
Script to populate the database with initial booster box data
"""

import sys
import os
import asyncio
from datetime import date
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.config import settings

# One Piece booster boxes data
# Source: Official One Piece TCG releases
ONE_PIECE_BOXES = [
    {
        "product_name": "One Piece - OP-01 Romance Dawn Booster Box",
        "set_name": "Romance Dawn",
        "game_type": "One Piece",
        "release_date": "2023-03-31",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-01.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-02 Paramount War Booster Box",
        "set_name": "Paramount War",
        "game_type": "One Piece",
        "release_date": "2023-07-07",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-02.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-03 Pillars of Strength Booster Box",
        "set_name": "Pillars of Strength",
        "game_type": "One Piece",
        "release_date": "2023-09-29",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-03.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
        "set_name": "Kingdoms of Intrigue",
        "game_type": "One Piece",
        "release_date": "2023-12-01",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-04.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-05 Awakening of the New Era Booster Box",
        "set_name": "Awakening of the New Era",
        "game_type": "One Piece",
        "release_date": "2024-03-08",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-05.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-06 Wings of the Captain Booster Box",
        "set_name": "Wings of the Captain",
        "game_type": "One Piece",
        "release_date": "2024-05-31",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-06.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-07 500 Years In The Future Booster Box",
        "set_name": "500 Years In The Future",
        "game_type": "One Piece",
        "release_date": "2024-09-13",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-07.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-08 Two Legends Booster Box",
        "set_name": "Two Legends",
        "game_type": "One Piece",
        "release_date": "2024-12-06",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-08.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-09 Emperors of the New World Booster Box",
        "set_name": "Emperors of the New World",
        "game_type": "One Piece",
        "release_date": "2025-02-14",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-09.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-10 Royal Blood Booster Box",
        "set_name": "Royal Blood",
        "game_type": "One Piece",
        "release_date": "2025-05-30",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-10.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
        "set_name": "A Fist of Divine Speed",
        "game_type": "One Piece",
        "release_date": "2025-06-06",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-11.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-12 Legacy of the Master Booster Box",
        "set_name": "Legacy of the Master",
        "game_type": "One Piece",
        "release_date": "2025-08-22",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-12.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
    {
        "product_name": "One Piece - OP-13 Carrying on His Will Booster Box",
        "set_name": "Carrying on His Will",
        "game_type": "One Piece",
        "release_date": "2025-11-07",
        "image_url": "https://cdn.tcgplayer.com/card-images/onepiece-13.jpg",
        "estimated_total_supply": 36600,
        "reprint_risk": "LOW"
    },
]


async def register_boxes(base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
    """Register all 13 One Piece booster boxes via the admin API"""
    
    # Use provided key, or try to get from settings
    if api_key is None:
        api_key = settings.admin_api_key if settings.admin_api_key else None
    
    print("🚀 Registering 13 One Piece booster boxes...")
    print(f"Using API key: {api_key[:10]}..." if api_key else "No API key (dev mode)")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        created = []
        errors = []
        
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        for box_data in ONE_PIECE_BOXES:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/admin/boxes",
                    json=box_data,
                    headers=headers
                )
                
                if response.status_code == 201:
                    try:
                        box = response.json()
                        created.append(box)
                        print(f"✅ Created: {box_data['product_name']}")
                        print(f"   ID: {box['id']}")
                    except Exception as json_error:
                        errors.append({"box": box_data["product_name"], "error": f"JSON parse error: {json_error}, Response text: {response.text[:200]}"})
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
                import traceback
                print(f"   Traceback: {traceback.format_exc()[:300]}")
            
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
        
        return len(created) == len(ONE_PIECE_BOXES)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Register One Piece booster boxes")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--api-key", default=None, help="Admin API key (defaults to ADMIN_API_KEY from .env if set)")
    
    args = parser.parse_args()
    
    success = asyncio.run(register_boxes(base_url=args.url, api_key=args.api_key))
    sys.exit(0 if success else 1)

