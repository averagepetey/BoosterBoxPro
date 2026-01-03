"""
Create historical entries for November 27, 2025 data
"""

import json
from pathlib import Path
from datetime import datetime

# Data from spreadsheet
november_27_data = {
    "OP-01 (Blue)": {
        "floor_price_usd": 3020.64,
        "active_listings_count": 0,
        "boxes_sold_per_day": 1.79,
    },
    "OP-01 (White)": {
        "floor_price_usd": 996.99,
        "active_listings_count": 0,
        "boxes_sold_per_day": 1.11,
    },
    "OP-02": {
        "floor_price_usd": 247.16,
        "active_listings_count": 17,
        "boxes_sold_per_day": 1.39,
    },
    "OP-03": {
        "floor_price_usd": 337.07,
        "active_listings_count": 18,
        "boxes_sold_per_day": 0.54,
    },
    "OP-04": {
        "floor_price_usd": 242.55,
        "active_listings_count": 24,
        "boxes_sold_per_day": 0.71,
    },
    "OP-05": {
        "floor_price_usd": 406.72,
        "active_listings_count": 0,
        "boxes_sold_per_day": 2.14,
    },
    "OP-06": {
        "floor_price_usd": 191.70,
        "active_listings_count": 58,
        "boxes_sold_per_day": 1.82,
    },
    "EB-01": {
        "floor_price_usd": 486.97,
        "active_listings_count": 7,
        "boxes_sold_per_day": 0.82,
    },
    "OP-07": {
        "floor_price_usd": 122.42,
        "active_listings_count": 8,
        "boxes_sold_per_day": 1.04,
    },
    "OP-08": {
        "floor_price_usd": 109.01,
        "active_listings_count": 91,
        "boxes_sold_per_day": 0.61,
    },
    "PRB-01": {
        "floor_price_usd": 554.59,
        "active_listings_count": 0,
        "boxes_sold_per_day": 0.79,
    },
    "OP-09": {
        "floor_price_usd": 240.41,
        "active_listings_count": 34,
        "boxes_sold_per_day": 0.68,
    },
    "OP-10": {
        "floor_price_usd": 102.32,
        "active_listings_count": 38,
        "boxes_sold_per_day": 1.07,
    },
    "EB-02": {
        "floor_price_usd": 260.52,
        "active_listings_count": 0,
        "boxes_sold_per_day": 1.00,
    },
    "OP-11": {
        "floor_price_usd": 167.07,
        "active_listings_count": 104,
        "boxes_sold_per_day": 2.89,
    },
    "OP-12": {
        "floor_price_usd": 104.22,
        "active_listings_count": 217,
        "boxes_sold_per_day": 1.50,
    },
    "PRB-02": {
        "floor_price_usd": 176.87,
        "active_listings_count": 79,
        "boxes_sold_per_day": 2.14,
    },
    "OP-13": {
        "floor_price_usd": 182.19,
        "active_listings_count": 87,
        "boxes_sold_per_day": 8.39,
    },
}

def create_historical_entries():
    """Create historical entries for November 27, 2025"""
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
    
    entry_date = "2025-11-27"
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
        
        if key not in november_27_data:
            continue
        
        box_data = november_27_data[key]
        
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


