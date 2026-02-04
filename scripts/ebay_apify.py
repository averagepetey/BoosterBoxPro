#!/usr/bin/env python3
"""
eBay Apify Scraper
------------------
Fetches eBay sold listings via Apify actor (3x1t/ebay-scraper-ppr).
Replaces custom Playwright scraper with reliable Apify-managed scraping.

Cost: Pay-per-result at $0.99 per 1,000 results (~$24/month for 18 boxes daily)
Tiered limits: hot=85, medium=50, slow=10 results per box

Run standalone: python scripts/ebay_apify.py [--debug <box_id>]
Called by daily_refresh.py as Phase 1b (after TCGplayer Apify).
"""

import json
import logging
import re
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urlencode

from apify_client import ApifyClient

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings

logger = logging.getLogger(__name__)

HISTORICAL_FILE = project_root / "data" / "historical_entries.json"

# Price floor as fraction of TCG market price (75% = reject below 25% discount)
MIN_PRICE_RATIO = 0.75

# Tiered result limits by box activity level (controls cost)
# Hot: 5 boxes × 85 = 425/day, Medium: 6 × 50 = 300/day, Slow: 7 × 10 = 70/day
# Total: 795/day × 30 = 23,850/month × $0.99/1000 = ~$24/month
RESULTS_LIMIT_HOT = 85
RESULTS_LIMIT_MEDIUM = 50
RESULTS_LIMIT_SLOW = 10

# Apify actor to use (PPR = Pay Per Result, $0.99/1000, >99% success rate)
APIFY_ACTOR = "3x1t/ebay-scraper-ppr"

# URL negative keywords - excluded at eBay level (FREE filtering)
# Note: -pack and -case omitted to allow "24 packs" and "case fresh" exceptions
URL_NEGATIVE_KEYWORDS = [
    "-japanese", "-korean", "-chinese", "-thai", "-jp", "-taiwan",
    "-display", "-playmat", "-sleeve", "-break", "-repack",
    "-damaged", "-opened", "-empty", "-custom", "-promo", "-resealed",
]

# eBay search configuration for each box
# Search terms: no "english" (LH_PrefLoc=1 handles US-only), negatives appended dynamically
# Tier: "hot" (newest/high demand), "medium" (established), "slow" (older sets)
EBAY_BOX_CONFIG: Dict[str, Dict[str, Any]] = {
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {
        "name": "OP-01 Romance Dawn (Blue)",
        "search": "one piece op-01 romance dawn booster box blue",
        "max_price": 500,
        "tier": "slow",
    },
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": {
        "name": "OP-01 Romance Dawn (White)",
        "search": "one piece op-01 romance dawn booster box white",
        "max_price": 400,
        "tier": "slow",
    },
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": {
        "name": "OP-02 Paramount War",
        "search": "one piece op-02 paramount war booster box",
        "max_price": 400,
        "tier": "slow",
    },
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": {
        "name": "OP-03 Pillars of Strength",
        "search": "one piece op-03 pillars of strength booster box",
        "max_price": 400,
        "tier": "slow",
    },
    "526c28b7-bc13-449b-a521-e63bdd81811a": {
        "name": "OP-04 Kingdoms of Intrigue",
        "search": "one piece op-04 kingdoms intrigue booster box",
        "max_price": 350,
        "tier": "slow",
    },
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": {
        "name": "OP-05 Awakening of the New Era",
        "search": "one piece op-05 awakening new era booster box",
        "max_price": 500,
        "tier": "medium",
    },
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": {
        "name": "OP-06 Wings of the Captain",
        "search": "one piece op-06 wings captain booster box",
        "max_price": 350,
        "tier": "medium",
    },
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": {
        "name": "OP-07 500 Years in the Future",
        "search": "one piece op-07 500 years future booster box",
        "max_price": 350,
        "tier": "medium",
    },
    "d0faf871-a930-4c80-a981-9df8741c90a9": {
        "name": "OP-08 Two Legends",
        "search": "one piece op-08 two legends booster box",
        "max_price": 600,
        "tier": "medium",
    },
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": {
        "name": "OP-09 Emperors in the New World",
        "search": "one piece op-09 emperors new world booster box",
        "max_price": 600,
        "tier": "hot",
    },
    "3429708c-43c3-4ed8-8be3-706db8b062bd": {
        "name": "OP-10 Royal Blood",
        "search": "one piece op-10 royal blood booster box",
        "max_price": 600,
        "tier": "hot",
    },
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": {
        "name": "OP-11 A Fist of Divine Speed",
        "search": "one piece op-11 fist divine speed booster box",
        "max_price": 700,
        "tier": "hot",
    },
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": {
        "name": "OP-12 Legacy of the Master",
        "search": "one piece op-12 legacy master booster box",
        "max_price": 600,
        "tier": "hot",
    },
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {
        "name": "OP-13 Carrying on His Will",
        "search": "one piece op-13 carrying his will booster box",
        "max_price": 2500,
        "tier": "hot",
    },
    "3b17b708-b35b-4008-971e-240ade7afc9c": {
        "name": "EB-01 Memorial Collection",
        "search": "one piece eb-01 memorial collection booster box",
        "max_price": 800,
        "tier": "medium",
    },
    "7509a855-f6da-445e-b445-130824d81d04": {
        "name": "EB-02 Anime 25th Collection",
        "search": "one piece eb-02 anime 25th booster box",
        "max_price": 600,
        "tier": "medium",
    },
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": {
        "name": "PRB-01 Premium Booster",
        "search": "one piece prb-01 premium booster box",
        "max_price": 800,
        "tier": "slow",
    },
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": {
        "name": "PRB-02 Premium Booster Vol. 2",
        "search": "one piece prb-02 premium booster vol 2 box",
        "max_price": 600,
        "tier": "slow",
    },
}

# Title keywords to exclude (Python-level safety net)
# Many overlap with URL negatives - this catches edge cases
TITLE_EXCLUSIONS = [
    "japanese", "jp", "korean", "chinese", "thai", "taiwan",
    "single", "card lot", "bundle",
    "damaged", "opened", "resealed", "display",
    "playmat", "sleeve", "deck box", "promo",
    "empty", "no cards", "custom", "repack",
    "check description", "check dis", "broken seal",
    "unsealed", "no seal", "incomplete",
    # Note: "pack", "case", "break" handled separately with exceptions
]

# Non-US/non-English indicators (backup for LH_PrefLoc=1)
NON_US_KEYWORDS = [
    "uk sealed", "uk version", "uk stock", "uk edition",
    "europe", "european", "australia", "australian",
    "canada", "canadian", "italy", "german", "france", "french",
    "spain", "spanish", "netherlands", "dutch", "mexico", "mexican",
    "asia", "asian",
]


def get_max_results(tier: str) -> int:
    """Get max results limit based on box tier."""
    if tier == "hot":
        return RESULTS_LIMIT_HOT
    elif tier == "medium":
        return RESULTS_LIMIT_MEDIUM
    else:
        return RESULTS_LIMIT_SLOW


def build_ebay_sold_url(search_term: str, min_price: int, max_price: int) -> str:
    """
    Build eBay search URL with sold items filter, price range, and negative keywords.

    eBay URL parameters:
    - LH_Complete=1 & LH_Sold=1: Sold items only
    - LH_PrefLoc=1: US sellers only (FREE filtering)
    - _udlo / _udhi: Price range
    - _sop=13: Sort by end date (most recent first)
    - Negative keywords appended to search (FREE filtering)
    """
    # Append negative keywords to search term
    search_with_negatives = search_term + " " + " ".join(URL_NEGATIVE_KEYWORDS)

    base_url = "https://www.ebay.com/sch/i.html"
    params = {
        "_nkw": search_with_negatives,
        "LH_Complete": "1",      # Completed listings
        "LH_Sold": "1",          # Sold items only
        "LH_PrefLoc": "1",       # US sellers only (NEW)
        "_udlo": str(min_price), # Min price
        "_udhi": str(max_price), # Max price
        "_sop": "13",            # Sort by end date (newest first)
        "LH_ItemCondition": "1000",  # New condition
        "_ipg": "240",  # Results per page (eBay max)
    }
    return f"{base_url}?{urlencode(params)}"


def parse_date(date_str: str) -> Optional[str]:
    """Parse eBay date string to ISO format (YYYY-MM-DD)."""
    if not date_str:
        return None

    # Try common eBay date formats
    for fmt in (
        "%b %d, %Y",      # "Jan 15, 2026"
        "%B %d, %Y",      # "January 15, 2026"
        "%Y-%m-%d",       # "2026-01-15"
        "%m/%d/%Y",       # "01/15/2026"
        "%d %b %Y",       # "15 Jan 2026"
    ):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Try to extract date from longer strings
    match = re.search(r'(\w{3})\s+(\d{1,2}),?\s+(\d{4})', date_str)
    if match:
        try:
            dt = datetime.strptime(f"{match.group(1)} {match.group(2)}, {match.group(3)}", "%b %d, %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


def extract_item_id(url: str) -> Optional[str]:
    """Extract eBay item ID from URL."""
    if not url:
        return None
    match = re.search(r'/itm/(\d+)', url)
    return match.group(1) if match else None


def is_excluded_title(title: str) -> bool:
    """Check if title contains exclusion keywords."""
    t = title.lower()
    return any(excl in t for excl in TITLE_EXCLUSIONS)


def is_non_us(title: str) -> bool:
    """Check if listing is non-US/non-English."""
    t = title.lower()
    if re.search(r'\buk\b', t):
        return True
    return any(kw in t for kw in NON_US_KEYWORDS)


def is_case_listing(title: str) -> bool:
    """Check if listing is a case (12+ boxes), not a single box."""
    t = title.lower()
    if "case fresh" in t:
        return False
    return bool(re.search(r'\bcase\b', t))


def is_pack_listing(title: str) -> bool:
    """
    Check if listing is packs (not a sealed box).
    Exception: "24 packs" is valid because a booster box contains 24 packs.
    """
    t = title.lower()
    # Exception: "24 packs" is a valid booster box description
    if re.search(r'\b24\s*packs?\b', t):
        return False
    # Any other pack reference is likely loose packs
    return bool(re.search(r'\bpacks?\b', t))


def is_break_listing(title: str) -> bool:
    """Check if listing is a break/rip (not a sealed box)."""
    t = title.lower()
    return bool(re.search(r'\b(break|rip|live)\b', t))


def detect_lot_quantity(title: str) -> int:
    """
    Detect if listing is a multi-box lot and return quantity.
    Returns 1 for single box, >1 for lots.

    Patterns: "x2", "x 2", "lot of 2", "2x", "2 x", "qty 2", "quantity 2"
    """
    t = title.lower()

    # Pattern: "x2", "x 2", "x3" etc at end or with space
    match = re.search(r'\bx\s*(\d+)\b', t)
    if match:
        return int(match.group(1))

    # Pattern: "2x", "2 x", "3x" etc
    match = re.search(r'\b(\d+)\s*x\b', t)
    if match:
        return int(match.group(1))

    # Pattern: "lot of 2", "lot of 3"
    match = re.search(r'\blot\s+of\s+(\d+)\b', t)
    if match:
        return int(match.group(1))

    # Pattern: "qty 2", "quantity 2"
    match = re.search(r'\b(?:qty|quantity)\s*(\d+)\b', t)
    if match:
        return int(match.group(1))

    return 1


def filter_listing(item: Dict[str, Any], min_price: float) -> Tuple[bool, int]:
    """
    Filter a single listing.

    Returns:
        tuple: (keep: bool, quantity: int)
        - keep: True if listing should be KEPT
        - quantity: Number of boxes in lot (for price normalization)
    """
    title = item.get("title", "")
    price = item.get("price")

    if not title or price is None:
        return False, 1

    # Title exclusions (general keywords)
    if is_excluded_title(title):
        return False, 1

    # Non-US check
    if is_non_us(title):
        return False, 1

    # Case check (with "case fresh" exception)
    if is_case_listing(title):
        return False, 1

    # Pack check (with "24 packs" exception)
    if is_pack_listing(title):
        return False, 1

    # Break/rip check (backup for URL negatives)
    if is_break_listing(title):
        return False, 1

    # Detect lot quantity for price normalization
    quantity = detect_lot_quantity(title)

    # Price check (dynamic minimum) - check per-unit price for lots
    unit_price = price / quantity if quantity > 1 else price
    if unit_price < min_price:
        return False, 1

    return True, quantity


def _write_ebay_to_db(
    box_id: str,
    today: str,
    ebay_data: Dict[str, Any],
    filtered_items: List[Dict[str, Any]],
) -> bool:
    """Write eBay data to database tables."""
    try:
        from app.services.ebay_metrics_writer import upsert_ebay_daily_metrics, insert_ebay_sales_raw
    except ImportError:
        logger.warning("ebay_metrics_writer not available, skipping DB write")
        return False

    try:
        upsert_ebay_daily_metrics(
            booster_box_id=box_id,
            metric_date=today,
            ebay_sales_count=ebay_data.get("ebay_sold_count", 0),
            ebay_volume_usd=ebay_data.get("ebay_volume_usd", 0),
            ebay_median_sold_price_usd=ebay_data.get("ebay_median_price_usd"),
            ebay_units_sold_count=ebay_data.get("ebay_sold_today", 0),
            ebay_volume_7d_ema=None,  # Computed in Phase 3
            ebay_active_listings_count=None,
            ebay_active_median_price_usd=None,
            ebay_active_low_price_usd=None,
            ebay_listings_added_today=None,
            ebay_listings_removed_today=None,
        )
        logger.debug(f"  DB: upserted ebay_box_metrics_daily for {box_id}")
    except Exception as e:
        logger.warning(f"eBay daily metrics DB write failed for {box_id}: {e}")

    # Convert filtered items to format expected by insert_ebay_sales_raw
    sold_items = []
    for item in filtered_items:
        sold_items.append({
            "ebay_item_id": item.get("item_id"),
            "title": item.get("title", ""),
            "sold_price_usd": item.get("price"),
            "sold_date": item.get("sold_date"),
            "item_url": item.get("url", ""),
            "sale_type": "sold",
        })

    try:
        inserted = insert_ebay_sales_raw(booster_box_id=box_id, sold_items=sold_items)
        logger.debug(f"  DB: inserted {inserted} rows into ebay_sales_raw for {box_id}")
    except Exception as e:
        logger.warning(f"eBay raw sales DB write failed for {box_id}: {e}")

    return True


def run_ebay_apify_scraper(
    debug_box_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Scrape eBay sold listings via Apify for all 18 boxes.

    Args:
        debug_box_id: If set, only scrape this box.

    Returns:
        Summary dict with results count, errors, and date.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Phase 1b: eBay Apify scraper starting for {today}")

    # Initialize Apify client
    api_token = settings.apify_api_token
    if not api_token:
        logger.error("APIFY_API_TOKEN not configured")
        return {"results": 0, "errors": ["APIFY_API_TOKEN not set"], "date": today}

    client = ApifyClient(api_token)

    # Load historical data
    hist = {}
    if HISTORICAL_FILE.exists():
        with open(HISTORICAL_FILE) as f:
            hist = json.load(f)

    # Clear old eBay data (fresh start with Apify)
    for box_id in hist:
        for entry in hist[box_id]:
            # Remove old 130point eBay fields
            ebay_fields = [k for k in entry.keys() if k.startswith("ebay_") or k == "_ebay_sold_item_ids"]
            for field in ebay_fields:
                del entry[field]

    # Determine which boxes to scrape
    if debug_box_id:
        if debug_box_id not in EBAY_BOX_CONFIG:
            logger.error(f"Unknown box_id: {debug_box_id}")
            return {"results": 0, "errors": [f"Unknown box: {debug_box_id}"], "date": today}
        box_items = [(debug_box_id, EBAY_BOX_CONFIG[debug_box_id])]
    else:
        box_items = list(EBAY_BOX_CONFIG.items())

    results_count = 0
    errors = []

    for box_id, config in box_items:
        name = config["name"]
        search = config["search"]
        max_price = config["max_price"]
        tier = config.get("tier", "medium")
        max_results = get_max_results(tier)

        # Get TCG market price for dynamic minimum
        tcg_market_price = None
        box_entries = hist.get(box_id, [])
        for entry in sorted(box_entries, key=lambda e: e.get("date", ""), reverse=True):
            if entry.get("market_price_usd"):
                tcg_market_price = entry["market_price_usd"]
                break
            elif entry.get("floor_price_usd"):
                tcg_market_price = entry["floor_price_usd"]
                break

        # Calculate dynamic minimum price (75% of TCG market)
        if tcg_market_price and tcg_market_price > 0:
            min_price = int(tcg_market_price * MIN_PRICE_RATIO)
        else:
            min_price = 50  # Fallback minimum

        logger.info(f"Scraping {name} [{tier}] (min=${min_price}, max=${max_price}, limit={max_results})")

        try:
            # Build eBay URL with filters
            ebay_url = build_ebay_sold_url(search, min_price, max_price)
            logger.debug(f"  URL: {ebay_url}")

            # Run Apify actor (3x1t PPR - pay per result)
            run_input = {
                "startUrls": [ebay_url],
                "maxItems": max_results,
            }

            run = client.actor(APIFY_ACTOR).call(run_input=run_input)
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

            logger.info(f"  Apify returned {len(items)} items")

            # Filter items
            filtered = []
            for item in items:
                # Normalize item structure
                normalized = {
                    "title": item.get("title", ""),
                    "price": None,
                    "sold_date": None,
                    "item_id": None,
                    "url": item.get("url", ""),
                }

                # Extract price
                price_str = item.get("price", "")
                if isinstance(price_str, (int, float)):
                    normalized["price"] = float(price_str)
                elif isinstance(price_str, str):
                    # Parse price string like "$450.00" or "450.00 USD"
                    match = re.search(r'[\d,]+\.?\d*', price_str.replace(",", ""))
                    if match:
                        normalized["price"] = float(match.group())

                # Extract date
                date_str = item.get("soldDate") or item.get("endDate") or item.get("date")
                normalized["sold_date"] = parse_date(str(date_str)) if date_str else None

                # Extract item ID
                normalized["item_id"] = extract_item_id(item.get("url", "")) or item.get("itemId")

                # Apply filters
                keep, quantity = filter_listing(normalized, min_price)
                if keep:
                    # Normalize price for multi-box lots (divide by quantity)
                    if quantity > 1 and normalized["price"]:
                        original_price = normalized["price"]
                        normalized["price"] = round(original_price / quantity, 2)
                        normalized["lot_quantity"] = quantity
                        normalized["lot_total_price"] = original_price
                        logger.debug(f"    Lot detected: '{normalized['title'][:50]}...' - ${original_price} / {quantity} = ${normalized['price']}")
                    filtered.append(normalized)

            logger.info(f"  Filtered to {len(filtered)} items")

            # Calculate metrics
            if filtered:
                prices = [item["price"] for item in filtered if item["price"]]
                item_ids = [item["item_id"] for item in filtered if item["item_id"]]

                # Get previous day's item IDs for "sold today" calculation
                prev_item_ids = set()
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                for entry in hist.get(box_id, []):
                    if entry.get("date") == yesterday:
                        prev_item_ids = set(entry.get("_ebay_sold_item_ids", []))
                        break

                # New sales = items not in yesterday's list
                new_item_ids = [iid for iid in item_ids if iid not in prev_item_ids]
                new_sales = [item for item in filtered if item["item_id"] in new_item_ids]
                new_prices = [item["price"] for item in new_sales if item["price"]]

                # If no previous tracking, count by date
                if not prev_item_ids:
                    # Count sales from yesterday (most recent complete day)
                    yesterday_sales = [item for item in filtered if item["sold_date"] == yesterday]
                    sold_today = len(yesterday_sales)
                    daily_volume = sum(item["price"] for item in yesterday_sales if item["price"])
                else:
                    sold_today = len(new_sales)
                    daily_volume = sum(new_prices) if new_prices else 0

                ebay_data = {
                    "ebay_sold_count": len(filtered),
                    "ebay_sold_today": sold_today,
                    "ebay_volume_usd": round(sum(prices), 2) if prices else 0,
                    "ebay_daily_volume_usd": round(daily_volume, 2),
                    "ebay_median_price_usd": round(statistics.median(prices), 2) if prices else None,
                    "ebay_avg_price_usd": round(statistics.mean(prices), 2) if prices else None,
                    "ebay_low_price_usd": round(min(prices), 2) if prices else None,
                    "ebay_high_price_usd": round(max(prices), 2) if prices else None,
                    "ebay_source": "apify",
                    "ebay_fetch_timestamp": datetime.now().isoformat(),
                    "_ebay_sold_item_ids": item_ids,
                }
            else:
                ebay_data = {
                    "ebay_sold_count": 0,
                    "ebay_sold_today": 0,
                    "ebay_volume_usd": 0,
                    "ebay_daily_volume_usd": 0,
                    "ebay_median_price_usd": None,
                    "ebay_avg_price_usd": None,
                    "ebay_low_price_usd": None,
                    "ebay_high_price_usd": None,
                    "ebay_source": "apify",
                    "ebay_fetch_timestamp": datetime.now().isoformat(),
                    "_ebay_sold_item_ids": [],
                }
                filtered = []  # Empty list for DB write

            # Update historical entry
            if box_id not in hist:
                hist[box_id] = []

            today_entry = next((e for e in hist[box_id] if e.get("date") == today), None)
            if today_entry:
                today_entry.update(ebay_data)
            else:
                hist[box_id].append({"date": today, **ebay_data})

            # Write to database
            _write_ebay_to_db(box_id, today, ebay_data, filtered)

            logger.info(f"  ✅ {name}: {ebay_data['ebay_sold_count']} sold, {ebay_data['ebay_sold_today']} today, median=${ebay_data['ebay_median_price_usd']}")
            results_count += 1

        except Exception as e:
            logger.error(f"  ❌ {name}: {e}")
            errors.append(f"{name}: {e}")

    # Save historical data
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(hist, f, indent=2)

    logger.info(f"Phase 1b complete: {results_count}/{len(box_items)} boxes, {len(errors)} errors")

    return {
        "results": results_count,
        "errors": errors,
        "date": today,
    }


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="eBay Apify Scraper")
    parser.add_argument("--debug", type=str, help="Only scrape this box_id")
    args = parser.parse_args()

    result = run_ebay_apify_scraper(debug_box_id=args.debug)
    print(json.dumps(result, indent=2))
