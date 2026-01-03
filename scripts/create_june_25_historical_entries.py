"""
Create historical entries for June 25, 2025 data
"""

import json
from pathlib import Path
from datetime import datetime

# Data from spreadsheet
june_25_data = {
    "OP-01 (Blue)": {
        "floor_price_usd": 1270.17,
        "active_listings_count": 4,
        "boxes_sold_per_day": 0.43,
    },
    "OP-01 (White)": {
        "floor_price_usd": 433.53,
        "active_listings_count": 25,
        "boxes_sold_per_day": 0.71,
    },
    "OP-02": {
        "floor_price_usd": 201.49,
        "active_listings_count": 19,
        "boxes_sold_per_day": 0.57,
    },
    "OP-03": {
        "floor_price_usd": 230.37,
        "active_listings_count": 20,
        "boxes_sold_per_day": 0.86,
    },
    "OP-04": {
        "floor_price_usd": 185.07,
        "active_listings_count": 5,
        "boxes_sold_per_day": 0.57,
    },
    "OP-05": {
        "floor_price_usd": 233.30,
        "active_listings_count": 55,
        "boxes_sold_per_day": 4.00,
    },
    "OP-06": {
        "floor_price_usd": 153.25,
        "active_listings_count": 84,
        "boxes_sold_per_day": 1.00,
    },
    "EB-01": {
        "floor_price_usd": 319.89,
        "active_listings_count": 24,
        "boxes_sold_per_day": 0.00,
    },
    "OP-07": {
        "floor_price_usd": 119.30,
        "active_listings_count": 61,
        "boxes_sold_per_day": 1.14,
    },
    "OP-08": {
        "floor_price_usd": 106.08,
        "active_listings_count": 314,
        "boxes_sold_per_day": 1.00,
    },
    "PRB-01": {
        "floor_price_usd": 265.81,
        "active_listings_count": 35,
        "boxes_sold_per_day": 0.71,
    },
    "OP-09": {
        "floor_price_usd": 178.10,
        "active_listings_count": 207,
        "boxes_sold_per_day": 1.86,
    },
    "OP-10": {
        "floor_price_usd": 96.15,
        "active_listings_count": 288,
        "boxes_sold_per_day": 1.71,
    },
    "EB-02": {
        "floor_price_usd": 176.29,
        "active_listings_count": 135,
        "boxes_sold_per_day": 1.57,
    },
    "OP-11": {
        "floor_price_usd": 125.40,
        "active_listings_count": 414,
        "boxes_sold_per_day": 3.00,
    },
}

def create_historical_entries():
    """Create historical entries for June 25, 2025"""
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
    
    entry_date = "2025-06-25"
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
        
        if key not in june_25_data:
            continue
        
        box_data = june_25_data[key]
        
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


