#!/usr/bin/env python3
"""
Pull sales data from TCGplayer via Apify for all 18 booster boxes.
Updates historical_entries.json with fresh data.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.services.tcgplayer_apify import TCGplayerApifyService, TCGPLAYER_URLS

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
HISTORICAL_FILE = DATA_DIR / "historical_entries.json"


def load_historical_entries():
    """Load existing historical entries."""
    if HISTORICAL_FILE.exists():
        with open(HISTORICAL_FILE, "r") as f:
            return json.load(f)
    return []


def save_historical_entries(entries):
    """Save historical entries."""
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(entries, f, indent=2)
    print(f"💾 Saved {len(entries)} entries to {HISTORICAL_FILE}")


def find_or_create_entry(entries, box_id, date_str):
    """Find existing entry for box+date or create new one."""
    for entry in entries:
        if entry.get("box_id") == box_id and entry.get("date") == date_str:
            return entry, False  # Found existing
    
    # Create new entry
    new_entry = {
        "box_id": box_id,
        "date": date_str,
    }
    entries.append(new_entry)
    return new_entry, True  # Created new


def pull_all_boxes():
    """Pull data for all boxes from TCGplayer via Apify."""
    api_token = os.getenv("APIFY_API_TOKEN")
    if not api_token:
        print("❌ APIFY_API_TOKEN not set in .env")
        sys.exit(1)
    
    service = TCGplayerApifyService(api_token)
    today = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\n{'='*60}")
    print(f"🚀 PULLING TCGPLAYER DATA FOR ALL BOXES")
    print(f"📅 Date: {today}")
    print(f"{'='*60}\n")
    
    # Load existing data
    entries = load_historical_entries()
    print(f"📂 Loaded {len(entries)} existing historical entries\n")
    
    # Track results
    results = []
    success_count = 0
    error_count = 0
    
    # Get boxes with URLs
    boxes_with_urls = {
        box_id: info 
        for box_id, info in TCGPLAYER_URLS.items() 
        if info.get("url")
    }
    
    print(f"📦 Processing {len(boxes_with_urls)} boxes with URLs...\n")
    
    for i, (box_id, info) in enumerate(boxes_with_urls.items(), 1):
        box_name = info["name"]
        url = info["url"]
        
        print(f"[{i}/{len(boxes_with_urls)}] {box_name}...")
        
        try:
            # Fetch data from Apify (synchronous call)
            raw_data = service.fetch_sales_history(url)
            
            if not raw_data:
                print(f"   ⚠️  No data returned")
                error_count += 1
                continue
            
            # Debug: check raw_data type
            print(f"   📦 Raw data type: {type(raw_data).__name__}")
            
            # Transform to our format
            transformed = service.transform_to_historical_entry(raw_data, box_id, today)
            
            # Debug: check transformed type
            print(f"   📦 Transformed type: {type(transformed).__name__}")
            
            if not transformed:
                print(f"   ⚠️  Could not transform data")
                error_count += 1
                continue
            
            # Find or create entry for today
            entry, is_new = find_or_create_entry(entries, box_id, today)
            
            # Update entry with transformed data
            for key, value in transformed.items():
                entry[key] = value
            entry["data_source"] = "tcgplayer_apify"
            
            status = "NEW" if is_new else "UPDATED"
            sold_per_day = transformed.get("boxes_sold_today", 0)
            floor_price = transformed.get("floor_price_usd", 0)
            daily_vol = transformed.get("daily_volume_usd", 0)
            print(f"   ✅ {status}: {sold_per_day}/day @ ${floor_price} (${daily_vol}/day volume)")
            
            results.append({
                "box": box_name,
                "sold_per_day": sold_per_day,
                "market_price": floor_price,
                "daily_volume": daily_vol,
            })
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            error_count += 1
    
    # Save updated entries
    print(f"\n{'='*60}")
    save_historical_entries(entries)
    
    # Print summary
    print(f"\n📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📅 Date: {today}")
    
    if results:
        print(f"\n📈 TOP MOVERS BY DAILY VOLUME:")
        sorted_results = sorted(results, key=lambda x: x["daily_volume"], reverse=True)
        for i, r in enumerate(sorted_results[:5], 1):
            print(f"   {i}. {r['box']}: ${r['daily_volume']:,.2f}/day ({r['sold_per_day']} boxes @ ${r['market_price']})")
    
    print(f"\n{'='*60}")
    print(f"✨ Done! Data saved to {HISTORICAL_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    pull_all_boxes()
