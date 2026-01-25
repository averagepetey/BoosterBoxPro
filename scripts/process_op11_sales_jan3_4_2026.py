"""
Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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




Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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




Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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





Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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




Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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




Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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





Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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




Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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




Process OP-11 Sales Data from TCGplayer Screenshot
Dates: January 3-4, 2026
Source: TCGplayer sales history
"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


async def main():
    """Process OP-11 sales data from January 3-4, 2026"""
    
    # Entry date - use the most recent date
    entry_date = "2026-01-04"
    
    # Raw sales data extracted from TCGplayer screenshot
    # Note: The $84.99 Japanese item will be auto-filtered
    raw_data = {
        "floor_price": 300.00,  # From previous listing data
        "floor_price_shipping": 15.99,
        "listings": [],  # No new listings, just sales
        "sales": [
            # January 4, 2026
            {
                "price": 300.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-04",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # January 3, 2026
            {
                "price": 324.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 320.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 285.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 310.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            # This one should be auto-filtered (JP)
            {
                "price": 84.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "FIST OF DIVINE SPEED (JAPANESE)",
                "platform": "tcgplayer"
            },
            {
                "price": 329.99,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 2,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
            {
                "price": 316.00,
                "shipping": 0.00,
                "quantity": 1,
                "date": "2026-01-03",
                "seller": "unknown",
                "title": "OP-11 Booster Box",
                "platform": "tcgplayer"
            },
        ]
    }
    
    print("=" * 60)
    print("Processing OP-11 Sales Data")
    print(f"Date: {entry_date}")
    print("=" * 60)
    
    # Count sales
    total_sales = sum(s.get("quantity", 1) for s in raw_data["sales"])
    total_volume = sum(s.get("price", 0) * s.get("quantity", 1) for s in raw_data["sales"])
    print(f"\nTotal Sales: {len(raw_data['sales'])} transactions")
    print(f"Total Units Sold: {total_sales}")
    print(f"Total Volume: ${total_volume:.2f}")
    
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






