"""
Process April 30, 2025 data for all booster boxes
"""

import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.chat_data_entry import ChatDataEntry

# Data extracted from the spreadsheet screenshot
april_30_data = [
    {
        "set_code": "OP-01",
        "product_name": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
        "floor_price_usd": 1215.61,
        "active_listings_count": 0,
        "boxes_sold_per_day": 0.71,
    },
    {
        "set_code": "OP-01",
        "product_name": "One Piece - OP-01 Romance Dawn Booster Box (White)",
        "floor_price_usd": 403.88,
        "active_listings_count": 7,
        "boxes_sold_per_day": 0.43,
    },
    {
        "set_code": "OP-02",
        "product_name": "One Piece - OP-02 Paramount War Booster Box",
        "floor_price_usd": 231.36,
        "active_listings_count": 106,
        "boxes_sold_per_day": 0.43,
    },
    {
        "set_code": "OP-03",
        "product_name": "One Piece - OP-03 Pillars of Strength Booster Box",
        "floor_price_usd": 220.76,
        "active_listings_count": 19,
        "boxes_sold_per_day": 0.71,
    },
    {
        "set_code": "OP-04",
        "product_name": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
        "floor_price_usd": 180.64,
        "active_listings_count": 20,
        "boxes_sold_per_day": 0.86,
    },
    {
        "set_code": "OP-05",
        "product_name": "One Piece - OP-05 Awakening of the New Era Booster Box",
        "floor_price_usd": 259.34,
        "active_listings_count": 49,
        "boxes_sold_per_day": 2.00,
    },
    {
        "set_code": "OP-06",
        "product_name": "One Piece - OP-06 Wings of the Captain Booster Box",
        "floor_price_usd": 144.35,
        "active_listings_count": 17,
        "boxes_sold_per_day": 1.29,
    },
    {
        "set_code": "EB-01",
        "product_name": "One Piece - EB-01 Memorial Collection Booster Box",
        "floor_price_usd": 314.36,
        "active_listings_count": 9,
        "boxes_sold_per_day": 0.14,
    },
    {
        "set_code": "OP-07",
        "product_name": "One Piece - OP-07 500 Years in the Future Booster Box",
        "floor_price_usd": 112.19,
        "active_listings_count": 20,
        "boxes_sold_per_day": 0.86,
    },
    {
        "set_code": "OP-08",
        "product_name": "One Piece - OP-08 Two Legends Booster Box",
        "floor_price_usd": 95.54,
        "active_listings_count": 239,
        "boxes_sold_per_day": 1.00,
    },
    {
        "set_code": "PRB-01",
        "product_name": "One Piece - PRB-01 Premium Booster Box",
        "floor_price_usd": 282.12,
        "active_listings_count": 19,
        "boxes_sold_per_day": 0.71,
    },
    {
        "set_code": "OP-09",
        "product_name": "One Piece - OP-09 Emperors in the New World Booster Box",
        "floor_price_usd": 185.39,
        "active_listings_count": 70,
        "boxes_sold_per_day": 2.14,
    },
    {
        "set_code": "OP-10",
        "product_name": "One Piece - OP-10 Royal Blood Booster Box",
        "floor_price_usd": 91.99,
        "active_listings_count": 337,
        "boxes_sold_per_day": 3.00,
    },
]

def process_all_boxes():
    """Process all boxes for April 30, 2025"""
    processor = ChatDataEntry()
    entry_date = "2025-04-30"
    
    results = []
    
    for box_data in april_30_data:
        # Create text representation for processing
        text_data = f"{box_data['product_name']}: Floor ${box_data['floor_price_usd']}, Listings {box_data['active_listings_count']}, Sales {box_data['boxes_sold_per_day']}"
        
        # Process the data
        result = processor.process_chat_data(text_data)
        
        # Override the date to April 30, 2025
        if result.get("success"):
            # Update the entry date in the historical data
            from scripts.historical_data_manager import historical_data_manager
            if historical_data_manager:
                existing_data = processor.load_existing_data()
                box = None
                for b in existing_data.get("data", []):
                    if b.get("product_name") == box_data["product_name"]:
                        box = b
                        break
                
                if box:
                    box_id = box.get("id")
                    # Get the latest entry and update its date
                    history = historical_data_manager.get_box_history(box_id)
                    if history:
                        # Update the most recent entry's date
                        latest = history[-1]
                        latest["date"] = entry_date
                        # Save updated history
                        all_data = historical_data_manager.load_historical_data()
                        all_data[box_id] = history
                        historical_data_manager.save_historical_data(all_data)
        
        results.append({
            "box": box_data["set_code"],
            "success": result.get("success", False),
            "message": result.get("message", "Unknown error")
        })
    
    return results

if __name__ == "__main__":
    results = process_all_boxes()
    for r in results:
        print(f"{r['box']}: {'✅' if r['success'] else '❌'} {r['message']}")


