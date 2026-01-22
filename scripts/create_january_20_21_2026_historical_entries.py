"""
Create historical entries for January 20, 2026 and January 21, 2026 data
Generated from screenshot data capture session
"""

import json
from pathlib import Path
from datetime import datetime

# Data collected from screenshots - January 20, 2026
january_20_data = {
    "OP-13": {
        "floor_price_usd": 541.95,  # Estimated from sales avg
        "active_listings_count": 49,
        "boxes_sold_today": 26,
        "daily_volume_usd": 14848.86,
    },
    "OP-09": {
        "floor_price_usd": 622.62,  # Estimated from sales avg
        "active_listings_count": 73,
        "boxes_sold_today": 18,
        "daily_volume_usd": 11207.10,
    },
    "EB-01": {
        "floor_price_usd": 847.31,  # Estimated from sales avg
        "active_listings_count": 12,
        "boxes_sold_today": 3,
        "daily_volume_usd": 2541.94,
    },
    "OP-11": {
        "floor_price_usd": 418.01,  # Estimated from sales avg
        "active_listings_count": 105,
        "boxes_sold_today": 25,
        "daily_volume_usd": 10450.37,
    },
    "OP-01 (Blue)": {
        "floor_price_usd": 6510.97,  # From lowest listing
        "active_listings_count": 11,
        "boxes_sold_today": 0,
        "daily_volume_usd": 0,
    },
    "PRB-01": {
        "floor_price_usd": 946.99,  # Estimated from sales avg
        "active_listings_count": 40,
        "boxes_sold_today": 2,
        "daily_volume_usd": 1893.98,
    },
    "OP-01 (White)": {
        "floor_price_usd": 2041.93,  # Estimated from sales avg
        "active_listings_count": 11,
        "boxes_sold_today": 2,
        "daily_volume_usd": 4083.85,
    },
    "OP-05": {
        "floor_price_usd": 1037.50,  # Estimated from sales avg
        "active_listings_count": 18,
        "boxes_sold_today": 4,
        "daily_volume_usd": 4150.00,
    },
    "OP-10": {
        "floor_price_usd": 229.96,  # Estimated from sales avg
        "active_listings_count": 520,
        "boxes_sold_today": 13,
        "daily_volume_usd": 2989.52,
    },
    "PRB-02": {
        "floor_price_usd": 332.73,  # Estimated from sales avg
        "active_listings_count": 64,
        "boxes_sold_today": 23,
        "daily_volume_usd": 7652.78,
    },
    "OP-07": {
        "floor_price_usd": 306.41,  # Estimated from sales avg
        "active_listings_count": 71,
        "boxes_sold_today": 4,
        "daily_volume_usd": 1225.62,
    },
    "OP-12": {
        "floor_price_usd": 212.60,  # Estimated from sales avg
        "active_listings_count": 87,
        "boxes_sold_today": 52,
        "daily_volume_usd": 11054.95,
    },
    "OP-04": {
        "floor_price_usd": 605.42,  # Estimated from sales avg
        "active_listings_count": 22,
        "boxes_sold_today": 2,
        "daily_volume_usd": 1210.84,
    },
    "OP-06": {
        "floor_price_usd": 342.22,  # Estimated from sales avg
        "active_listings_count": 48,
        "boxes_sold_today": 24,
        "daily_volume_usd": 8213.31,
    },
    "EB-02": {
        "floor_price_usd": 541.72,  # Estimated from sales avg
        "active_listings_count": 36,
        "boxes_sold_today": 16,
        "daily_volume_usd": 8667.55,
    },
    "OP-02": {
        "floor_price_usd": 637.48,  # Estimated from sales avg
        "active_listings_count": 22,
        "boxes_sold_today": 2,
        "daily_volume_usd": 1274.95,
    },
    "OP-08": {
        "floor_price_usd": 206.67,  # Estimated from sales avg
        "active_listings_count": 42,
        "boxes_sold_today": 18,
        "daily_volume_usd": 3720.12,
    },
    "OP-03": {
        "floor_price_usd": 795.59,  # Estimated from sales avg
        "active_listings_count": 30,
        "boxes_sold_today": 2,
        "daily_volume_usd": 1591.18,
    },
}

# Data collected from screenshots - January 21, 2026
january_21_data = {
    "OP-13": {
        "floor_price_usd": 570.58,  # Estimated from sales avg
        "active_listings_count": 49,
        "boxes_sold_today": 12,
        "daily_volume_usd": 6846.93,
    },
    "OP-09": {
        "floor_price_usd": 622.62,  # Carried forward (no sales)
        "active_listings_count": 73,
        "boxes_sold_today": 0,
        "daily_volume_usd": 0,
    },
    "EB-01": {
        "floor_price_usd": 847.31,  # Carried forward (no sales)
        "active_listings_count": 12,
        "boxes_sold_today": 0,
        "daily_volume_usd": 0,
    },
    "OP-11": {
        "floor_price_usd": 402.50,  # Estimated from sales avg
        "active_listings_count": 105,
        "boxes_sold_today": 2,
        "daily_volume_usd": 805.00,
    },
    "OP-01 (Blue)": {
        "floor_price_usd": 6510.97,  # Carried forward (no sales)
        "active_listings_count": 11,
        "boxes_sold_today": 0,
        "daily_volume_usd": 0,
    },
    "PRB-01": {
        "floor_price_usd": 840.00,  # From sale
        "active_listings_count": 40,
        "boxes_sold_today": 1,
        "daily_volume_usd": 840.00,
    },
    "OP-01 (White)": {
        "floor_price_usd": 2113.38,  # From sale
        "active_listings_count": 11,
        "boxes_sold_today": 1,
        "daily_volume_usd": 2113.38,
    },
    "OP-05": {
        "floor_price_usd": 1097.45,  # Estimated from sales avg
        "active_listings_count": 18,
        "boxes_sold_today": 11,
        "daily_volume_usd": 12071.91,
    },
    "OP-10": {
        "floor_price_usd": 232.18,  # Estimated from sales avg
        "active_listings_count": 520,
        "boxes_sold_today": 4,
        "daily_volume_usd": 928.73,
    },
    "PRB-02": {
        "floor_price_usd": 332.33,  # Estimated from sales avg
        "active_listings_count": 64,
        "boxes_sold_today": 3,
        "daily_volume_usd": 997.00,
    },
    "OP-07": {
        "floor_price_usd": 306.33,  # Estimated from sales avg
        "active_listings_count": 71,
        "boxes_sold_today": 3,
        "daily_volume_usd": 919.00,
    },
    "OP-12": {
        "floor_price_usd": 214.95,  # Estimated from sales avg
        "active_listings_count": 87,
        "boxes_sold_today": 6,
        "daily_volume_usd": 1289.70,
    },
    "OP-04": {
        "floor_price_usd": 555.00,  # From sale
        "active_listings_count": 22,
        "boxes_sold_today": 1,
        "daily_volume_usd": 555.00,
    },
    "OP-06": {
        "floor_price_usd": 339.88,  # From sale
        "active_listings_count": 48,
        "boxes_sold_today": 1,
        "daily_volume_usd": 339.88,
    },
    "EB-02": {
        "floor_price_usd": 649.49,  # From sale
        "active_listings_count": 36,
        "boxes_sold_today": 1,
        "daily_volume_usd": 649.49,
    },
    "OP-02": {
        "floor_price_usd": 560.00,  # From sale
        "active_listings_count": 22,
        "boxes_sold_today": 1,
        "daily_volume_usd": 560.00,
    },
    "OP-08": {
        "floor_price_usd": 343.33,  # Estimated from sales avg
        "active_listings_count": 42,
        "boxes_sold_today": 3,
        "daily_volume_usd": 1029.99,
    },
    "OP-03": {
        "floor_price_usd": 763.33,  # Estimated from sales avg
        "active_listings_count": 30,
        "boxes_sold_today": 2,
        "daily_volume_usd": 1526.65,
    },
}


def create_historical_entries():
    """Create historical entries for January 20-21, 2026"""
    historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
    data_file = Path(__file__).parent.parent / "data" / "leaderboard.json"
    
    # Load leaderboard to get box IDs
    with open(data_file, 'r') as f:
        leaderboard = json.load(f)
    
    # Load or create historical data
    if historical_file.exists():
        with open(historical_file, 'r') as f:
            historical_data = json.load(f)
    else:
        historical_data = {}
    
    created_count = 0
    
    # Process both dates
    for entry_date, day_data in [("2026-01-20", january_20_data), ("2026-01-21", january_21_data)]:
        print(f"\n📅 Processing {entry_date}...")
        
        # Create entries for each box
        for box in leaderboard.get("data", []):
            product_name = box.get("product_name", "")
            box_id = box.get("id")
            
            # Find matching set code
            import re
            set_code_match = re.search(r'(OP|EB|PRB)-\d+', product_name, re.IGNORECASE)
            if not set_code_match:
                continue
            
            set_code = set_code_match.group(0).upper()
            
            # Check if it's Blue or White variant
            key = None
            if "(Blue)" in product_name:
                key = "OP-01 (Blue)" if set_code == "OP-01" else set_code
            elif "(White)" in product_name:
                key = "OP-01 (White)" if set_code == "OP-01" else set_code
            else:
                key = set_code
            
            if key not in day_data:
                continue
            
            box_data = day_data[key]
            
            # Create historical entry
            entry = {
                "date": entry_date,
                "source": "screenshot_capture",
                "data_type": "combined",
                "floor_price_usd": box_data["floor_price_usd"],
                "active_listings_count": box_data["active_listings_count"],
                "boxes_sold_today": box_data["boxes_sold_today"],
                "daily_volume_usd": box_data["daily_volume_usd"],
                "boxes_sold_per_day": box_data["boxes_sold_today"],
                "timestamp": datetime.now().isoformat()
            }
            
            if box_id not in historical_data:
                historical_data[box_id] = []
            
            # Check if entry already exists for this date
            existing = False
            for i, e in enumerate(historical_data[box_id]):
                if e.get("date") == entry_date:
                    # Update existing entry
                    historical_data[box_id][i] = entry
                    existing = True
                    print(f"  🔄 Updated existing entry for {key}")
                    break
            
            if not existing:
                historical_data[box_id].append(entry)
                created_count += 1
                print(f"  ✅ Created entry for {key}")
    
    # Sort entries by date for each box
    for box_id in historical_data:
        historical_data[box_id].sort(key=lambda x: x.get("date", ""))
    
    # Save historical data
    historical_file.parent.mkdir(exist_ok=True)
    with open(historical_file, 'w') as f:
        json.dump(historical_data, f, indent=2)
    
    print(f"\n✅ Created/Updated {created_count} historical entries")
    print(f"📁 Data saved to: {historical_file}")
    return created_count


def update_leaderboard_with_latest():
    """Update leaderboard.json with latest metrics from Jan 21 data"""
    data_file = Path(__file__).parent.parent / "data" / "leaderboard.json"
    
    with open(data_file, 'r') as f:
        leaderboard = json.load(f)
    
    updated_count = 0
    
    for box in leaderboard.get("data", []):
        product_name = box.get("product_name", "")
        
        # Find matching set code
        import re
        set_code_match = re.search(r'(OP|EB|PRB)-\d+', product_name, re.IGNORECASE)
        if not set_code_match:
            continue
        
        set_code = set_code_match.group(0).upper()
        
        # Check if it's Blue or White variant
        key = None
        if "(Blue)" in product_name:
            key = "OP-01 (Blue)" if set_code == "OP-01" else set_code
        elif "(White)" in product_name:
            key = "OP-01 (White)" if set_code == "OP-01" else set_code
        else:
            key = set_code
        
        if key not in january_21_data:
            continue
        
        day_data = january_21_data[key]
        
        # Update metrics
        if "metrics" not in box:
            box["metrics"] = {}
        
        box["metrics"]["active_listings_count"] = day_data["active_listings_count"]
        box["metrics"]["floor_price_usd"] = day_data["floor_price_usd"]
        box["metrics"]["daily_volume_usd"] = day_data["daily_volume_usd"]
        box["metrics"]["units_sold_count"] = day_data["boxes_sold_today"]
        box["metrics"]["boxes_sold_per_day"] = day_data["boxes_sold_today"]
        box["metric_date"] = "2026-01-21"
        
        updated_count += 1
        print(f"✅ Updated leaderboard for {key}")
    
    with open(data_file, 'w') as f:
        json.dump(leaderboard, f, indent=2)
    
    print(f"\n✅ Updated {updated_count} boxes in leaderboard")
    return updated_count


if __name__ == "__main__":
    print("=" * 60)
    print("📊 January 20-21, 2026 Historical Data Import")
    print("=" * 60)
    
    # Create historical entries
    create_historical_entries()
    
    print("\n" + "=" * 60)
    print("📈 Updating Leaderboard with Latest Data")
    print("=" * 60)
    
    # Update leaderboard with latest data
    update_leaderboard_with_latest()
    
    print("\n" + "=" * 60)
    print("✅ Data import complete!")
    print("=" * 60)

