#!/usr/bin/env python3
"""
One-off script: Re-date 2026-01-31 scraper data → 2026-01-30
-------------------------------------------------------------
Today's scraper run (dated 2026-01-31) should be treated as 2026-01-30 data,
so the automatic cron job tomorrow generates fresh 2026-01-31 data.

Steps:
1. Load historical_entries.json
2. For each box: find the 2026-01-31 scraper entry and the 2026-01-30 Apify entry
3. Change scraper entry date to 2026-01-30 — becomes the official 01-30 entry
4. Merge Apify sales fields into the scraper entry (both listings + sales data)
5. Remove the old standalone Apify-only 01-30 entry (overwritten by merged one)
6. Recompute boxes_added_today delta using 2026-01-29 data (with >100 guard)
7. Save back to JSON
8. Run Phase 3 rolling metrics for 2026-01-30
"""

import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

HISTORICAL_FILE = project_root / "data" / "historical_entries.json"

APIFY_FIELDS = [
    "boxes_sold_per_day",
    "boxes_sold_today",
    "daily_volume_usd",
    "volume_7d",
    "unified_volume_usd",
    "market_price_usd",
    "estimated_actual_sales_today",
    "baseline_7d_avg",
    "avg_change_from_yesterday",
    "avg_change_pct",
    "price_change_from_yesterday",
    "price_change_pct",
    "spike_detected",
    "spike_magnitude_pct",
]


def main():
    print("Loading historical_entries.json...")
    with open(HISTORICAL_FILE, "r") as f:
        data = json.load(f)

    merged_count = 0
    skipped_count = 0

    for box_id, entries in data.items():
        # Find 01-31 scraper entry and 01-30 Apify entry
        scraper_jan31 = None
        apify_jan30 = None
        jan29_entry = None

        for e in entries:
            d = e.get("date")
            if d == "2026-01-31":
                scraper_jan31 = e
            elif d == "2026-01-30":
                apify_jan30 = e
            elif d == "2026-01-29":
                jan29_entry = e

        if scraper_jan31 is None:
            skipped_count += 1
            continue

        # Step 3: Re-date scraper entry to 01-30
        scraper_jan31["date"] = "2026-01-30"

        # Step 4: Merge Apify sales fields into the scraper entry
        if apify_jan30:
            for field in APIFY_FIELDS:
                if apify_jan30.get(field) is not None and scraper_jan31.get(field) is None:
                    scraper_jan31[field] = apify_jan30[field]

        # Step 5: Remove the old standalone Apify-only 01-30 entry
        data[box_id] = [e for e in entries if not (e.get("date") == "2026-01-30" and e is not scraper_jan31)]

        # Step 6: Recompute boxes_added_today delta using 01-29 data
        yesterday_alc = jan29_entry.get("active_listings_count") if jan29_entry else None
        if yesterday_alc is not None:
            yesterday_alc = int(yesterday_alc)

        today_alc = scraper_jan31.get("active_listings_count") or 0

        if yesterday_alc is not None and yesterday_alc > 100:
            # Guard: inflated data, skip delta
            scraper_jan31["boxes_added_today"] = None
            scraper_jan31["boxes_removed_today"] = None
        elif yesterday_alc is not None:
            delta = today_alc - yesterday_alc
            scraper_jan31["boxes_added_today"] = max(0, delta)
            scraper_jan31["boxes_removed_today"] = max(0, -delta)
        # else: leave as-is

        merged_count += 1
        fp = scraper_jan31.get("floor_price_usd", "?")
        alc = scraper_jan31.get("active_listings_count", "?")
        sold = scraper_jan31.get("boxes_sold_per_day", "?")
        print(f"  {box_id}: merged → 01-30 | floor=${fp} listings={alc} sold/day={sold}")

    # Step 7: Save back to JSON
    print(f"\nSaving... ({merged_count} merged, {skipped_count} skipped)")
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("Saved historical_entries.json")

    # Step 8: Run Phase 3 rolling metrics for 01-30
    print("\nRunning Phase 3: Rolling Metrics for 2026-01-30...")
    from scripts.rolling_metrics import compute_rolling_metrics

    result = compute_rolling_metrics("2026-01-30")
    print(f"Phase 3 result: {json.dumps(result, indent=2)}")
    print("\nDone!")


if __name__ == "__main__":
    main()
