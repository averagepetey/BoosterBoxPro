#!/usr/bin/env python3
"""
eBay SerpApi Scraper
--------------------
Fetches eBay sold + active listings via SerpApi's eBay engine.
Replaces both Phase 1b (Apify caffein.dev sold) and Phase 1b-B (130point active).

Cost: $25/month SerpApi Starter plan (1,000 searches/month)
  - 18 boxes × active daily = 540/month
  - 14 high-volume × sold daily = 420/month
  - 4 low-volume × sold every 3rd day = 40/month
  - Total: ~1,000/month

Run standalone: python scripts/ebay_serpapi.py [--debug <box_id>]
Called by daily_refresh.py as Phase 1b-SerpApi.
"""

import json
import logging
import re
import statistics
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import settings
from scripts.ebay_apify import (
    TITLE_EXCLUSIONS,
    NON_US_KEYWORDS,
    detect_lot_quantity,
    is_excluded_title,
    is_non_us,
    is_case_listing,
    is_pack_listing,
    is_break_listing,
    extract_item_id,
    parse_date,
)

logger = logging.getLogger(__name__)

# Price floor ratios (fraction of TCG floor price)
ACTIVE_MIN_PRICE_RATIO = 0.79  # Active listings: reject below 21% discount
SOLD_MIN_PRICE_RATIO = 0.65    # Sold listings: reject below 35% discount

# SerpApi endpoint
SERPAPI_URL = "https://serpapi.com/search.json"

# Low-volume boxes: sold scraped every 3rd day (day_of_year % 3 == 0)
LOW_VOLUME_BOX_IDS = {
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4",  # OP-01 Blue
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a",  # OP-03
    "526c28b7-bc13-449b-a521-e63bdd81811a",  # OP-04
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62",  # PRB-02
}

# eBay search config for each box (18 boxes)
# search_query: primary eBay search terms
# min_price / max_price: USD price range for SerpApi URL params
SERPAPI_BOX_CONFIG: Dict[str, Dict[str, Any]] = {
    "860ffe3f-9286-42a9-ad4e-d079a6add6f4": {
        "name": "OP-01 Romance Dawn (Blue)",
        "search_query": "OP01 romance dawn booster box blue english",
        "min_price": 20,
        "max_price": 500,
    },
    "18ade4d4-512b-4261-a119-2b6cfaf1fa2a": {
        "name": "OP-01 Romance Dawn (White)",
        "search_query": "OP01 romance dawn booster box white english",
        "min_price": 15,
        "max_price": 400,
    },
    "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320": {
        "name": "OP-02 Paramount War",
        "search_query": "OP02 paramount war booster box english",
        "min_price": 15,
        "max_price": 400,
    },
    "d3929fc6-6afa-468a-b7a1-ccc0f392131a": {
        "name": "OP-03 Pillars of Strength",
        "search_query": "OP03 pillars strength booster box english",
        "min_price": 15,
        "max_price": 400,
    },
    "526c28b7-bc13-449b-a521-e63bdd81811a": {
        "name": "OP-04 Kingdoms of Intrigue",
        "search_query": "OP04 kingdoms intrigue booster box english",
        "min_price": 15,
        "max_price": 350,
    },
    "6ea1659d-7b86-46c5-8fb2-0596262b8e68": {
        "name": "OP-05 Awakening of the New Era",
        "search_query": "OP05 awakening new era booster box english",
        "min_price": 20,
        "max_price": 500,
    },
    "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa": {
        "name": "OP-06 Wings of the Captain",
        "search_query": "OP06 wings captain booster box english",
        "min_price": 15,
        "max_price": 350,
    },
    "9bfebc47-4a92-44b3-b157-8c53d6a6a064": {
        "name": "OP-07 500 Years in the Future",
        "search_query": "OP07 500 years future booster box english",
        "min_price": 15,
        "max_price": 350,
    },
    "d0faf871-a930-4c80-a981-9df8741c90a9": {
        "name": "OP-08 Two Legends",
        "search_query": "OP08 two legends booster box english",
        "min_price": 30,
        "max_price": 600,
    },
    "c035aa8b-6bec-4237-aff5-1fab1c0f53ce": {
        "name": "OP-09 Emperors in the New World",
        "search_query": "OP09 emperors new world booster box english",
        "min_price": 30,
        "max_price": 600,
    },
    "3429708c-43c3-4ed8-8be3-706db8b062bd": {
        "name": "OP-10 Royal Blood",
        "search_query": "OP10 royal blood booster box english",
        "min_price": 30,
        "max_price": 600,
    },
    "46039dfc-a980-4bbd-aada-8cc1e124b44b": {
        "name": "OP-11 A Fist of Divine Speed",
        "search_query": "OP11 fist divine speed booster box english",
        "min_price": 40,
        "max_price": 700,
    },
    "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc": {
        "name": "OP-12 Legacy of the Master",
        "search_query": "OP12 legacy master booster box english",
        "min_price": 30,
        "max_price": 600,
    },
    "2d7d2b54-596d-4c80-a02f-e2eeefb45a34": {
        "name": "OP-13 Carrying on His Will",
        "search_query": "OP13 carrying his will booster box english",
        "min_price": 200,
        "max_price": 2500,
    },
    "3b17b708-b35b-4008-971e-240ade7afc9c": {
        "name": "EB-01 Memorial Collection",
        "search_query": "EB01 memorial collection booster box english",
        "min_price": 40,
        "max_price": 800,
    },
    "7509a855-f6da-445e-b445-130824d81d04": {
        "name": "EB-02 Anime 25th Collection",
        "search_query": "EB02 anime 25th booster box english",
        "min_price": 30,
        "max_price": 600,
    },
    "743bf253-98ca-49d5-93fe-a3eaef9f72c1": {
        "name": "PRB-01 Premium Booster",
        "search_query": "PRB01 premium booster box one piece",
        "min_price": 40,
        "max_price": 800,
    },
    "3bda2acb-a55c-4a6e-ae93-dff5bad27e62": {
        "name": "PRB-02 Premium Booster Vol. 2",
        "search_query": "PRB02 premium booster vol 2 box one piece",
        "min_price": 40,
        "max_price": 600,
    },
}

# Track total searches for budget logging
_searches_used = 0


def serpapi_search(
    query: str,
    search_type: str,
    min_price: int,
    max_price: int,
    api_key: str,
) -> List[Dict[str, Any]]:
    """
    Execute a SerpApi eBay search.

    Args:
        query: eBay search terms
        search_type: "active" or "sold"
        min_price: Minimum price in USD
        max_price: Maximum price in USD
        api_key: SerpApi API key

    Returns:
        List of organic_results from SerpApi response
    """
    global _searches_used

    params: Dict[str, Any] = {
        "engine": "ebay",
        "api_key": api_key,
        "_nkw": query,
        "LH_ItemCondition": "1000",    # New condition
        "LH_PrefLoc": "1",             # US sellers only (1=Domestic)
        "_udlo": str(min_price),
        "_udhi": str(max_price),
        "_ipg": "200",                 # 200 results per page
    }

    if search_type == "sold":
        params["show_only"] = "Sold"
        params["_sop"] = "10"  # Time: newly listed (most recent sales first)

    try:
        resp = httpx.get(SERPAPI_URL, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        _searches_used += 1

        results = data.get("organic_results", [])
        logger.debug(f"  SerpApi returned {len(results)} results for '{query}' ({search_type})")
        return results

    except httpx.HTTPStatusError as e:
        logger.error(f"  SerpApi HTTP error: {e.response.status_code} - {e.response.text[:200]}")
        raise
    except Exception as e:
        logger.error(f"  SerpApi request failed: {e}")
        raise


def filter_serpapi_results(
    results: List[Dict[str, Any]],
    search_type: str,
    tcg_floor_price: Optional[float],
    min_price: int,
    max_price: int,
) -> List[Dict[str, Any]]:
    """
    Filter SerpApi eBay results using existing quality checks.

    Returns list of normalized dicts with:
    - title, price, ebay_item_id, item_url, sold_date (sold only), condition, seller
    """
    price_ratio = ACTIVE_MIN_PRICE_RATIO if search_type == "active" else SOLD_MIN_PRICE_RATIO

    # Dynamic price floor based on TCG market price
    if tcg_floor_price and tcg_floor_price > 0:
        dynamic_min = tcg_floor_price * price_ratio
    else:
        dynamic_min = float(min_price)

    seen_ids: set = set()
    filtered: List[Dict[str, Any]] = []
    rejected = 0

    for item in results:
        title = item.get("title", "")
        if not title:
            rejected += 1
            continue

        # Extract price
        price_info = item.get("price", {})
        if isinstance(price_info, dict):
            price = price_info.get("extracted")
            if price is None:
                price = price_info.get("raw")
                if isinstance(price, str):
                    match = re.search(r'[\d,]+\.?\d*', price.replace(",", ""))
                    price = float(match.group()) if match else None
        elif isinstance(price_info, (int, float)):
            price = float(price_info)
        elif isinstance(price_info, str):
            match = re.search(r'[\d,]+\.?\d*', price_info.replace(",", ""))
            price = float(match.group()) if match else None
        else:
            price = None

        if price is None:
            rejected += 1
            continue

        # Title exclusions
        if is_excluded_title(title):
            rejected += 1
            continue

        # Non-US check
        if is_non_us(title):
            rejected += 1
            continue

        # Case check
        if is_case_listing(title):
            rejected += 1
            continue

        # Pack check
        if is_pack_listing(title):
            rejected += 1
            continue

        # Break/rip check
        if is_break_listing(title):
            rejected += 1
            continue

        # Lot quantity detection and price normalization
        quantity = detect_lot_quantity(title)
        unit_price = price / quantity if quantity > 1 else price

        # Price floor check
        if unit_price < dynamic_min:
            rejected += 1
            continue

        # Dedup by eBay item ID
        # product_id = unique listing ID; epid = shared catalog ID (not unique)
        link = item.get("link", "")
        ebay_item_id = item.get("product_id") or extract_item_id(link)
        if ebay_item_id:
            if ebay_item_id in seen_ids:
                rejected += 1
                continue
            seen_ids.add(ebay_item_id)

        # Build normalized result
        normalized: Dict[str, Any] = {
            "title": title,
            "price": round(unit_price, 2),
            "ebay_item_id": str(ebay_item_id) if ebay_item_id else None,
            "item_url": link,
            "condition": item.get("condition", ""),
            "seller": item.get("seller", {}).get("username", "") if isinstance(item.get("seller"), dict) else "",
        }

        if quantity > 1:
            normalized["lot_quantity"] = quantity
            normalized["lot_total_price"] = round(price, 2)

        # Sold date (sold items only)
        if search_type == "sold":
            sold_date_str = item.get("sold_date") or item.get("date")
            if sold_date_str:
                normalized["sold_date"] = parse_date(str(sold_date_str))
            else:
                normalized["sold_date"] = None

        filtered.append(normalized)

    logger.info(f"  Filtered to {len(filtered)} items ({rejected} rejected)")
    return filtered


def should_scrape_sold_today(box_id: str) -> bool:
    """Check if sold listings should be scraped today for this box."""
    if box_id not in LOW_VOLUME_BOX_IDS:
        return True  # High-volume: always scrape
    day_of_year = datetime.now().timetuple().tm_yday
    return day_of_year % 3 == 0


def load_tcg_floor_prices() -> Dict[str, float]:
    """Load TCG floor prices from DB (Phase 1 writes these before us)."""
    floors: Dict[str, float] = {}
    try:
        from app.services.db_historical_reader import _get_sync_engine
        from sqlalchemy import text as sql_text

        engine = _get_sync_engine()
        with engine.connect() as conn:
            rows = conn.execute(sql_text("""
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
                floors[bid] = float(fp)
        logger.info(f"Loaded {len(floors)} TCG floor prices from DB")
    except Exception as e:
        logger.warning(f"Could not load TCG floors from DB: {e}")
    return floors


def load_yesterday_ebay_active() -> Dict[str, Optional[int]]:
    """Load yesterday's eBay active listing counts from DB for delta calculation."""
    counts: Dict[str, Optional[int]] = {}
    try:
        from app.services.db_historical_reader import _get_sync_engine
        from sqlalchemy import text as sql_text

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        engine = _get_sync_engine()
        with engine.connect() as conn:
            rows = conn.execute(sql_text("""
                SELECT booster_box_id, ebay_active_listings_count
                FROM ebay_box_metrics_daily
                WHERE metric_date = :yesterday
            """), {"yesterday": yesterday}).fetchall()
        for r in rows:
            d = r._mapping if hasattr(r, "_mapping") else dict(r)
            bid = str(d["booster_box_id"])
            ct = d.get("ebay_active_listings_count")
            counts[bid] = int(ct) if ct is not None else None
        logger.info(f"Loaded {len(counts)} yesterday eBay active counts from DB")
    except Exception as e:
        logger.warning(f"Could not load yesterday eBay active counts: {e}")
    return counts


def process_active_results(
    box_id: str,
    filtered: List[Dict[str, Any]],
    tcg_floor_price: Optional[float],
    yesterday_active_count: Optional[int],
    today: str,
) -> Dict[str, Any]:
    """
    Process filtered active listings and write metrics to DB.

    Returns dict of computed metrics.
    """
    from app.services.ebay_metrics_writer import upsert_ebay_daily_metrics

    prices = [item["price"] for item in filtered if item.get("price")]

    # Count within 20% of TCG floor (for active_listings_count)
    ref_floor = tcg_floor_price if tcg_floor_price and tcg_floor_price > 0 else (min(prices) if prices else None)
    if ref_floor and ref_floor > 0:
        threshold = ref_floor * 1.20
        within_20pct = sum(1 for p in prices if p <= threshold)
    else:
        within_20pct = len(prices)

    median_price = round(statistics.median(prices), 2) if prices else None
    low_price = round(min(prices), 2) if prices else None

    # Delta from yesterday
    listings_added = None
    listings_removed = None
    if yesterday_active_count is not None and within_20pct is not None:
        delta = within_20pct - yesterday_active_count
        listings_added = delta
        listings_removed = max(0, -delta)

    # Write to DB
    upsert_ebay_daily_metrics(
        booster_box_id=box_id,
        metric_date=today,
        ebay_active_listings_count=within_20pct,
        ebay_active_median_price_usd=median_price,
        ebay_active_low_price_usd=low_price,
        ebay_listings_added_today=listings_added,
        ebay_listings_removed_today=listings_removed,
    )

    return {
        "active_count": within_20pct,
        "median_price": median_price,
        "low_price": low_price,
        "added": listings_added,
        "removed": listings_removed,
    }


def process_sold_results(
    box_id: str,
    filtered: List[Dict[str, Any]],
    target_date: str,
) -> Dict[str, Any]:
    """
    Process filtered sold listings: insert raw sales and write accumulated metrics.

    Args:
        box_id: Booster box UUID
        filtered: Filtered sold listings
        target_date: Date to count sales for (usually yesterday)

    Returns dict of computed metrics.
    """
    from app.services.ebay_metrics_writer import (
        upsert_ebay_daily_metrics,
        insert_ebay_sales_raw,
        query_accumulated_ebay_metrics,
    )

    # Filter to target date sales
    target_items = [item for item in filtered if item.get("sold_date") == target_date]
    logger.info(f"  Date filter: {len(target_items)} from {target_date}, {len(filtered) - len(target_items)} other dates")

    # Insert raw sales (all dates — dedup handles duplicates)
    sold_items = []
    for item in filtered:
        if not item.get("ebay_item_id"):
            continue
        sold_items.append({
            "ebay_item_id": item["ebay_item_id"],
            "title": item.get("title", ""),
            "sold_price_usd": item.get("price"),
            "sold_date": item.get("sold_date"),
            "item_url": item.get("item_url", ""),
            "sale_type": "sold",
        })

    inserted = insert_ebay_sales_raw(booster_box_id=box_id, sold_items=sold_items)
    logger.debug(f"  DB: inserted {inserted} rows into ebay_sales_raw")

    # Query accumulated metrics for target date (source of truth)
    accumulated = query_accumulated_ebay_metrics(box_id, target_date)

    # Upsert daily metrics with accumulated values
    upsert_ebay_daily_metrics(
        booster_box_id=box_id,
        metric_date=target_date,
        ebay_sales_count=accumulated["count"],
        ebay_volume_usd=accumulated["volume"],
        ebay_median_sold_price_usd=accumulated["median_price"],
        ebay_units_sold_count=accumulated["count"],
    )

    return {
        "sold_count": accumulated["count"],
        "volume": accumulated["volume"],
        "median_price": accumulated["median_price"],
        "inserted": inserted,
    }


def run_ebay_serpapi_scraper(
    debug_box_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point: scrape eBay via SerpApi for all 18 boxes.

    For each box:
    1. Search active listings (always) → process and write to DB
    2. If should_scrape_sold_today: search sold listings → process and write to DB

    Args:
        debug_box_id: If set, only scrape this box (for testing).

    Returns:
        Summary dict with results, errors, date, searches_used.
    """
    global _searches_used
    _searches_used = 0

    reference_time = datetime.now()
    today = reference_time.strftime("%Y-%m-%d")
    yesterday = (reference_time - timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"Phase 1b-SerpApi: starting for {today}")
    logger.info(f"  Counting sold from: {yesterday} (yesterday)")

    # Check API key
    api_key = settings.serpapi_api_key
    if not api_key:
        logger.error("SERPAPI_API_KEY not configured")
        return {"results": 0, "errors": ["SERPAPI_API_KEY not set"], "date": today, "searches_used": 0}

    # Load reference data
    tcg_floors = load_tcg_floor_prices()
    yesterday_active = load_yesterday_ebay_active()

    # Determine which boxes to scrape
    if debug_box_id:
        if debug_box_id not in SERPAPI_BOX_CONFIG:
            logger.error(f"Unknown box_id: {debug_box_id}")
            return {"results": 0, "errors": [f"Unknown box: {debug_box_id}"], "date": today, "searches_used": 0}
        box_items = [(debug_box_id, SERPAPI_BOX_CONFIG[debug_box_id])]
    else:
        box_items = list(SERPAPI_BOX_CONFIG.items())

    results_count = 0
    errors: List[str] = []

    for box_id, config in box_items:
        name = config["name"]
        query = config["search_query"]
        tcg_floor = tcg_floors.get(box_id)

        # Dynamic price range based on TCG floor (2x ceiling, 0.5x floor)
        # Falls back to hardcoded config values if no TCG floor available
        if tcg_floor and tcg_floor > 0:
            min_price = max(config["min_price"], int(tcg_floor * 0.5))
            max_price = max(config["max_price"], int(tcg_floor * 2.0))
        else:
            min_price = config["min_price"]
            max_price = config["max_price"]

        logger.info(f"Scraping {name}" + (f" (TCG floor: ${tcg_floor:.2f})" if tcg_floor else ""))

        # --- Active listings (always) ---
        try:
            active_raw = serpapi_search(query, "active", min_price, max_price, api_key)
            active_filtered = filter_serpapi_results(active_raw, "active", tcg_floor, min_price, max_price)
            active_metrics = process_active_results(
                box_id, active_filtered, tcg_floor,
                yesterday_active.get(box_id), today,
            )
            logger.info(
                f"  Active: {active_metrics['active_count']} listings, "
                f"floor=${active_metrics['low_price']}, "
                f"delta={active_metrics['added']}"
            )
        except Exception as e:
            logger.warning(f"  Active search failed for {name}: {e}")
            errors.append(f"{name} active: {e}")

        # --- Sold listings (tiered frequency) ---
        if should_scrape_sold_today(box_id):
            try:
                sold_raw = serpapi_search(query, "sold", min_price, max_price, api_key)
                sold_filtered = filter_serpapi_results(sold_raw, "sold", tcg_floor, min_price, max_price)
                sold_metrics = process_sold_results(box_id, sold_filtered, yesterday)
                logger.info(
                    f"  Sold: {sold_metrics['sold_count']} on {yesterday}, "
                    f"${sold_metrics['volume']:.2f} volume, "
                    f"median=${sold_metrics['median_price']}"
                )
            except Exception as e:
                logger.warning(f"  Sold search failed for {name}: {e}")
                errors.append(f"{name} sold: {e}")
        else:
            logger.info(f"  Sold: skipped (low-volume, next scrape in {3 - datetime.now().timetuple().tm_yday % 3} days)")

        results_count += 1

        # Small delay between boxes to be respectful to API
        if len(box_items) > 1 and box_id != box_items[-1][0]:
            time.sleep(0.5)

    logger.info(f"Phase 1b-SerpApi complete: {results_count}/{len(box_items)} boxes, {len(errors)} errors")
    logger.info(f"  Searches used: {_searches_used}/1000 monthly budget")

    return {
        "results": results_count,
        "errors": errors,
        "date": today,
        "searches_used": _searches_used,
    }


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(description="eBay SerpApi Scraper")
    parser.add_argument("--debug", type=str, help="Only scrape this box_id")
    args = parser.parse_args()

    result = run_ebay_serpapi_scraper(debug_box_id=args.debug)
    print(json.dumps(result, indent=2))
