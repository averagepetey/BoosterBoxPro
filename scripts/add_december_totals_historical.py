"""
Add December 2025 entries to historical_entries.json so volume_7d, volume_30d,
and 30d average sales have enough data points for accuracy.

Uses the same December snapshot (Dec 25 spreadsheet data) for additional dates:
Dec 4, 11, 18, 30, 31. Idempotent: skips dates that already exist.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

# Same December snapshot as create_december_25_historical_entries.py
DECEMBER_SNAPSHOT = {
    "OP-01 (Blue)": {"floor_price_usd": 3998.49, "active_listings_count": 0, "boxes_sold_per_day": 1.38},
    "OP-01 (White)": {"floor_price_usd": 1431.94, "active_listings_count": 3, "boxes_sold_per_day": 1.86},
    "OP-02": {"floor_price_usd": 378.17, "active_listings_count": 27, "boxes_sold_per_day": 2.43},
    "OP-03": {"floor_price_usd": 392.02, "active_listings_count": 4, "boxes_sold_per_day": 0.93},
    "OP-04": {"floor_price_usd": 365.23, "active_listings_count": 13, "boxes_sold_per_day": 0.96},
    "OP-05": {"floor_price_usd": 776.05, "active_listings_count": 28, "boxes_sold_per_day": 4.64},
    "OP-06": {"floor_price_usd": 256.90, "active_listings_count": 134, "boxes_sold_per_day": 3.14},
    "EB-01": {"floor_price_usd": 765.78, "active_listings_count": 2, "boxes_sold_per_day": 1.18},
    "OP-07": {"floor_price_usd": 192.50, "active_listings_count": 38, "boxes_sold_per_day": 3.25},
    "OP-08": {"floor_price_usd": 153.22, "active_listings_count": 72, "boxes_sold_per_day": 1.96},
    "PRB-01": {"floor_price_usd": 738.72, "active_listings_count": 8, "boxes_sold_per_day": 1.11},
    "OP-09": {"floor_price_usd": 421.27, "active_listings_count": 58, "boxes_sold_per_day": 3.93},
    "OP-10": {"floor_price_usd": 154.65, "active_listings_count": 43, "boxes_sold_per_day": 3.25},
    "EB-02": {"floor_price_usd": 445.00, "active_listings_count": 6, "boxes_sold_per_day": 1.46},
    "OP-11": {"floor_price_usd": 244.32, "active_listings_count": 16, "boxes_sold_per_day": 4.54},
    "OP-12": {"floor_price_usd": 145.27, "active_listings_count": 46, "boxes_sold_per_day": 4.57},
    "PRB-02": {"floor_price_usd": 245.80, "active_listings_count": 14, "boxes_sold_per_day": 2.71},
    "OP-13": {"floor_price_usd": 362.52, "active_listings_count": 22, "boxes_sold_per_day": 19.32},
}

# December dates to add (same snapshot; gives volume sums more data points)
DECEMBER_DATES = ["2025-12-04", "2025-12-11", "2025-12-18", "2025-12-30", "2025-12-31"]


def _key_for_box(product_name: str) -> Optional[str]:
    set_code_match = re.search(r"(OP|EB|PRB)-\d+", product_name, re.IGNORECASE)
    if not set_code_match:
        return None
    set_code = set_code_match.group(0).upper()
    if "(Blue)" in product_name:
        return "OP-01 (Blue)" if set_code == "OP-01" else set_code
    if "(White)" in product_name:
        return "OP-01 (White)" if set_code == "OP-01" else set_code
    return set_code


def add_december_totals() -> int:
    historical_file = Path(__file__).parent.parent / "data" / "historical_entries.json"
    leaderboard_file = Path(__file__).parent.parent / "data" / "leaderboard.json"

    with open(leaderboard_file, "r") as f:
        leaderboard = json.load(f)

    if historical_file.exists():
        with open(historical_file, "r") as f:
            historical_data = json.load(f)
    else:
        historical_data = {}

    existing_dates_by_box = {
        box_id: {e.get("date") for e in entries}
        for box_id, entries in historical_data.items()
    }
    created_count = 0

    for box in leaderboard.get("data", []):
        product_name = box.get("product_name", "")
        box_id = box.get("id")
        key = _key_for_box(product_name)
        if not key or key not in DECEMBER_SNAPSHOT:
            continue

        if box_id not in historical_data:
            historical_data[box_id] = []
        existing = existing_dates_by_box.setdefault(box_id, {e.get("date") for e in historical_data[box_id]})

        box_data = DECEMBER_SNAPSHOT[key]
        for entry_date in DECEMBER_DATES:
            if entry_date in existing:
                continue
            entry = {
                "date": entry_date,
                "source": "spreadsheet_import",
                "data_type": "combined",
                "floor_price_usd": box_data["floor_price_usd"],
                "active_listings_count": box_data["active_listings_count"],
                "boxes_sold_today": box_data["boxes_sold_per_day"],
                "boxes_sold_per_day": box_data["boxes_sold_per_day"],
                "timestamp": datetime.now().isoformat(),
            }
            historical_data[box_id].append(entry)
            existing.add(entry_date)
            created_count += 1

    for box_id in historical_data:
        historical_data[box_id].sort(key=lambda x: x.get("date", ""))

    historical_file.parent.mkdir(exist_ok=True)
    with open(historical_file, "w") as f:
        json.dump(historical_data, f, indent=2)

    print(f"Added {created_count} December 2025 entries (dates: {', '.join(DECEMBER_DATES)})")
    return created_count


if __name__ == "__main__":
    add_december_totals()
