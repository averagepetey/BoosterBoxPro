#!/usr/bin/env python3
"""
One-off: Show what data would be implemented for OP-13 box detail based on
the latest scrape + existing history. No DB or API changes.
Output: avg daily sold, boxes added, total listings, days to 20% calculation.
"""

import json
from pathlib import Path
from collections import defaultdict

# OP-13: leaderboard UUID (used by box detail) and TCG UUID (used by scraper in JSON)
OP13_LEADERBOARD_ID = "550e8400-e29b-41d4-a716-446655440018"
OP13_TCG_ID = "2d7d2b54-596d-4c80-a02f-e2eeefb45a34"

def load_json():
    path = Path(__file__).resolve().parent.parent / "data" / "historical_entries.json"
    with open(path, "r") as f:
        return json.load(f)

def get_active_listings(entry):
    """Resolve listing count from various keys the scraper/history use."""
    return (
        entry.get("active_listings_count")
        or entry.get("listings_count")
        or entry.get("listings_count_in_range")
    )

def merge_same_date(entries):
    by_date = defaultdict(list)
    for e in entries:
        d = e.get("date")
        if d:
            by_date[d].append(e)
    merged = []
    for date_str in sorted(by_date.keys()):
        group = by_date[date_str]
        if len(group) == 1:
            merged.append(group[0].copy())
            continue
        base = group[0].copy()
        total_listings = 0
        for e in group:
            alc = get_active_listings(e)
            if alc is not None:
                alc = int(alc)
                if alc > total_listings:
                    total_listings = alc
            alc2 = e.get("active_listings_count")
            if alc2 is not None and int(alc2) > total_listings:
                total_listings = int(alc2)
        if total_listings > 0:
            base["active_listings_count"] = total_listings
        merged.append(base)
    return merged

def main():
    data = load_json()
    entries_leaderboard = data.get(OP13_LEADERBOARD_ID, [])
    entries_tcg = data.get(OP13_TCG_ID, [])
    combined = list(entries_leaderboard) + list(entries_tcg)
    merged = merge_same_date(combined)
    merged.sort(key=lambda x: x.get("date", ""))

    # Latest entry (what box detail would use as "latest")
    latest = merged[-1] if merged else {}
    latest_date = latest.get("date", "N/A")

    # Total listings: from latest entry, or most recent entry that has it (e.g. latest scrape)
    total_listings = (
        latest.get("active_listings_count")
        or get_active_listings(latest)
    )
    if total_listings is None and merged:
        for e in reversed(merged):
            total_listings = e.get("active_listings_count") or get_active_listings(e)
            if total_listings is not None:
                break
    if total_listings is not None:
        total_listings = int(total_listings)

    # 30-day average sold: from last 30 entries that have boxes_sold_per_day
    sales_values = []
    for e in merged[-60:]:  # look at last 60 to get up to 30 with values
        v = e.get("boxes_sold_per_day") or e.get("boxes_sold_today")
        if v is not None:
            sales_values.append(float(v))
    avg_daily_sold = (sum(sales_values) / len(sales_values)) if sales_values else None
    if avg_daily_sold is not None:
        avg_daily_sold = round(avg_daily_sold, 2)

    # Avg boxes added per day (last 30 entries)
    added_values = []
    for e in merged[-60:]:
        v = e.get("boxes_added_today")
        if v is not None:
            added_values.append(int(v))
    avg_boxes_added_per_day = (sum(added_values) / len(added_values)) if added_values else 0
    avg_boxes_added_per_day = round(avg_boxes_added_per_day, 2)

    # Boxes added "today" – scraper does not provide this (it only provides total listings)
    boxes_added_today = latest.get("boxes_added_today")

    # Days to 20% (box detail formula)
    # days_to_20pct = active_listings / (boxes_sold_30d_avg - avg_boxes_added_per_day)
    days_to_20pct = None
    if avg_daily_sold is not None and total_listings is not None and total_listings > 0:
        net_burn = avg_daily_sold - avg_boxes_added_per_day
        if net_burn > 0.05:
            days_to_20pct = round(total_listings / net_burn, 2)
            if days_to_20pct > 180:
                days_to_20pct = 180.0
        elif net_burn <= 0:
            days_to_20pct = None  # N/A

    # ---- Report ----
    print("OP-13 (Carrying on His Will) – data that would drive the box detail page")
    print("(based on latest scrape + historical_entries.json, no implementation yet)\n")
    print(f"Latest entry date:        {latest_date}")
    print(f"Total listings (≤20%):    {total_listings if total_listings is not None else 'N/A'}  (from latest scrape/listings data)")
    print(f"Avg daily sold (30d):     {avg_daily_sold if avg_daily_sold is not None else 'N/A'}  (from historical entries)")
    print(f"Boxes added today:       {boxes_added_today if boxes_added_today is not None else 'N/A'}  (scraper does not set this)")
    print(f"Avg boxes added/day:     {avg_boxes_added_per_day}  (from history; 0 if no data)")
    print()
    print("Days to 20% calculation:")
    if days_to_20pct is not None:
        print(f"  active_listings / (avg_sales_30d - avg_boxes_added_per_day)")
        print(f"  = {total_listings} / ({avg_daily_sold} - {avg_boxes_added_per_day})")
        print(f"  = {total_listings} / {avg_daily_sold - avg_boxes_added_per_day}")
        print(f"  => days_to_20pct = {days_to_20pct}")
    else:
        print("  => N/A (need positive net burn rate: avg_sales_30d > avg_boxes_added_per_day)")
    print()
    print("Sources: leaderboard UUID + TCG UUID entries merged by date; latest row used for listings/sold; 30d avg from recent entries.")

if __name__ == "__main__":
    main()
