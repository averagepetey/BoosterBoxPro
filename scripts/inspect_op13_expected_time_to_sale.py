#!/usr/bin/env python3
"""
Inspect what data the box detail API uses for OP-13 expected time to sale.
Prints: source (DB vs JSON), latest entry, and computed expected_days_to_sell.
"""
import sys
from pathlib import Path

# Project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# OP-13 DB UUID (from app.services.historical_data DB_TO_LEADERBOARD_UUID_MAP)
OP13_DB_UUID = "2d7d2b54-596d-4c80-a02f-e2eeefb45a34"


def main():
    from app.services.historical_data import (
        get_box_historical_data,
        get_box_price_history,
        get_box_30d_avg_sales,
    )

    box_id = OP13_DB_UUID

    # 1) Raw entries (to see if source is DB or JSON)
    raw_entries = get_box_historical_data(box_id, prefer_db=True)
    if not raw_entries:
        print("No historical data found for OP-13 (DB or JSON).")
        return

    # Detect source: DB returns entries with no 'source' key (from _row_to_entry); JSON has 'source'
    has_source = any(e.get("source") for e in raw_entries)
    source = "JSON (historical_entries.json)" if has_source else "DB (box_metrics_unified)"
    print(f"Source: {source}")
    print(f"Total entries: {len(raw_entries)}")
    print()

    # 2) Same as box detail API: get_box_price_history (adds listings_within_10pct_floor etc.)
    historical_data = get_box_price_history(box_id, days=90)
    if not historical_data:
        print("get_box_price_history returned no entries (e.g. no floor_price_usd).")
        return

    latest = historical_data[-1]
    print("Latest entry (used for box detail metrics):")
    print(f"  date: {latest.get('date')}")
    print(f"  floor_price_usd: {latest.get('floor_price_usd')}")
    print(f"  active_listings_count: {latest.get('active_listings_count')}")
    print(f"  listings_within_10pct_floor: {latest.get('listings_within_10pct_floor')}")
    print(f"  boxes_sold_per_day: {latest.get('boxes_sold_per_day')}")
    print(f"  boxes_sold_30d_avg: {latest.get('boxes_sold_30d_avg')}")
    print(f"  boxes_added_today: {latest.get('boxes_added_today')}")
    print()

    # 3) Compute expected_days_to_sell exactly like main.py (including active_listings fallback)
    active_listings = latest.get("active_listings_count") or 0
    if not active_listings and len(historical_data) > 1:
        for entry in reversed(historical_data[:-1]):
            alc = entry.get("active_listings_count")
            if alc is not None and alc > 0:
                active_listings = int(alc)
                print(f"  (active_listings_count came from earlier entry date={entry.get('date')}: {active_listings})")
                break
        print()
    supply_10pct = latest.get("listings_within_10pct_floor")
    supply = supply_10pct if supply_10pct is not None and supply_10pct > 0 else active_listings

    boxes_sold_per_day = latest.get("boxes_sold_per_day") or 0
    avg_sales_30d = latest.get("boxes_sold_30d_avg")
    if avg_sales_30d is None:
        try:
            avg_sales_30d = get_box_30d_avg_sales(box_id)
        except Exception:
            avg_sales_30d = None

    sales_per_day = boxes_sold_per_day or avg_sales_30d

    avg_boxes_added_per_day = latest.get("avg_boxes_added_per_day")
    if avg_boxes_added_per_day is None and historical_data:
        recent = historical_data[-30:] if len(historical_data) >= 30 else historical_data
        added_vals = [e.get("boxes_added_today", 0) for e in recent if e.get("boxes_added_today") is not None]
        avg_boxes_added_per_day = sum(added_vals) / len(added_vals) if added_vals else 0
    else:
        avg_boxes_added_per_day = avg_boxes_added_per_day or 0

    listings_added_per_day = avg_boxes_added_per_day or 0.0
    net_burn = (sales_per_day - listings_added_per_day) if sales_per_day else 0

    expected_days_to_sell = None
    if supply and supply > 0 and sales_per_day and sales_per_day > 0 and net_burn > 0.05:
        raw = supply / net_burn
        expected_days_to_sell = round(max(1.0, min(365.0, raw)), 2)

    print("Expected time to sale calculation:")
    print(f"  supply (listings_within_10pct_floor or active_listings_count): {supply}")
    print(f"  sales_per_day (boxes_sold_per_day or boxes_sold_30d_avg): {sales_per_day}")
    print(f"  listings_added_per_day (avg_boxes_added_per_day): {listings_added_per_day}")
    print(f"  net_burn: {net_burn}")
    print(f"  expected_days_to_sell = supply / net_burn = {supply} / {net_burn} = {expected_days_to_sell}")
    print()
    print(f"Result shown on box detail: {expected_days_to_sell} days")


if __name__ == "__main__":
    main()
