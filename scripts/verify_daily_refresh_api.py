#!/usr/bin/env python3
"""
Verify daily refresh data via the API (leaderboard + one box detail).
Run after a daily refresh to confirm metrics are updated and returned correctly.

Usage:
  export BACKEND_URL="https://your-api.run.app"   # or http://localhost:8000
  python scripts/verify_daily_refresh_api.py

Optional: BACKEND_URL defaults to http://localhost:8000 if not set.
"""

import os
import sys
from pathlib import Path

# Project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def main():
    base = (os.environ.get("BACKEND_URL") or "http://localhost:8000").rstrip("/")
    try:
        import urllib.request
        # Leaderboard (limit=3)
        req = urllib.request.Request(f"{base}/booster-boxes?limit=3")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode()
    except Exception as e:
        print(f"❌ Could not fetch leaderboard: {e}")
        print("   Set BACKEND_URL if your API is not at http://localhost:8000")
        return 1

    try:
        import json
        leaderboard = json.loads(data)
    except Exception as e:
        print(f"❌ Invalid JSON from leaderboard: {e}")
        return 1

    boxes = leaderboard.get("data") or []
    if not boxes:
        print("⚠️  Leaderboard returned no boxes.")
        return 0

    print("=" * 60)
    print("📊 Leaderboard (first 3 boxes) – key metrics")
    print("=" * 60)
    for b in boxes[:3]:
        name = (b.get("product_name") or "?")[:45]
        m = b.get("metrics") or {}
        fp = m.get("floor_price_usd")
        alc = m.get("active_listings_count")
        sold = m.get("boxes_sold_30d_avg") or m.get("boxes_sold_per_day")
        vol = m.get("unified_volume_usd") or m.get("daily_volume_usd")
        added = m.get("boxes_added_today")
        print(f"\n  {name}")
        print(f"    floor_price_usd: {fp}")
        print(f"    active_listings_count: {alc}")
        print(f"    boxes_sold_30d_avg / boxes_sold_per_day: {sold}")
        print(f"    unified_volume_usd / daily_volume_usd: {vol}")
        print(f"    boxes_added_today: {added}")

    # Fetch first box detail
    first_id = boxes[0].get("id")
    if not first_id:
        print("\n⚠️  No box id for detail request.")
        return 0

    try:
        req2 = urllib.request.Request(f"{base}/booster-boxes/{first_id}")
        req2.add_header("Accept", "application/json")
        with urllib.request.urlopen(req2, timeout=15) as resp2:
            detail = json.loads(resp2.read().decode())
    except Exception as e:
        print(f"\n❌ Could not fetch box detail: {e}")
        return 1

    d = detail.get("data") or {}
    m = d.get("metrics") or {}
    print("\n" + "=" * 60)
    print(f"📦 Box detail (first box) – metrics")
    print("=" * 60)
    print(f"  product_name: {d.get('product_name')}")
    print(f"  floor_price_usd: {m.get('floor_price_usd')}")
    print(f"  active_listings_count: {m.get('active_listings_count')}")
    print(f"  boxes_sold_per_day: {m.get('boxes_sold_per_day')}")
    print(f"  boxes_sold_30d_avg: {m.get('boxes_sold_30d_avg')}")
    print(f"  boxes_added_today: {m.get('boxes_added_today')}")
    print(f"  avg_boxes_added_per_day: {m.get('avg_boxes_added_per_day')}")
    print(f"  daily_volume_usd: {m.get('daily_volume_usd')}")
    print(f"  unified_volume_usd: {m.get('unified_volume_usd')}")
    print("=" * 60)
    print("If these match what you expect after a daily refresh, the pipeline is accurate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
