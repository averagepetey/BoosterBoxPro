#!/usr/bin/env python3
"""
eBay Apify Scraper
------------------
Fetches eBay sold listings via Apify actor (caffein.dev/ebay-sold-listings).
Replaces custom Playwright scraper with reliable Apify-managed scraping.

Cost: $2 per 1,000 results (~$1.66/day = ~$50/month for all 18 boxes)
Note: Exceeds $29 starter plan - consider reducing tiers or upgrading plan
Tiered limits: hot=85, medium=50, slow=15 results per box

Run standalone: python scripts/ebay_apify.py [--debug <box_id>]
Called by daily_refresh.py as Phase 1b (after TCGplayer Apify).
"""

import json
import logging
import random
import re
import statistics
import time
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
PASS_RATE_FILE = project_root / "data" / "ebay_pass_rates.json"

# Price floor as fraction of TCG market price (65% = reject below 35% discount)
MIN_PRICE_RATIO = 0.65

# Tiered result limits by box activity level (fallback when no pass rate data)
# Hot: 5 boxes × 85 = 425/day, Medium: 6 × 50 = 300/day, Slow: 7 × 15 = 105/day
# Total: 830/day × 30 = 24,900/month × $2/1000 = ~$50/month
RESULTS_LIMIT_HOT = 85
RESULTS_LIMIT_MEDIUM = 50
RESULTS_LIMIT_SLOW = 15

# Dynamic allocation settings (used when pass rate data available)
DAILY_RESULTS_BUDGET = 830  # Total results/day across all boxes
MIN_RESULTS_PER_BOX = 10    # Minimum to catch rare sales
MAX_RESULTS_PER_BOX = 120   # Maximum per box (diminishing returns)
MIN_DAYS_FOR_DYNAMIC = 3    # Days of data needed before using dynamic allocation

# Apify actor to use ($2 per 1,000 results - pay-per-result, no rental)
APIFY_ACTOR = "caffein.dev/ebay-sold-listings"

# Retry settings (74% success rate → 99.5% with 3 retries)
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [10, 30, 60]  # Exponential backoff for rate limits

# Delay between boxes to avoid rate limiting (randomized)
MIN_DELAY_BETWEEN_BOXES = 3  # seconds
MAX_DELAY_BETWEEN_BOXES = 8  # seconds

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
# eBay search configuration for each box
# "searches" is a list of 2 queries - results are deduped by item URL
# Search 1: No-hyphen set code (matches both OP13 and OP-13)
# Search 2: Set name without code (catches listings where code is at end or missing)
EBAY_BOX_CONFIG: Dict[str, Dict[str, Any]] = {
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {
        "name": "OP-01 Romance Dawn (Blue)",
        "searches": ["OP01 romance dawn booster box blue", "romance dawn booster box blue english"],
        "max_price": 500,
        "tier": "slow",
    },
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": {
        "name": "OP-01 Romance Dawn (White)",
        "searches": ["OP01 romance dawn booster box white", "romance dawn booster box white english"],
        "max_price": 400,
        "tier": "slow",
    },
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": {
        "name": "OP-02 Paramount War",
        "searches": ["OP02 paramount war booster box", "paramount war booster box english"],
        "max_price": 400,
        "tier": "slow",
    },
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": {
        "name": "OP-03 Pillars of Strength",
        "searches": ["OP03 pillars strength booster box", "pillars of strength booster box english"],
        "max_price": 400,
        "tier": "slow",
    },
    "526c28b7-bc13-449b-a521-e63bdd81811a": {
        "name": "OP-04 Kingdoms of Intrigue",
        "searches": ["OP04 kingdoms intrigue booster box", "kingdoms intrigue booster box english"],
        "max_price": 350,
        "tier": "slow",
    },
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": {
        "name": "OP-05 Awakening of the New Era",
        "searches": ["OP05 awakening new era booster box", "awakening new era booster box english"],
        "max_price": 500,
        "tier": "medium",
    },
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": {
        "name": "OP-06 Wings of the Captain",
        "searches": ["OP06 wings captain booster box", "wings of the captain booster box english"],
        "max_price": 350,
        "tier": "medium",
    },
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": {
        "name": "OP-07 500 Years in the Future",
        "searches": ["OP07 500 years future booster box", "500 years in the future booster box english"],
        "max_price": 350,
        "tier": "medium",
    },
    "d0faf871-a930-4c80-a981-9df8741c90a9": {
        "name": "OP-08 Two Legends",
        "searches": ["OP08 two legends booster box", "two legends booster box english"],
        "max_price": 600,
        "tier": "medium",
    },
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": {
        "name": "OP-09 Emperors in the New World",
        "searches": ["OP09 emperors new world booster box", "emperors new world booster box english"],
        "max_price": 800,
        "tier": "hot",
    },
    "3429708c-43c3-4ed8-8be3-706db8b062bd": {
        "name": "OP-10 Royal Blood",
        "searches": ["OP10 royal blood booster box", "royal blood booster box english"],
        "max_price": 600,
        "tier": "hot",
    },
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": {
        "name": "OP-11 A Fist of Divine Speed",
        "searches": ["OP11 fist divine speed booster box", "fist of divine speed booster box english"],
        "max_price": 700,
        "tier": "hot",
    },
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": {
        "name": "OP-12 Legacy of the Master",
        "searches": ["OP12 legacy master booster box", "legacy of the master booster box english"],
        "max_price": 600,
        "tier": "hot",
    },
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {
        "name": "OP-13 Carrying on His Will",
        "searches": ["OP13 carrying his will booster box", "carrying on his will booster box english"],
        "max_price": 2500,
        "tier": "hot",
    },
    "3b17b708-b35b-4008-971e-240ade7afc9c": {
        "name": "EB-01 Memorial Collection",
        "searches": ["EB01 memorial collection booster box", "memorial collection booster box english"],
        "max_price": 800,
        "tier": "medium",
    },
    "7509a855-f6da-445e-b445-130824d81d04": {
        "name": "EB-02 Anime 25th Collection",
        "searches": ["EB02 anime 25th booster box", "anime 25th collection booster box english"],
        "max_price": 600,
        "tier": "medium",
    },
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": {
        "name": "PRB-01 Premium Booster",
        "searches": ["PRB01 premium booster box", "one piece premium booster box"],
        "max_price": 800,
        "tier": "slow",
    },
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": {
        "name": "PRB-02 Premium Booster Vol. 2",
        "searches": ["PRB02 premium booster box", "one piece premium booster vol 2 box"],
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
    """Get max results limit based on box tier (fallback when no pass rate data)."""
    if tier == "hot":
        return RESULTS_LIMIT_HOT
    elif tier == "medium":
        return RESULTS_LIMIT_MEDIUM
    else:
        return RESULTS_LIMIT_SLOW


def calculate_dynamic_allocation(pass_rates: Dict[str, Any], box_configs: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate optimal results allocation based on historical pass rates.

    Boxes with higher pass rates (more daily sales) get more results allocated.
    This minimizes waste by not over-fetching for low-volume boxes.

    Args:
        pass_rates: Historical pass rate data from ebay_pass_rates.json
        box_configs: EBAY_BOX_CONFIG with tier info

    Returns:
        Dict mapping box_id to allocated results count
    """
    # Collect pass rates from last N days
    all_dates = sorted(pass_rates.keys(), reverse=True)[:MIN_DAYS_FOR_DYNAMIC * 2]  # Look at recent dates

    if len(all_dates) < MIN_DAYS_FOR_DYNAMIC:
        logger.info(f"  Only {len(all_dates)} days of pass rate data, need {MIN_DAYS_FOR_DYNAMIC}. Using tier-based allocation.")
        return {}  # Not enough data, use tier-based fallback

    # Calculate average pass rate per box
    box_avg_pass_rates: Dict[str, float] = {}
    box_avg_passed: Dict[str, float] = {}

    for box_id in box_configs.keys():
        rates = []
        passed_counts = []
        for date in all_dates:
            if date in pass_rates and box_id in pass_rates[date]:
                box_data = pass_rates[date][box_id]
                rates.append(box_data.get("pass_rate", 0))
                passed_counts.append(box_data.get("passed", 0))

        if rates:
            box_avg_pass_rates[box_id] = sum(rates) / len(rates)
            box_avg_passed[box_id] = sum(passed_counts) / len(passed_counts)
        else:
            # No data for this box, use tier-based estimate
            tier = box_configs[box_id].get("tier", "medium")
            box_avg_pass_rates[box_id] = 0.05 if tier == "hot" else 0.03 if tier == "medium" else 0.01
            box_avg_passed[box_id] = 2 if tier == "hot" else 1 if tier == "medium" else 0.5

    # Calculate allocation based on expected daily sales (passed count)
    # Boxes that find more sales get proportionally more budget
    total_expected = sum(box_avg_passed.values()) or 1

    allocation: Dict[str, int] = {}
    remaining_budget = DAILY_RESULTS_BUDGET

    # First pass: allocate proportionally
    for box_id, avg_passed in box_avg_passed.items():
        # Base allocation proportional to historical sales found
        proportion = avg_passed / total_expected
        base_alloc = int(DAILY_RESULTS_BUDGET * proportion)

        # Also factor in pass rate - low pass rate means we need more results to find sales
        pass_rate = box_avg_pass_rates[box_id]
        if pass_rate > 0:
            # If pass rate is 5%, we need ~20 results per expected sale
            # If pass rate is 10%, we need ~10 results per expected sale
            efficiency_factor = min(2.0, 0.05 / pass_rate) if pass_rate < 0.05 else 1.0
            adjusted_alloc = int(base_alloc * efficiency_factor)
        else:
            adjusted_alloc = base_alloc

        # Clamp to min/max
        allocation[box_id] = max(MIN_RESULTS_PER_BOX, min(MAX_RESULTS_PER_BOX, adjusted_alloc))

    # Normalize to fit budget
    total_allocated = sum(allocation.values())
    if total_allocated > DAILY_RESULTS_BUDGET:
        scale = DAILY_RESULTS_BUDGET / total_allocated
        for box_id in allocation:
            allocation[box_id] = max(MIN_RESULTS_PER_BOX, int(allocation[box_id] * scale))

    # Log allocation summary
    total_final = sum(allocation.values())
    logger.info(f"  Dynamic allocation: {total_final} results across {len(allocation)} boxes")

    # Show top allocations
    sorted_alloc = sorted(allocation.items(), key=lambda x: x[1], reverse=True)
    for box_id, count in sorted_alloc[:3]:
        name = box_configs[box_id]["name"]
        pass_rate = box_avg_pass_rates.get(box_id, 0) * 100
        logger.info(f"    {name}: {count} results (avg pass rate: {pass_rate:.1f}%)")

    return allocation


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

    # Try common date formats including ISO timestamps
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%fZ",  # "2026-02-03T00:00:00.000Z" (ISO with ms)
        "%Y-%m-%dT%H:%M:%SZ",      # "2026-02-03T00:00:00Z" (ISO)
        "%Y-%m-%dT%H:%M:%S",       # "2026-02-03T00:00:00" (ISO no Z)
        "%Y-%m-%d",                # "2026-01-15"
        "%b %d, %Y",               # "Jan 15, 2026"
        "%B %d, %Y",               # "January 15, 2026"
        "%m/%d/%Y",                # "01/15/2026"
        "%d %b %Y",                # "15 Jan 2026"
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


def parse_ended_at(date_str: str) -> Optional[datetime]:
    """
    Parse caffein.dev endedAt timestamp to datetime object.

    Handles formats like:
    - "2026-02-04T15:30:00.000Z" (ISO format)
    - "2026-02-04T15:30:00Z"
    - "Feb 4, 2026" (fallback to date-only)
    """
    if not date_str:
        return None

    # Try ISO format with milliseconds
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%fZ",  # "2026-02-04T15:30:00.000Z"
        "%Y-%m-%dT%H:%M:%SZ",      # "2026-02-04T15:30:00Z"
        "%Y-%m-%dT%H:%M:%S",       # "2026-02-04T15:30:00"
        "%Y-%m-%d",                # "2026-02-04"
    ):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    # Fallback: try parse_date and convert to datetime at midnight
    date_only = parse_date(date_str)
    if date_only:
        return datetime.strptime(date_only, "%Y-%m-%d")

    return None


def filter_to_yesterday(
    items: List[Dict[str, Any]],
    target_date: str
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Filter items to only those with endedAt matching the target date.

    Designed for midnight scraping: run at 12:05am, count yesterday's sales.
    The caffein.dev API returns dates as midnight timestamps (e.g., 2026-02-03T00:00:00.000Z),
    so we compare by date string only.

    Args:
        items: List of normalized items with 'sold_date' field (YYYY-MM-DD)
        target_date: The date to match (usually yesterday), format YYYY-MM-DD

    Returns:
        tuple: (filtered_items, rejected_count)
    """
    filtered = []
    rejected = 0

    for item in items:
        sold_date = item.get("sold_date")
        if sold_date == target_date:
            filtered.append(item)
        else:
            rejected += 1

    return filtered, rejected


def load_pass_rates() -> Dict[str, Any]:
    """Load pass rate history from JSON file."""
    if PASS_RATE_FILE.exists():
        with open(PASS_RATE_FILE) as f:
            return json.load(f)
    return {}


def save_pass_rates(data: Dict[str, Any]) -> None:
    """Save pass rate history to JSON file."""
    with open(PASS_RATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_pass_rate(
    pass_rates: Dict[str, Any],
    date: str,
    box_id: str,
    fetched: int,
    passed: int
) -> None:
    """Record pass rate for a box on a given date."""
    if date not in pass_rates:
        pass_rates[date] = {}

    pass_rates[date][box_id] = {
        "fetched": fetched,
        "passed": passed,
        "pass_rate": round(passed / fetched, 3) if fetched > 0 else 0
    }


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
    reference_time = datetime.now()
    today = reference_time.strftime("%Y-%m-%d")
    yesterday = (reference_time - timedelta(days=1)).strftime("%Y-%m-%d")
    logger.info(f"Phase 1b: eBay Apify scraper starting for {today}")
    logger.info(f"  Counting sales from: {yesterday} (yesterday)")

    # Initialize Apify client
    api_token = settings.apify_api_token
    if not api_token:
        logger.error("APIFY_API_TOKEN not configured")
        return {"results": 0, "errors": ["APIFY_API_TOKEN not set"], "date": today}

    client = ApifyClient(api_token)

    # Load pass rate history for tracking
    pass_rates = load_pass_rates()
    total_fetched = 0  # Track total API results for cost logging

    # Calculate dynamic allocation based on historical pass rates
    dynamic_allocation = calculate_dynamic_allocation(pass_rates, EBAY_BOX_CONFIG)
    if dynamic_allocation:
        logger.info("  Using dynamic allocation based on pass rate history")
    else:
        logger.info("  Using tier-based allocation (insufficient pass rate data)")

    # Load TCG floor prices from DB (Phase 1 Apify writes these before us)
    _apify_tcg_floors = {}
    try:
        from app.services.db_historical_reader import _get_sync_engine
        from sqlalchemy import text as _text
        _engine = _get_sync_engine()
        with _engine.connect() as conn:
            rows = conn.execute(_text("""
                SELECT DISTINCT ON (booster_box_id) booster_box_id, floor_price_usd
                FROM box_metrics_unified
                WHERE floor_price_usd IS NOT NULL
                ORDER BY booster_box_id, metric_date DESC
            """)).fetchall()
        for r in rows:
            d = r._mapping if hasattr(r, "_mapping") else dict(r)
            bid = str(d["booster_box_id"])
            fp = d.get("floor_price_usd")
            if fp is not None:
                _apify_tcg_floors[bid] = float(fp)
        logger.info(f"Loaded {len(_apify_tcg_floors)} TCG floor prices from DB")
    except Exception as e:
        logger.warning(f"Could not load TCG floors from DB: {e}")

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
        # Support both old "search" (string) and new "searches" (list) format
        searches = config.get("searches") or [config.get("search", "")]
        max_price = config["max_price"]
        tier = config.get("tier", "medium")

        # Use dynamic allocation if available, otherwise fall back to tier-based
        if dynamic_allocation and box_id in dynamic_allocation:
            max_results = dynamic_allocation[box_id]
            allocation_type = "dynamic"
        else:
            max_results = get_max_results(tier)
            allocation_type = "tier"

        # Get TCG market price from DB for dynamic minimum
        tcg_market_price = _apify_tcg_floors.get(box_id)

        # Calculate dynamic minimum price (65% of TCG market)
        if tcg_market_price and tcg_market_price > 0:
            min_price = int(tcg_market_price * MIN_PRICE_RATIO)
        else:
            min_price = 50  # Fallback minimum

        logger.info(f"Scraping {name} [{tier}/{allocation_type}] (min=${min_price}, max=${max_price}, limit={max_results})")

        try:
            # Run multiple searches and dedupe by item URL
            all_items_by_url: Dict[str, Dict] = {}
            results_per_search = max(10, max_results // len(searches))  # Split limit between searches

            for search_idx, search in enumerate(searches):
                logger.debug(f"  Search {search_idx + 1}/{len(searches)}: {search}")

                run_input = {
                    "keyword": search,
                    "count": results_per_search,
                    "minPrice": min_price,
                    "maxPrice": max_price,
                }

                search_items = None
                last_error = None
                for attempt in range(MAX_RETRIES + 1):
                    try:
                        run = client.actor(APIFY_ACTOR).call(run_input=run_input)
                        search_items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
                        break  # Success, exit retry loop
                    except Exception as retry_err:
                        last_error = retry_err
                        err_str = str(retry_err).lower()

                        # Classify error for smarter retry
                        is_rate_limit = "429" in err_str or "rate limit" in err_str
                        is_blocked = "403" in err_str or "forbidden" in err_str
                        is_timeout = "timeout" in err_str

                        if attempt < MAX_RETRIES:
                            base_wait = RETRY_BACKOFF_SECONDS[attempt]
                            if is_rate_limit or is_blocked:
                                wait_time = base_wait * 2
                            else:
                                wait_time = base_wait

                            error_type = "RATE_LIMIT" if is_rate_limit else "BLOCKED" if is_blocked else "TIMEOUT" if is_timeout else "ERROR"
                            logger.warning(f"  ⚠️ Attempt {attempt + 1} [{error_type}]: {retry_err}. Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            logger.error(f"  ❌ All {MAX_RETRIES + 1} attempts failed for {name} search {search_idx + 1}")
                            raise last_error

                if search_items:
                    # Dedupe by URL (unique per listing)
                    for item in search_items:
                        url = item.get("url", "")
                        if url and url not in all_items_by_url:
                            all_items_by_url[url] = item

                # Small delay between searches to avoid rate limits
                if search_idx < len(searches) - 1:
                    time.sleep(random.uniform(1, 3))

            items = list(all_items_by_url.values())
            if not items:
                raise last_error or Exception("No items returned from any search")

            logger.info(f"  Apify returned {len(items)} unique items from {len(searches)} searches")

            # Filter items
            filtered = []
            rejected_count = 0
            for item in items:
                # Normalize item structure
                normalized = {
                    "title": item.get("title", ""),
                    "price": None,
                    "sold_date": None,
                    "item_id": None,
                    "url": item.get("url", ""),
                }

                # Extract price (caffein.dev uses soldPrice, others use price)
                price_str = item.get("soldPrice") or item.get("price", "")
                if isinstance(price_str, (int, float)):
                    normalized["price"] = float(price_str)
                elif isinstance(price_str, str):
                    # Parse price string like "$450.00" or "450.00 USD"
                    match = re.search(r'[\d,]+\.?\d*', price_str.replace(",", ""))
                    if match:
                        normalized["price"] = float(match.group())

                # Extract date (caffein.dev uses endedAt, others use soldDate/endDate)
                date_str = item.get("endedAt") or item.get("soldDate") or item.get("endDate") or item.get("date")
                normalized["sold_date"] = parse_date(str(date_str)) if date_str else None
                # Also store as datetime for 24-hour filtering
                normalized["ended_at_dt"] = parse_ended_at(str(date_str)) if date_str else None

                # Extract item ID (caffein.dev uses itemId, fallback to URL extraction)
                normalized["item_id"] = item.get("itemId") or extract_item_id(item.get("url", ""))

                # Skip items without price
                if normalized["price"] is None:
                    rejected_count += 1
                    continue

                # Apply filters
                keep, quantity = filter_listing(normalized, min_price)
                if not keep:
                    rejected_count += 1
                    continue

                # Normalize price for multi-box lots (divide by quantity)
                if quantity > 1 and normalized["price"]:
                    original_price = normalized["price"]
                    normalized["price"] = round(original_price / quantity, 2)
                    normalized["lot_quantity"] = quantity
                    normalized["lot_total_price"] = original_price
                    logger.debug(f"    Lot detected: '{normalized['title'][:50]}...' - ${original_price} / {quantity} = ${normalized['price']}")
                filtered.append(normalized)

            logger.info(f"  Quality filtered to {len(filtered)} items ({rejected_count} rejected)")

            # Track total fetched for cost logging
            total_fetched += len(items)

            # Apply date filter - only count sales from yesterday
            items_yesterday, rejected_date = filter_to_yesterday(filtered, yesterday)
            pass_rate = len(items_yesterday) / len(items) if items else 0

            logger.info(f"  Date filter: {len(items_yesterday)} from {yesterday}, {rejected_date} other dates (pass rate: {pass_rate:.1%})")

            # Log pass rate for future optimization
            log_pass_rate(pass_rates, today, box_id, len(items), len(items_yesterday))

            # Calculate metrics from yesterday's sales only
            if items_yesterday:
                prices_yesterday = [item["price"] for item in items_yesterday if item["price"]]

                ebay_data = {
                    "ebay_sold_count": len(items_yesterday),  # Sales on target date
                    "ebay_sold_today": len(items_yesterday),  # Same - this IS the daily count
                    "ebay_volume_usd": round(sum(prices_yesterday), 2) if prices_yesterday else 0,
                    "ebay_daily_volume_usd": round(sum(prices_yesterday), 2) if prices_yesterday else 0,
                    "ebay_median_price_usd": round(statistics.median(prices_yesterday), 2) if prices_yesterday else None,
                    "ebay_avg_price_usd": round(statistics.mean(prices_yesterday), 2) if prices_yesterday else None,
                    "ebay_low_price_usd": round(min(prices_yesterday), 2) if prices_yesterday else None,
                    "ebay_high_price_usd": round(max(prices_yesterday), 2) if prices_yesterday else None,
                    "ebay_source": "apify_caffein",
                    "ebay_fetch_timestamp": reference_time.isoformat(),
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
                    "ebay_source": "apify_caffein",
                    "ebay_fetch_timestamp": reference_time.isoformat(),
                }
                items_yesterday = []  # Empty list for DB write

            # Write to database for yesterday's date
            _write_ebay_to_db(box_id, yesterday, ebay_data, items_yesterday)

            logger.info(f"  ✅ {name}: {ebay_data['ebay_sold_count']} sold on {yesterday}, median=${ebay_data['ebay_median_price_usd']}")
            results_count += 1

        except Exception as e:
            # Classify error for better debugging
            err_str = str(e).lower()
            if "429" in err_str or "rate limit" in err_str:
                error_type = "RATE_LIMIT"
            elif "403" in err_str or "forbidden" in err_str or "blocked" in err_str:
                error_type = "BLOCKED"
            elif "timeout" in err_str or "timed out" in err_str:
                error_type = "TIMEOUT"
            elif "captcha" in err_str:
                error_type = "CAPTCHA"
            else:
                error_type = "UNKNOWN"

            logger.error(f"  ❌ {name} [{error_type}]: {e}")
            errors.append(f"{name} [{error_type}]: {e}")

        # Delay between boxes to avoid rate limiting (skip delay for last box or debug mode)
        if len(box_items) > 1 and box_id != box_items[-1][0]:
            delay = random.uniform(MIN_DELAY_BETWEEN_BOXES, MAX_DELAY_BETWEEN_BOXES)
            logger.debug(f"  Waiting {delay:.1f}s before next box...")
            time.sleep(delay)

    # DB is source of truth — skip JSON write (file may not exist in CI)

    # Save pass rates for future optimization
    save_pass_rates(pass_rates)

    # Log cost summary
    est_cost = total_fetched * 0.002  # $2 per 1000 results
    monthly_projection = est_cost * 30
    logger.info(f"Phase 1b complete: {results_count}/{len(box_items)} boxes, {len(errors)} errors")
    logger.info(f"  💰 Cost: {total_fetched} results fetched, est. ${est_cost:.2f} today, ~${monthly_projection:.2f}/month projected")

    return {
        "results": results_count,
        "errors": errors,
        "date": today,
        "total_fetched": total_fetched,
        "est_cost_usd": round(est_cost, 2),
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
