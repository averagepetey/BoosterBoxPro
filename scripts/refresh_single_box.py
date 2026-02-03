#!/usr/bin/env python3
"""
Refresh Apify sales data for a single box.
Usage: python scripts/refresh_single_box.py op-13
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.tcgplayer_apify import (
    TCGplayerApifyService,
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

# Map short names to box IDs
BOX_SHORT_NAMES = {
    "op-01-blue": "860ffe3f-9286-42a9-ad4e-d079a6add6f4",
    "op-01-white": "18ade4d4-512b-4261-a119-2b6cfaf1fa2a",
    "op-02": "f8d8f3ee-2020-4aa9-bcf0-2ef4ec815320",
    "op-03": "d3929fc6-6afa-468a-b7a1-ccc0f392131a",
    "op-04": "526c28b7-bc13-449b-a521-e63bdd81811a",
    "op-05": "6ea1659d-7b86-46c5-8fb2-0596262b8e68",
    "op-06": "b4e3c7bf-3d55-4b25-80ca-afaecb1df3fa",
    "op-07": "9bfebc47-4a92-44b3-b157-8c53d6a6a064",
    "op-08": "d0faf871-a930-4c80-a981-9df8741c90a9",
    "op-09": "c035aa8b-6bec-4237-aff5-1fab1c0f53ce",
    "op-10": "3429708c-43c3-4ed8-8be3-706db8b062bd",
    "op-11": "46039dfc-a980-4bbd-aada-8cc1e124b44b",
    "op-12": "b7ae78ec-3ea4-488b-8470-e05f80fdb2dc",
    "op-13": "2d7d2b54-596d-4c80-a02f-e2eeefb45a34",
    "eb-01": "3b17b708-b35b-4008-971e-240ade7afc9c",
    "eb-02": "7509a855-f6da-445e-b445-130824d81d04",
    "prb-01": "743bf253-98ca-49d5-93fe-a3eaef9f72c1",
    "prb-02": "3bda2acb-a55c-4a6e-ae93-dff5bad27e62",
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/refresh_single_box.py <box-name>")
        print("Example: python scripts/refresh_single_box.py op-13")
        print(f"\nAvailable boxes: {', '.join(BOX_SHORT_NAMES.keys())}")
        sys.exit(1)

    box_name = sys.argv[1].lower()

    if box_name not in BOX_SHORT_NAMES:
        print(f"Unknown box: {box_name}")
        print(f"Available boxes: {', '.join(BOX_SHORT_NAMES.keys())}")
        sys.exit(1)

    box_id = BOX_SHORT_NAMES[box_name]
    config = TCGPLAYER_URLS[box_id]

    print(f"=" * 60)
    print(f"Refreshing sales data for: {config['name']}")
    print(f"Box ID: {box_id}")
    print(f"URL: {config['url']}")
    print(f"=" * 60)

    # Load existing historical data
    data_dir = project_root / "data"
    historical_file = data_dir / "historical_entries.json"

    historical = {}
    if historical_file.exists():
        with open(historical_file) as f:
            historical = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")

    # Initialize Apify service
    from app.config import settings
    from apify_client import ApifyClient

    api_token = settings.apify_api_token
    if not api_token:
        print("ERROR: APIFY_API_TOKEN not configured in .env")
        sys.exit(1)

    client = ApifyClient(api_token)

    print(f"\nFetching from Apify...")

    try:
        run = client.actor("scraped/tcgplayer-sales-history").call(run_input={"url": config["url"]})
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

        if not items:
            print("ERROR: No data returned from Apify")
            sys.exit(1)

        data = items[0]
        buckets = data.get("buckets", [])
        buckets = sorted(buckets, key=lambda b: b.get("bucketStartDate", ""), reverse=True)

        print(f"\n📊 RAW APIFY DATA:")
        print(f"  Total quantity sold (lifetime): {data.get('totalQuantitySold')}")
        print(f"  Lifetime avg (Apify): {_safe_float(data.get('averageDailyQuantitySold')):.2f}/day")
        print(f"  Total buckets: {len(buckets)}")

        # Show recent buckets
        print(f"\n📅 RECENT WEEKLY BUCKETS (newest first):")
        for i, bucket in enumerate(buckets[:5]):
            start = bucket.get("bucketStartDate", "")[:10]
            qty = _safe_int(bucket.get("quantitySold", 0))
            price = _safe_float(bucket.get("marketPrice", 0))
            print(f"  [{i}] {start}: {qty} sold @ ${price:.2f}")

        # Current incomplete bucket
        incomplete = get_current_incomplete_bucket(buckets, today)
        if incomplete:
            inc_start = incomplete.get("bucketStartDate", "")[:10]
            inc_qty = incomplete.get("quantitySold", 0)
            print(f"\n🔄 CURRENT INCOMPLETE BUCKET:")
            print(f"  Start: {inc_start}")
            print(f"  Quantity so far: {inc_qty}")

        # Complete buckets
        complete = get_complete_weekly_buckets(buckets, today)
        if complete:
            print(f"\n✅ MOST RECENT COMPLETE BUCKET:")
            comp_start = complete[0].get("bucketStartDate", "")[:10]
            comp_qty = _safe_int(complete[0].get("quantitySold", 0))
            print(f"  Start: {comp_start}")
            print(f"  Quantity: {comp_qty} (= {comp_qty/7:.2f}/day)")

        # Get previous entry for delta computation
        prev_entry = get_previous_entry(historical, box_id, today)
        if prev_entry:
            print(f"\n📂 PREVIOUS ENTRY (from historical_entries.json):")
            print(f"  Date: {prev_entry.get('date')}")
            print(f"  current_bucket_start: {prev_entry.get('current_bucket_start')}")
            print(f"  current_bucket_qty: {prev_entry.get('current_bucket_qty')}")
            print(f"  boxes_sold_today: {prev_entry.get('boxes_sold_today')}")
        else:
            print(f"\n📂 NO PREVIOUS ENTRY for this box")

        # Compute metrics
        boxes_sold_per_day = compute_daily_sales_from_buckets(buckets, today=today) or 0
        weekly_rate = compute_this_week_daily_rate(buckets, today=today) or boxes_sold_per_day

        # Delta tracking
        boxes_sold_today = weekly_rate
        delta_source = "weekly_rate_fallback"
        if incomplete and prev_entry:
            current_bucket_start = incomplete.get("bucketStartDate", "")[:10]
            current_bucket_qty = _safe_int(incomplete.get("quantitySold"))
            delta, source = compute_delta_sold_today(current_bucket_qty, current_bucket_start, prev_entry)
            if delta is not None:
                boxes_sold_today = delta
                delta_source = source

        # Market price
        if buckets:
            market_price = _safe_float(buckets[0].get("marketPrice"))
        else:
            market_price = 0

        print(f"\n📈 COMPUTED METRICS:")
        print(f"  boxes_sold_per_day (active avg): {boxes_sold_per_day}")
        print(f"  weekly_rate (recent complete week): {weekly_rate}")
        print(f"  boxes_sold_today: {boxes_sold_today} (source: {delta_source})")
        print(f"  market_price: ${_safe_float(market_price):.2f}")

        # Ask to update
        print(f"\n" + "=" * 60)
        response = input("Update historical_entries.json with this data? [y/N]: ")

        if response.lower() == 'y':
            # Build new entry
            new_entry = {
                "date": today,
                "source": "apify_tcgplayer",
                "boxes_sold_per_day": boxes_sold_per_day,
                "boxes_sold_today": boxes_sold_today,
                "current_bucket_start": incomplete.get("bucketStartDate", "")[:10] if incomplete else None,
                "current_bucket_qty": _safe_int(incomplete.get("quantitySold")) if incomplete else None,
                "delta_source": delta_source,
                "floor_price_usd": market_price,
                "market_price_usd": market_price,
                "daily_volume_usd": round(boxes_sold_today * market_price, 2),
                "timestamp": datetime.now().isoformat(),
            }

            # Update historical
            if box_id not in historical:
                historical[box_id] = []
            historical[box_id] = [e for e in historical[box_id] if e.get("date") != today]
            historical[box_id].append(new_entry)

            with open(historical_file, "w") as f:
                json.dump(historical, f, indent=2)

            print(f"✅ Updated historical_entries.json")
        else:
            print("Skipped update.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
