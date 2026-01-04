"""
Process OP-11 Listings Data from TCGplayer Screenshot
Date: January 4, 2026
Source: TCGplayer marketplace listings
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 listings data from January 4, 2026"""
    
    # Entry date
    entry_date = "2026-01-04"
    
    # Raw data extracted from TCGplayer screenshots
    raw_data = {
        "floor_price": 300.00,  # Tsuta Ledger - lowest price
        "floor_price_shipping": 15.99,  # Shipping for floor listing
        "listings": [
            # Page 1
            {
                "price": 300.00,
                "shipping": 15.99,
                "quantity": 1,
                "seller": "Tsuta Ledger",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 311.12,
                "shipping": 13.00,
                "quantity": 1,
                "seller": "UpperTunnel",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 14.99,
                "quantity": 1,
                "seller": "NE Arkys Store",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 344.98,
                "shipping": 0.00,
                "quantity": 1,
                "seller": "Showdown Value Cards",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 348.98,
                "shipping": 0.00,
                "quantity": 1,
                "seller": "BMC Collectibles TCG",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # Page 2
            {
                "price": 348.99,
                "shipping": 0.00,
                "quantity": 8,
                "seller": "MultiMonster Deals",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 349.00,
                "shipping": 0.00,
                "quantity": 5,
                "seller": "blujay",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 349.97,
                "shipping": 0.00,
                "quantity": 2,
                "seller": "mnbaseball",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 345.00,
                "shipping": 5.00,
                "quantity": 1,
                "seller": "GX Shops",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 350.00,
                "shipping": 0.00,
                "quantity": 1,
                "seller": "JY Production",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 360.00,
                "shipping": 14.99,
                "quantity": 1,
                "seller": "GameRave",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # Page 3
            {
                "price": 379.99,
                "shipping": 0.00,
                "quantity": 5,
                "seller": "Stacked Deck LLC",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 380.00,
                "shipping": 0.00,
                "quantity": 8,
                "seller": "WildCardCyclone",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 389.99,
                "shipping": 0.00,
                "quantity": 1,
                "seller": "Miami Card Supply",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 375.00,
                "shipping": 14.99,
                "quantity": 5,
                "seller": "Rivero Press",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # Page 4
            {
                "price": 399.99,
                "shipping": 0.00,
                "quantity": 12,
                "seller": "RR Precon",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 399.99,
                "shipping": 0.00,
                "quantity": 1,
                "seller": "BoosterBooster TCG",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 398.99,
                "shipping": 4.99,
                "quantity": 2,
                "seller": "Token TCG",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 399.99,
                "shipping": 7.99,
                "quantity": 1,
                "seller": "OmniKing",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 245.00,
                "shipping": 199.99,
                "quantity": 1,
                "seller": "Blacktokyo",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ],
        "sales": []  # No sales data provided in screenshots
    }
    
    print("=" * 60)
    print("Processing OP-11 Listings Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count total listings
    total_quantity = sum(l.get("quantity", 1) for l in raw_data["listings"])
    print(f"\nTotal Listings: {len(raw_data['listings'])} sellers")
    print(f"Total Boxes Available: {total_quantity}")
    print(f"Floor Price: ${raw_data['floor_price']:.2f} + ${raw_data['floor_price_shipping']:.2f} shipping")
    
    # Process the data
    print("\nProcessing...")
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name="One Piece - OP-11 A Fist of Divine Speed Booster Box",
        entry_date=entry_date
    )
    
    print("\n" + "=" * 60)
    print("Processing Result")
    print("=" * 60)
    print(f"Success: {result['success']}")
    
    if result.get('message'):
        print(f"Message: {result['message']}")
    
    if result.get('errors'):
        print(f"\n❌ Errors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    if result.get('steps'):
        print(f"\n📋 Steps Completed:")
        for step, status in result['steps'].items():
            print(f"  - {step}: {status}")
    
    if result.get('metrics'):
        print(f"\n📊 Calculated Metrics:")
        for metric, value in result['metrics'].items():
            if value is not None:
                if isinstance(value, float):
                    print(f"  - {metric}: {value:.2f}")
                else:
                    print(f"  - {metric}: {value}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main())

