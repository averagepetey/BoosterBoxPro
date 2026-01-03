"""
Create historical entries for October 30, 2025 data
"""

import json
from pathlib import Path
from datetime import datetime

# Data from spreadsheet
october_30_data = {
    "OP-01 (Blue)": {
        "floor_price_usd": 2584.26,
        "active_listings_count": 2,
        "boxes_sold_per_day": 0.75,
    },
    "OP-01 (White)": {
        "floor_price_usd": 621.61,
        "active_listings_count": 0,
        "boxes_sold_per_day": 0.96,
    },
    "OP-02": {
        "floor_price_usd": 229.95,
        "active_listings_count": 55,
        "boxes_sold_per_day": 0.71,
    },
    "OP-03": {
        "floor_price_usd": 279.25,
        "active_listings_count": 1,
        "boxes_sold_per_day": 0.64,
    },
    "OP-04": {
        "floor_price_usd": 247.36,
        "active_listings_count": 8,
        "boxes_sold_per_day": 0.61,
    },
    "OP-05": {
        "floor_price_usd": 357.99,
        "active_listings_count": 15,
        "boxes_sold_per_day": 2.75,
    },
    "OP-06": {
        "floor_price_usd": 160.63,
        "active_listings_count": 37,
        "boxes_sold_per_day": 1.86,
    },
    "EB-01": {
        "floor_price_usd": 390.24,
        "active_listings_count": 2,
        "boxes_sold_per_day": 0.46,
    },
    "OP-07": {
        "floor_price_usd": 122.80,
        "active_listings_count": 51,
        "boxes_sold_per_day": 0.96,
    },
    "OP-08": {
        "floor_price_usd": 100.62,
        "active_listings_count": 54,
        "boxes_sold_per_day": 0.71,
    },
    "PRB-01": {
        "floor_price_usd": 452.62,
        "active_listings_count": 8,
        "boxes_sold_per_day": 0.50,
    },
    "OP-09": {
        "floor_price_usd": 214.22,
        "active_listings_count": 26,
        "boxes_sold_per_day": 2.18,
    },
    "OP-10": {
        "floor_price_usd": 96.98,
        "active_listings_count": 7,
        "boxes_sold_per_day": 1.25,
    },
    "EB-02": {
        "floor_price_usd": 232.77,
        "active_listings_count": 36,
        "boxes_sold_per_day": 0.64,
    },
    "OP-11": {
        "floor_price_usd": 139.10,
        "active_listings_count": 90,
        "boxes_sold_per_day": 1.64,
    },
    "OP-12": {
        "floor_price_usd": 106.65,
        "active_listings_count": 430,
        "boxes_sold_per_day": 3.04,
    },
    "PRB-02": {
        "floor_price_usd": 163.39,
        "active_listings_count": 217,
        "boxes_sold_per_day": 3.61,
    },
}

def create_historical_entries():
    """Create historical entries for October 30, 2025"""
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
    
    entry_date = "2025-10-30"
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
        
        if key not in october_30_data:
            continue
        
        box_data = october_30_data[key]
        
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


