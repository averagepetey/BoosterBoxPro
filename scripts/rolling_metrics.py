#!/usr/bin/env python3
"""
Phase 3: Rolling Metrics Computation
-------------------------------------
After Phase 1 (Apify sales) and Phase 2 (Scraper listings) write raw data,
this module computes all derived/rolling metrics and stores them in the JSON entry.

Run standalone:  python scripts/rolling_metrics.py [--date 2026-01-30]
Called by daily_refresh.py after Phase 2.

Metrics computed for each box's target-date entry:
  1. avg_boxes_added_per_day      – 30-day simple average of boxes_added_today
  2. boxes_added_7d_ema           – EMA alpha=0.25 on boxes_added_today
  3. boxes_added_30d_ema          – EMA alpha=0.065 on boxes_added_today
  4. floor_price_1d_change_pct    – (today - yesterday) / yesterday × 100
  5. floor_price_30d_change_pct   – (today - 30d ago) / 30d ago × 100
  6. liquidity_score              – (sold_30d_avg / active_listings) × 100, cap 10
  7. days_to_20pct_increase       – active_listings / (avg_sales - avg_added), cap 180
  8. expected_time_to_sale_days   – supply_10pct / (sales/day - avg_added), cap [1, 365]
  9. unified_volume_7d_ema        – EMA alpha=0.3 on unified_volume_usd (or daily_volume_usd × 30)
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

HISTORICAL_FILE = project_root / "data" / "historical_entries.json"


def _load_json() -> dict:
    with open(HISTORICAL_FILE, "r") as f:
        return json.load(f)


def _save_json(data: dict) -> None:
    with open(HISTORICAL_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_entry_for_date(entries: list, date_str: str) -> dict | None:
    for e in entries:
        if e.get("date") == date_str:
            return e
    return None


def _sorted_entries(entries: list) -> list:
    return sorted(entries, key=lambda x: x.get("date", ""))


def _ema(values: list[float], alpha: float) -> float | None:
    """Compute EMA over a list of values (oldest first). Returns final EMA value."""
    if not values:
        return None
    ema_val = values[0]
    for v in values[1:]:
        ema_val = alpha * v + (1 - alpha) * ema_val
    return ema_val


def compute_rolling_metrics(target_date: str | None = None) -> dict:
    """
    Compute all derived metrics for each box's entry on target_date.

    Args:
        target_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Summary dict with counts of boxes updated, skipped, etc.
    """
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Phase 3: Computing rolling metrics for {target_date}")

    data = _load_json()
    updated = 0
    skipped = 0

    for box_id, entries in data.items():
        sorted_ents = _sorted_entries(entries)
        target_entry = _get_entry_for_date(sorted_ents, target_date)
        if target_entry is None:
            skipped += 1
            continue

        # Get index of target entry in sorted list for lookback
        target_idx = None
        for i, e in enumerate(sorted_ents):
            if e.get("date") == target_date:
                target_idx = i
                break
        if target_idx is None:
            skipped += 1
            continue

        # ── Gather lookback data ──────────────────────────────────────
        # Entries up to and including target_date (for EMA / averages)
        history = sorted_ents[: target_idx + 1]

        # Previous entry (yesterday or most recent before target)
        prev_entry = sorted_ents[target_idx - 1] if target_idx > 0 else None

        # Entry ~30 days ago
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        cutoff_30d = (target_dt - timedelta(days=30)).strftime("%Y-%m-%d")
        entry_30d_ago = None
        for e in reversed(sorted_ents[:target_idx]):
            if e.get("date", "") <= cutoff_30d:
                entry_30d_ago = e
                break

        # Last 30 entries (or fewer) for rolling averages
        recent_30 = history[-30:] if len(history) >= 30 else history

        # ── 1. avg_boxes_added_per_day (30-day simple avg) ────────────
        boxes_added_vals = [
            e.get("boxes_added_today", 0) or 0
            for e in recent_30
            if e.get("boxes_added_today") is not None
        ]
        avg_boxes_added = (
            round(sum(boxes_added_vals) / len(boxes_added_vals), 2)
            if boxes_added_vals
            else None
        )
        target_entry["avg_boxes_added_per_day"] = avg_boxes_added

        # ── 2. boxes_added_7d_ema (alpha=0.25) ───────────────────────
        ba_all = [
            e.get("boxes_added_today", 0) or 0
            for e in history
            if e.get("boxes_added_today") is not None
        ]
        ba_7d_ema = round(_ema(ba_all, 0.25), 2) if ba_all else None
        target_entry["boxes_added_7d_ema"] = ba_7d_ema

        # ── 3. boxes_added_30d_ema (alpha=0.065) ─────────────────────
        ba_30d_ema = round(_ema(ba_all, 0.065), 2) if ba_all else None
        target_entry["boxes_added_30d_ema"] = ba_30d_ema

        # ── 4. floor_price_1d_change_pct ──────────────────────────────
        fp_today = target_entry.get("floor_price_usd")
        fp_prev = prev_entry.get("floor_price_usd") if prev_entry else None
        if fp_today and fp_prev and fp_prev > 0:
            target_entry["floor_price_1d_change_pct"] = round(
                ((fp_today - fp_prev) / fp_prev) * 100, 2
            )
        else:
            target_entry.setdefault("floor_price_1d_change_pct", None)

        # ── 5. floor_price_30d_change_pct ─────────────────────────────
        fp_30d = entry_30d_ago.get("floor_price_usd") if entry_30d_ago else None
        if fp_today and fp_30d and fp_30d > 0:
            target_entry["floor_price_30d_change_pct"] = round(
                ((fp_today - fp_30d) / fp_30d) * 100, 2
            )
        else:
            target_entry.setdefault("floor_price_30d_change_pct", None)

        # ── Shared inputs for metrics 6-8 ─────────────────────────────
        active_listings = target_entry.get("active_listings_count") or 0
        supply_10pct = target_entry.get("listings_within_10pct_floor")
        supply = supply_10pct if supply_10pct and supply_10pct > 0 else active_listings

        # 30-day average sales
        sold_vals = [
            float(e.get("boxes_sold_per_day") or e.get("boxes_sold_today") or 0)
            for e in recent_30
        ]
        sold_30d_avg = (
            round(sum(sold_vals) / len(sold_vals), 2) if sold_vals else None
        )
        # Also store boxes_sold_30d_avg for DB/display
        target_entry["boxes_sold_30d_avg"] = sold_30d_avg

        avg_added = avg_boxes_added or 0

        # ── 6. liquidity_score ────────────────────────────────────────
        if sold_30d_avg and sold_30d_avg > 0 and active_listings and active_listings > 0:
            raw_score = (sold_30d_avg / active_listings) * 100
            target_entry["liquidity_score"] = round(min(raw_score, 10.0), 1)
        elif sold_30d_avg and sold_30d_avg > 0:
            target_entry["liquidity_score"] = 5.0
        else:
            target_entry.setdefault("liquidity_score", None)

        # ── 7. days_to_20pct_increase ─────────────────────────────────
        if sold_30d_avg and sold_30d_avg > 0 and active_listings and active_listings > 0:
            net_burn = sold_30d_avg - avg_added
            if net_burn > 0.05:
                d20 = round(active_listings / net_burn, 2)
                target_entry["days_to_20pct_increase"] = min(d20, 180.0)
            elif net_burn <= 0:
                target_entry["days_to_20pct_increase"] = None
            else:
                target_entry["days_to_20pct_increase"] = 180.0
        else:
            target_entry.setdefault("days_to_20pct_increase", None)

        # ── 8. expected_time_to_sale_days ─────────────────────────────
        sales_per_day = (
            target_entry.get("boxes_sold_per_day")
            or target_entry.get("boxes_sold_today")
            or sold_30d_avg
            or 0
        )
        if supply and supply > 0 and sales_per_day and sales_per_day > 0:
            net_burn = sales_per_day - avg_added
            if net_burn > 0.05:
                raw_days = supply / net_burn
                target_entry["expected_time_to_sale_days"] = round(
                    max(1.0, min(365.0, raw_days)), 2
                )
            else:
                target_entry["expected_time_to_sale_days"] = None
        else:
            target_entry.setdefault("expected_time_to_sale_days", None)

        # ── 9. unified_volume_7d_ema (alpha=0.3) ─────────────────────
        vol_values = []
        for e in history:
            vol = e.get("unified_volume_usd")
            if vol is None:
                daily = e.get("daily_volume_usd")
                if daily and daily > 0:
                    vol = daily * 30
            if vol is not None and vol > 0:
                vol_values.append(float(vol))
        uv7_ema = round(_ema(vol_values, 0.3), 2) if vol_values else None
        target_entry["unified_volume_7d_ema"] = uv7_ema

        updated += 1

    _save_json(data)

    # Write Phase 3 metrics to DB
    db_updated = 0
    try:
        from app.services.box_metrics_writer import upsert_daily_metrics
        from app.services.historical_data import DB_TO_LEADERBOARD_UUID_MAP

        for box_id, entries in data.items():
            entry = _get_entry_for_date(entries, target_date)
            if entry is None:
                continue
            booster_box_id = DB_TO_LEADERBOARD_UUID_MAP.get(box_id, box_id)
            ok = upsert_daily_metrics(
                booster_box_id=booster_box_id,
                metric_date=target_date,
                floor_price_usd=entry.get("floor_price_usd"),
                boxes_sold_per_day=entry.get("boxes_sold_per_day"),
                active_listings_count=entry.get("active_listings_count"),
                unified_volume_usd=entry.get("unified_volume_usd"),
                unified_volume_7d_ema=entry.get("unified_volume_7d_ema"),
                boxes_sold_30d_avg=entry.get("boxes_sold_30d_avg"),
                boxes_added_today=entry.get("boxes_added_today"),
                liquidity_score=entry.get("liquidity_score"),
                days_to_20pct_increase=entry.get("days_to_20pct_increase"),
                avg_boxes_added_per_day=entry.get("avg_boxes_added_per_day"),
                expected_days_to_sell=entry.get("expected_time_to_sale_days"),
                floor_price_1d_change_pct=entry.get("floor_price_1d_change_pct"),
            )
            if ok:
                db_updated += 1
    except Exception as e:
        logger.warning(f"Phase 3 DB write failed (non-fatal): {e}")

    summary = {
        "target_date": target_date,
        "boxes_updated": updated,
        "boxes_skipped": skipped,
        "db_updated": db_updated,
    }
    logger.info(f"Phase 3 complete: {updated} boxes updated, {skipped} skipped, {db_updated} DB rows upserted")
    return summary


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    parser = argparse.ArgumentParser(description="Phase 3: Rolling Metrics Computation")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date (YYYY-MM-DD). Defaults to today.",
    )
    args = parser.parse_args()

    result = compute_rolling_metrics(target_date=args.date)
    print(json.dumps(result, indent=2))
