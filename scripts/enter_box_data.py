"""
Universal Box Data Entry Script
================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())


================================
Use this single script to enter listings and/or sales data for ANY booster box.

Usage:
    python scripts/enter_box_data.py

The script will prompt you for:
1. Box name (e.g., "OP-11", "OP-13", "EB-01")
2. Entry date (defaults to today)
3. Floor price
4. Listings data (optional)
5. Sales data (optional)

All filtering (JP, 25% below floor) and calculations happen automatically.
"""

import sys
import asyncio
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.automated_screenshot_processor import process_screenshot_data


# Box name mappings for convenience
BOX_NAME_MAP = {
    "op-01": "One Piece - OP-01 Romance Dawn Booster Box",
    "op-01-blue": "One Piece - OP-01 Romance Dawn Booster Box (Blue)",
    "op-01-white": "One Piece - OP-01 Romance Dawn Booster Box (White)",
    "op-02": "One Piece - OP-02 Paramount War Booster Box",
    "op-03": "One Piece - OP-03 Pillars of Strength Booster Box",
    "op-04": "One Piece - OP-04 Kingdoms of Intrigue Booster Box",
    "op-05": "One Piece - OP-05 Awakening of the New Era Booster Box",
    "op-06": "One Piece - OP-06 Wings of the Captain Booster Box",
    "op-07": "One Piece - OP-07 500 Years In The Future Booster Box",
    "op-08": "One Piece - OP-08 Two Legends Booster Box",
    "op-09": "One Piece - OP-09 Emperors of the New World Booster Box",
    "op-10": "One Piece - OP-10 Royal Blood Booster Box",
    "op-11": "One Piece - OP-11 A Fist of Divine Speed Booster Box",
    "op-12": "One Piece - OP-12 Legacy of the Master Booster Box",
    "op-13": "One Piece - OP-13 Carrying on His Will Booster Box",
    "eb-01": "One Piece - EB-01 Memorial Collection Booster Box",
    "eb-02": "One Piece - EB-02 Anime 25th Collection Booster Box",
    "prb-01": "One Piece - PRB-01 Premium Booster Box (The Best)",
}


def get_full_box_name(short_name: str) -> str:
    """Convert short name to full database name"""
    key = short_name.lower().strip()
    if key in BOX_NAME_MAP:
        return BOX_NAME_MAP[key]
    # If not found, return as-is (might be full name already)
    return short_name


async def process_data(box_name: str, entry_date: str, raw_data: dict):
    """Process the data and save to database"""
    full_name = get_full_box_name(box_name)
    
    print(f"\n📦 Processing: {full_name}")
    print(f"📅 Date: {entry_date}")
    print(f"💰 Floor Price: ${raw_data.get('floor_price', 0):.2f}")
    print(f"📋 Listings: {len(raw_data.get('listings', []))}")
    print(f"🛒 Sales: {len(raw_data.get('sales', []))}")
    
    result = await process_screenshot_data(
        raw_data=raw_data,
        box_name=full_name,
        entry_date=entry_date
    )
    
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ SUCCESS!")
        print(f"Message: {result.get('message', 'Data saved')}")
        
        # Show filtering results
        filtering = result.get('steps', {}).get('filtering', {})
        if filtering:
            print(f"\n📊 Filtering:")
            print(f"   Listings: {filtering.get('listings_before', 0)} → {filtering.get('listings_after', 0)}")
            print(f"   Sales: {filtering.get('sales_before', 0)} → {filtering.get('sales_after', 0)}")
        
        # Show key metrics
        metrics = result.get('metrics', {})
        if metrics:
            print(f"\n📈 Updated Metrics:")
            if metrics.get('floor_price_usd'):
                print(f"   Floor Price: ${metrics['floor_price_usd']:.2f}")
            if metrics.get('unified_volume_7d_ema'):
                print(f"   7-Day EMA Volume: ${metrics['unified_volume_7d_ema']:.2f}")
            if metrics.get('active_listings_count') is not None:
                print(f"   Active Listings: {metrics['active_listings_count']}")
            if metrics.get('boxes_sold_per_day') is not None:
                print(f"   Boxes Sold/Day: {metrics['boxes_sold_per_day']}")
    else:
        print("❌ FAILED!")
        for error in result.get('errors', []):
            print(f"   Error: {error}")
    
    return result


# ============================================================================
# DATA ENTRY SECTION - Edit the data below for each entry
# ============================================================================

# Box identifier (use short name like "op-11" or full name)
BOX_NAME = "eb-02"

# Entry date (YYYY-MM-DD format, or None for today)
ENTRY_DATE = "2026-01-04"

# Floor price (lowest listing price, not including shipping)
FLOOR_PRICE = 599.00
FLOOR_SHIPPING = 0.00

# Listings data - none for this run
LISTINGS = []

# Sales data - EB-02 corrected sales for January 4, 2026 (1 sale, not 0)
SALES = [
    {"price": 599.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "One Piece EB-02 Anime 25th Collection Booster Box", "platform": "ebay"},
]

# ============================================================================
# END DATA ENTRY SECTION
# ============================================================================


async def main():
    """Main entry point"""
    entry_date = ENTRY_DATE or date.today().isoformat()
    
    raw_data = {
        "floor_price": FLOOR_PRICE,
        "floor_price_shipping": FLOOR_SHIPPING,
        "listings": LISTINGS,
        "sales": SALES
    }
    
    # Check if there's any data to process
    if not LISTINGS and not SALES:
        print("⚠️  No listings or sales data provided.")
        print("   Edit the LISTINGS and/or SALES variables in this script.")
        print("\n   Example listing:")
        print('   {"price": 300.00, "shipping": 15.99, "quantity": 1, "seller": "Seller", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        print("\n   Example sale:")
        print('   {"price": 300.00, "shipping": 0.00, "quantity": 1, "date": "2026-01-04", "seller": "unknown", "title": "OP-11 Booster Box", "platform": "tcgplayer"}')
        return
    
    await process_data(BOX_NAME, entry_date, raw_data)


if __name__ == "__main__":
    print("=" * 50)
    print("📦 Universal Box Data Entry Script")
    print("=" * 50)
    asyncio.run(main())

