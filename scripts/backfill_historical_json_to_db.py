#!/usr/bin/env python3
"""
Backfill historical_entries.json into box_metrics_unified so the app can read
from DB instead of JSON. Run once after deploying the DB-backed historical reader.

- Resolves leaderboard UUIDs to DB booster_box_id via LEADERBOARD_TO_DB_UUID_MAP.
- Upserts (booster_box_id, metric_date) so existing DB rows are updated.
- Only inserts for booster_box_id that exist in booster_boxes (no new boxes created).

Usage (from repo root, with venv active):
  python scripts/backfill_historical_json_to_db.py

Safe to run multiple times; conflicts update existing rows.
"""

import json
import sys
from pathlib import Path

# add project root so app imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.historical_data import LEADERBOARD_TO_DB_UUID_MAP
from app.services.db_historical_reader import _get_sync_engine
from sqlalchemy import text


def run():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    hist_path = data_dir / "historical_entries.json"
    if not hist_path.exists():
        print("historical_entries.json not found, nothing to backfill", flush=True)
        return 0

    print("Loading historical_entries.json...", flush=True)
    with open(hist_path, "r") as f:
        data = json.load(f)
    total_entries = sum(len(entries) for entries in data.values())
    print(f"Found {len(data)} boxes, {total_entries} entries. Connecting to DB...", flush=True)

    q = text("""
        INSERT INTO box_metrics_unified (
            booster_box_id, metric_date, floor_price_usd,
            boxes_sold_per_day, active_listings_count,
            unified_volume_usd, unified_volume_7d_ema,
            boxes_sold_30d_avg, boxes_added_today
        ) VALUES (
            CAST(:bid AS uuid), CAST(:md AS date), :fp, :bspd, :alc, :uvu, :uv7, :bs30, :bat
        )
        ON CONFLICT (booster_box_id, metric_date)
        DO UPDATE SET
            floor_price_usd = COALESCE(EXCLUDED.floor_price_usd, box_metrics_unified.floor_price_usd),
            boxes_sold_per_day = COALESCE(EXCLUDED.boxes_sold_per_day, box_metrics_unified.boxes_sold_per_day),
            active_listings_count = COALESCE(EXCLUDED.active_listings_count, box_metrics_unified.active_listings_count),
            unified_volume_usd = COALESCE(EXCLUDED.unified_volume_usd, box_metrics_unified.unified_volume_usd),
            unified_volume_7d_ema = COALESCE(EXCLUDED.unified_volume_7d_ema, box_metrics_unified.unified_volume_7d_ema),
            boxes_sold_30d_avg = COALESCE(EXCLUDED.boxes_sold_30d_avg, box_metrics_unified.boxes_sold_30d_avg),
            boxes_added_today = COALESCE(EXCLUDED.boxes_added_today, box_metrics_unified.boxes_added_today),
            updated_at = NOW()
    """)

    engine = _get_sync_engine()
    upserted, skipped = 0, 0
    done = 0

    with engine.connect() as conn:
        for box_id, entries in data.items():
            booster_box_id = LEADERBOARD_TO_DB_UUID_MAP.get(box_id, box_id)
            if not entries:
                continue
            for e in entries:
                date_val = e.get("date")
                if not date_val:
                    skipped += 1
                    done += 1
                    continue
                floor_price_usd = e.get("floor_price_usd")
                boxes_sold_per_day = e.get("boxes_sold_per_day") or e.get("boxes_sold_today")
                active_listings_count = e.get("active_listings_count")
                unified_volume_usd = e.get("unified_volume_usd")
                unified_volume_7d_ema = e.get("unified_volume_7d_ema")
                daily_volume_usd = e.get("daily_volume_usd")
                if unified_volume_usd is None and daily_volume_usd is not None:
                    unified_volume_usd = daily_volume_usd * 30
                boxes_sold_30d_avg = e.get("boxes_sold_30d_avg")
                boxes_added_today = e.get("boxes_added_today")

                try:
                    with conn.begin():
                        conn.execute(q, {
                            "bid": booster_box_id,
                            "md": date_val,
                            "fp": floor_price_usd,
                            "bspd": boxes_sold_per_day,
                            "alc": active_listings_count,
                            "uvu": unified_volume_usd,
                            "uv7": unified_volume_7d_ema,
                            "bs30": boxes_sold_30d_avg,
                            "bat": boxes_added_today,
                        })
                    upserted += 1
                except Exception as ex:
                    if "foreign key" in str(ex).lower() or "booster_boxes" in str(ex).lower() or "violates" in str(ex).lower():
                        skipped += 1
                    else:
                        raise
                done += 1
                if done % 500 == 0:
                    print(f"  ... processed {done} / {total_entries} (upserted={upserted}, skipped={skipped})", flush=True)

    print(f"Backfill done: upserted={upserted}, skipped={skipped}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
