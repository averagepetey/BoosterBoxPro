#!/usr/bin/env python3
"""
Run full daily refresh for a specific target date.
Usage: python scripts/refresh_for_date.py 2026-02-02
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_apify_refresh(target_date: str):
    """Phase 1: Fetch TCGplayer sales data from Apify for all boxes."""
    logger.info("=" * 60)
    logger.info(f"Phase 1: Apify TCGplayer Sales (target_date={target_date})")
    logger.info("=" * 60)

    from app.config import settings
    from apify_client import ApifyClient
    from app.services.tcgplayer_apify import (
        TCGPLAYER_URLS,
        compute_daily_sales_from_buckets,
        compute_this_week_daily_rate,
        get_current_incomplete_bucket,
        get_complete_weekly_buckets,
        get_previous_entry,
        compute_delta_sold_today,
        _safe_int,
        _safe_float,
    )

    api_token = settings.apify_api_token
    if not api_token:
        raise ValueError("APIFY_API_TOKEN not configured")

    client = ApifyClient(api_token)

    # Load existing historical data
    data_dir = project_root / "data"
    historical_file = data_dir / "historical_entries.json"

    historical = {}
    if historical_file.exists():
        with open(historical_file) as f:
            historical = json.load(f)

    success_count = 0
    error_count = 0

    for box_id, config in TCGPLAYER_URLS.items():
        url = config.get("url")
        name = config.get("name", box_id)

        if not url:
            continue

        logger.info(f"Fetching {name}...")

        try:
            run = client.actor("scraped/tcgplayer-sales-history").call(run_input={"url": url})
            items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

            if not items:
                logger.warning(f"  No data for {name}")
                error_count += 1
                continue

            data = items[0]
            buckets = data.get("buckets", [])
            buckets = sorted(buckets, key=lambda b: b.get("bucketStartDate", ""), reverse=True)

            # Market price from most recent bucket
            if buckets:
                market_price = _safe_float(buckets[0].get("marketPrice"))
            else:
                market_price = 0

            # Compute sales metrics
            boxes_sold_per_day = compute_daily_sales_from_buckets(buckets, today=target_date) or 0
            weekly_rate = compute_this_week_daily_rate(buckets, today=target_date) or boxes_sold_per_day

            # Get incomplete bucket for delta tracking
            incomplete = get_current_incomplete_bucket(buckets, target_date)
            current_bucket_start = incomplete.get("bucketStartDate", "")[:10] if incomplete else None
            current_bucket_qty = _safe_int(incomplete.get("quantitySold")) if incomplete else None

            # Delta tracking
            prev_entry = get_previous_entry(historical, box_id, target_date)
            boxes_sold_today = weekly_rate
            delta_source = "weekly_rate"

            if current_bucket_qty is not None and current_bucket_start:
                # If bucket started on target_date, use full bucket qty as "sold today"
                if current_bucket_start == target_date:
                    boxes_sold_today = current_bucket_qty
                    delta_source = "bucket_total"
                elif prev_entry:
                    delta, source = compute_delta_sold_today(current_bucket_qty, current_bucket_start, prev_entry)
                    if delta is not None:
                        boxes_sold_today = delta
                        delta_source = source

            # Find/update entry for target_date
            if box_id not in historical:
                historical[box_id] = []

            # Find existing entry for target_date
            existing_entry = None
            for entry in historical[box_id]:
                if entry.get("date") == target_date:
                    existing_entry = entry
                    break

            if existing_entry:
                # Update existing entry
                existing_entry["boxes_sold_per_day"] = boxes_sold_per_day
                existing_entry["boxes_sold_today"] = boxes_sold_today
                existing_entry["market_price_usd"] = market_price
                existing_entry["floor_price_usd"] = market_price
                existing_entry["current_bucket_start"] = current_bucket_start
                existing_entry["current_bucket_qty"] = current_bucket_qty
                existing_entry["delta_source"] = delta_source
                existing_entry["daily_volume_usd"] = round(boxes_sold_today * market_price, 2)
                existing_entry["apify_refresh_timestamp"] = datetime.now().isoformat()
            else:
                # Create new entry
                new_entry = {
                    "date": target_date,
                    "source": "apify_tcgplayer",
                    "boxes_sold_per_day": boxes_sold_per_day,
                    "boxes_sold_today": boxes_sold_today,
                    "market_price_usd": market_price,
                    "floor_price_usd": market_price,
                    "current_bucket_start": current_bucket_start,
                    "current_bucket_qty": current_bucket_qty,
                    "delta_source": delta_source,
                    "daily_volume_usd": round(boxes_sold_today * market_price, 2),
                    "timestamp": datetime.now().isoformat(),
                }
                historical[box_id].append(new_entry)

            logger.info(f"  ✅ {name}: {boxes_sold_today} sold today @ ${market_price:.2f}")
            success_count += 1

        except Exception as e:
            logger.error(f"  ❌ {name}: {e}")
            error_count += 1

    # Save
    with open(historical_file, "w") as f:
        json.dump(historical, f, indent=2)

    logger.info(f"\nPhase 1 complete: {success_count} success, {error_count} errors")
    return success_count, error_count


async def run_ebay_scraper(target_date: str):
    """Phase 1b: Fetch eBay sales data."""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Phase 1b: eBay Scraper (target_date={target_date})")
    logger.info("=" * 60)

    try:
        from scripts.ebay_scraper import run_ebay_scraper as ebay_scrape
        result = await ebay_scrape()
        logger.info(f"  ✅ eBay: {result.get('results', 0)} boxes, {len(result.get('errors', []))} errors")
        return result
    except Exception as e:
        logger.warning(f"  ⚠️ eBay scraper failed (non-fatal): {e}")
        return {"results": 0, "errors": [str(e)]}


async def run_listings_scraper(target_date: str):
    """Phase 2: Fetch active listings count from TCGplayer."""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Phase 2: Listings Scraper (target_date={target_date})")
    logger.info("=" * 60)

    try:
        from scripts.listings_scraper import run_scraper
        results, errors = await run_scraper()
        logger.info(f"  ✅ Listings: {len(results)} success, {len(errors)} errors")
        return len(results), len(errors)
    except Exception as e:
        logger.error(f"  ❌ Listings scraper failed: {e}")
        return 0, 0


def run_rolling_metrics(target_date: str):
    """Phase 3: Compute rolling metrics."""
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Phase 3: Rolling Metrics (target_date={target_date})")
    logger.info("=" * 60)

    try:
        from scripts.rolling_metrics import compute_rolling_metrics
        result = compute_rolling_metrics(target_date=target_date)
        logger.info(f"  ✅ Rolling metrics: {result.get('boxes_updated', 0)} boxes, {result.get('db_updated', 0)} DB rows")
        return result
    except Exception as e:
        logger.error(f"  ❌ Rolling metrics failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/refresh_for_date.py YYYY-MM-DD")
        print("Example: python scripts/refresh_for_date.py 2026-02-02")
        sys.exit(1)

    target_date = sys.argv[1]

    # Validate date format
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print(f"Invalid date format: {target_date}. Use YYYY-MM-DD.")
        sys.exit(1)

    logger.info("=" * 70)
    logger.info(f"Full Daily Refresh for {target_date}")
    logger.info("=" * 70)

    start_time = datetime.now()

    # Phase 1: Apify
    apify_success, apify_errors = run_apify_refresh(target_date)

    # Phase 1b: eBay
    ebay_result = asyncio.run(run_ebay_scraper(target_date))

    # Phase 2: Listings
    listings_success, listings_errors = asyncio.run(run_listings_scraper(target_date))

    # Phase 3: Rolling Metrics
    metrics_result = run_rolling_metrics(target_date)

    # Summary
    duration = (datetime.now() - start_time).total_seconds()

    logger.info("")
    logger.info("=" * 70)
    logger.info("REFRESH COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Target date: {target_date}")
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Apify: {apify_success} success, {apify_errors} errors")
    logger.info(f"eBay: {ebay_result.get('results', 0)} boxes")
    logger.info(f"Listings: {listings_success} success, {listings_errors} errors")
    logger.info(f"DB rows updated: {metrics_result.get('db_updated', 0)}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
