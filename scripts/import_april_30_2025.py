"""
Import April 30, 2025 data for all booster boxes
Direct JSON update approach
"""

import json
from pathlib import Path
from datetime import date

# Data extracted from spreadsheet
april_30_2025_data = {
    "OP-01 (Blue)": {
        "floor_price_usd": 1215.61,
        "active_listings_count": 0,
        "boxes_sold_per_day": 0.71,
    },
    "OP-01 (White)": {
        "floor_price_usd": 403.88,
        "active_listings_count": 7,
        "boxes_sold_per_day": 0.43,
    },
    "OP-02": {
        "floor_price_usd": 231.36,
        "active_listings_count": 106,
        "boxes_sold_per_day": 0.43,
    },
    "OP-03": {
        "floor_price_usd": 220.76,
        "active_listings_count": 19,
        "boxes_sold_per_day": 0.71,
    },
    "OP-04": {
        "floor_price_usd": 180.64,
        "active_listings_count": 20,
        "boxes_sold_per_day": 0.86,
    },
    "OP-05": {
        "floor_price_usd": 259.34,
        "active_listings_count": 49,
        "boxes_sold_per_day": 2.00,
    },
    "OP-06": {
        "floor_price_usd": 144.35,
        "active_listings_count": 17,
        "boxes_sold_per_day": 1.29,
    },
    "EB-01": {
        "floor_price_usd": 314.36,
        "active_listings_count": 9,
        "boxes_sold_per_day": 0.14,
    },
    "OP-07": {
        "floor_price_usd": 112.19,
        "active_listings_count": 20,
        "boxes_sold_per_day": 0.86,
    },
    "OP-08": {
        "floor_price_usd": 95.54,
        "active_listings_count": 239,
        "boxes_sold_per_day": 1.00,
    },
    "PRB-01": {
        "floor_price_usd": 282.12,
        "active_listings_count": 19,
        "boxes_sold_per_day": 0.71,
    },
    "OP-09": {
        "floor_price_usd": 185.39,
        "active_listings_count": 70,
        "boxes_sold_per_day": 2.14,
    },
    "OP-10": {
        "floor_price_usd": 91.99,
        "active_listings_count": 337,
        "boxes_sold_per_day": 3.00,
    },
}

def update_leaderboard_data():
    """Update leaderboard.json with April 30, 2025 data"""
    data_file = Path(__file__).parent.parent / "data" / "leaderboard.json"
    mock_file = Path(__file__).parent.parent / "mock_data" / "leaderboard.json"
    
    # Load existing data
    if data_file.exists():
        with open(data_file, 'r') as f:
            data = json.load(f)
    elif mock_file.exists():
        with open(mock_file, 'r') as f:
            data = json.load(f)
    else:
        print("No data file found")
        return
    
    entry_date = "2025-04-30"
    updated_count = 0
    
    # Update each box
    for box in data.get("data", []):
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
        
        if key not in april_30_2025_data:
            continue
        
        box_data = april_30_2025_data[key]
        
        # Update metrics
        if "metrics" not in box:
            box["metrics"] = {}
        
        # Update with new data
        box["metrics"]["floor_price_usd"] = box_data["floor_price_usd"]
        box["metrics"]["active_listings_count"] = box_data["active_listings_count"]
        box["metrics"]["boxes_sold_per_day"] = box_data["boxes_sold_per_day"]
        box["metrics"]["units_sold_count"] = int(box_data["boxes_sold_per_day"])  # Use as daily count
        
        # Update metric_date
        box["metric_date"] = entry_date
        
        updated_count += 1
        print(f"✅ Updated {set_code}: Floor ${box_data['floor_price_usd']}, Listings {box_data['active_listings_count']}, Sales {box_data['boxes_sold_per_day']}/day")
    
    # Save updated data
    data_file.parent.mkdir(exist_ok=True)
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Updated {updated_count} boxes for {entry_date}")
    return updated_count

if __name__ == "__main__":
    update_leaderboard_data()


