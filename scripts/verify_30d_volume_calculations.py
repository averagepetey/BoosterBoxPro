#!/usr/bin/env python3
"""
Verify 30d volume calculations manually.

Usage:
  python scripts/verify_30d_volume_calculations.py [box_id]

Example:
  python scripts/verify_30d_volume_calculations.py
  python scripts/verify_30d_volume_calculations.py 550e8400-e29b-41d4-a716-446655440018

Prints:
- Entries in the last 30 days and each period's contribution (floor × sold × days).
- Manual rolling total.
- get_box_30d_volume() (rolling) and get_box_30d_volume_ramp_estimate() (ramp).
- get_box_30d_volume_or_ramp() (what we actually use: ramp if < 7 entries, else rolling).
- boxes_sold_30d_avg for spot-checking.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root so we can import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# OP-13 leaderboard UUID
OP13_ID = "550e8400-e29b-41d4-a716-446655440018"


def main():
    box_id = (sys.argv[1] if len(sys.argv) > 1 else OP13_ID).strip()

    from app.services.historical_data import (
        get_box_historical_data,
        get_box_30d_volume,
        get_box_30d_volume_ramp_estimate,
        get_box_30d_volume_or_ramp,
        get_box_30d_avg_sales,
        ROLLING_MIN_ENTRIES_30D,
    )

    entries = get_box_historical_data(box_id)
    if not entries:
        print(f"No historical data for box_id={box_id}")
        return

    entries = sorted(entries, key=lambda x: x.get("date", ""))
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    cutoff_obj = datetime.strptime(cutoff_date, "%Y-%m-%d")
    today = datetime.now()
    recent = [e for e in entries if (e.get("date") or "") >= cutoff_date]

    print("=" * 60)
    print(f"30d volume verification — box_id: {box_id}")
    print(f"Cutoff (30d ago): {cutoff_date}  Today: {today.strftime('%Y-%m-%d')}")
    print(f"Entries in last 30d: {len(recent)}  (rolling if >= {ROLLING_MIN_ENTRIES_30D}, else ramp)")
    print("=" * 60)

    if not recent:
        print("No entries in last 30 days.")
        rolling_result = get_box_30d_volume(box_id)
        ramp_result = get_box_30d_volume_ramp_estimate(box_id)
        smart_result = get_box_30d_volume_or_ramp(box_id)
        print(f"get_box_30d_volume()      = {rolling_result}")
        print(f"get_box_30d_volume_ramp_estimate() = {ramp_result}")
        print(f"get_box_30d_volume_or_ramp()      = {smart_result}")
        return

    # Manual rolling total
    print("\n--- Manual rolling total (each entry: floor × sold × days_in_period) ---")
    total = 0.0
    for i, entry in enumerate(recent):
        floor_price = entry.get("floor_price_usd") or 0
        sold = entry.get("boxes_sold_per_day") or entry.get("boxes_sold_today") or 0
        date_str = entry.get("date", "")
        if not date_str:
            continue
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        if i < len(recent) - 1:
            next_str = recent[i + 1].get("date", "")
            try:
                next_date = datetime.strptime(next_str, "%Y-%m-%d")
                start = max(entry_date, cutoff_obj)
                end = min(next_date, today)
                days = max(1, (end - start).days)
            except (ValueError, TypeError):
                days = 1
        else:
            start = max(entry_date, cutoff_obj)
            end = min(today, cutoff_obj + timedelta(days=30))
            days = max(1, (end - start).days)
        if len(recent) == 1:
            days = 30
        contrib = floor_price * sold * days
        total += contrib
        print(f"  {date_str}  floor={floor_price:.2f}  sold/d={sold:.2f}  days={days}  =>  {contrib:,.2f}")

    print(f"\n  Manual rolling total (sum above) = {total:,.2f}")

    # 30d avg sales
    avg_sales = get_box_30d_avg_sales(box_id)
    print(f"\n  boxes_sold_30d_avg (from service) = {avg_sales}")

    # Ramp formula (first + current) / 2 * 30 * avg_sales
    if len(recent) >= 2 and avg_sales:
        first_floor = recent[0].get("floor_price_usd") or 0
        current_floor = recent[-1].get("floor_price_usd") or 0
        ramp_manual = 30.0 * avg_sales * (first_floor + current_floor) / 2.0
        print(f"\n--- Ramp formula (first month only): 30 × avg_sales × (first_floor + current_floor) / 2 ---")
        print(f"  first_floor={first_floor:.2f}  current_floor={current_floor:.2f}  avg_sales={avg_sales}")
        print(f"  Manual ramp = 30 × {avg_sales} × ({first_floor:.2f} + {current_floor:.2f}) / 2 = {ramp_manual:,.2f}")

    # Service results
    print("\n--- Service results ---")
    rolling_result = get_box_30d_volume(box_id)
    ramp_result = get_box_30d_volume_ramp_estimate(box_id)
    smart_result = get_box_30d_volume_or_ramp(box_id)
    print(f"  get_box_30d_volume()             = {rolling_result}  (rolling)")
    print(f"  get_box_30d_volume_ramp_estimate() = {ramp_result}  (ramp)")
    print(f"  get_box_30d_volume_or_ramp()       = {smart_result}  (used: ramp if <{ROLLING_MIN_ENTRIES_30D} entries, else rolling)")

    # Spot check
    if rolling_result is not None and abs((rolling_result or 0) - total) > 0.02:
        print(f"\n  WARNING: Manual rolling total {total:,.2f} != get_box_30d_volume() {rolling_result}")
    else:
        print(f"\n  OK: Rolling total matches get_box_30d_volume()")
    print("=" * 60)


if __name__ == "__main__":
    main()
