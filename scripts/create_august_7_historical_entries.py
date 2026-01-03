"""
Create historical entries for August 7, 2025 data
"""

import json
from pathlib import Path
from datetime import datetime

# Data from spreadsheet
august_7_data = {
    "OP-01 (Blue)": {
        "floor_price_usd": 1530.67,
        "active_listings_count": 1,
        "boxes_sold_per_day": 0.50,
    },
    "OP-01 (White)": {
        "floor_price_usd": 436.58,
        "active_listings_count": 2,
        "boxes_sold_per_day": 1.00,
    },
    "OP-02": {
        "floor_price_usd": 202.82,
        "active_listings_count": 21,
        "boxes_sold_per_day": 0.79,
    },
    "OP-03": {
        "floor_price_usd": 239.06,
        "active_listings_count": 8,
        "boxes_sold_per_day": 1.14,
    },
    "OP-04": {
        "floor_price_usd": 192.48,
        "active_listings_count": 11,
        "boxes_sold_per_day": 0.36,
    },
    "OP-05": {
        "floor_price_usd": 235.92,
        "active_listings_count": 57,
        "boxes_sold_per_day": 2.25,
    },
    "OP-06": {
        "floor_price_usd": 153.44,
        "active_listings_count": 122,
        "boxes_sold_per_day": 1.50,
    },
    "EB-01": {
        "floor_price_usd": 317.86,
        "active_listings_count": 3,
        "boxes_sold_per_day": 0.71,
    },
    "OP-07": {
        "floor_price_usd": 132.71,
        "active_listings_count": 86,
        "boxes_sold_per_day": 1.36,
    },
    "OP-08": {
        "floor_price_usd": 105.74,
        "active_listings_count": 249,
        "boxes_sold_per_day": 0.82,
    },
    "PRB-01": {
        "floor_price_usd": 330.90,
        "active_listings_count": 5,
        "boxes_sold_per_day": 0.46,
    },
    "OP-09": {
        "floor_price_usd": 186.90,
        "active_listings_count": 88,
        "boxes_sold_per_day": 2.50,
    },
    "OP-10": {
        "floor_price_usd": 99.66,
        "active_listings_count": 137,
        "boxes_sold_per_day": 1.46,
    },
    "EB-02": {
        "floor_price_usd": 173.33,
        "active_listings_count": 60,
        "boxes_sold_per_day": 0.82,
    },
    "OP-11": {
        "floor_price_usd": 132.37,
        "active_listings_count": 60,
        "boxes_sold_per_day": 2.71,
    },
}

def create_historical_entries():
    """Create historical entries for August 7, 2025"""
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
    
    entry_date = "2025-08-07"
    created_count = 0
    
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
        
        if key not in august_7_data:
            continue
        
        box_data = august_7_data[key]
        
        # Create historical entry
        entry = {
            "date": entry_date,
            "source": "spreadsheet_import",
            "data_type": "combined",
            "floor_price_usd": box_data["floor_price_usd"],
            "active_listings_count": box_data["active_listings_count"],
            "boxes_sold_today": box_data["boxes_sold_per_day"],
            "boxes_sold_per_day": box_data["boxes_sold_per_day"],
            "timestamp": datetime.now().isoformat()
        }
        
        if box_id not in historical_data:
            historical_data[box_id] = []
        
        # Check if entry already exists for this date
        existing = False
        for e in historical_data[box_id]:
            if e.get("date") == entry_date:
                existing = True
                break
        
        if not existing:
            historical_data[box_id].append(entry)
            created_count += 1
            print(f"✅ Created historical entry for {set_code}")
    
    # Save historical data
    historical_file.parent.mkdir(exist_ok=True)
    with open(historical_file, 'w') as f:
        json.dump(historical_data, f, indent=2)
    
    print(f"\n✅ Created {created_count} historical entries for {entry_date}")
    return created_count

if __name__ == "__main__":
    create_historical_entries()


