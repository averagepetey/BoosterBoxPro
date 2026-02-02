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

# Data epoch: only count entries from this date forward toward the 30-day gate.
# Earlier entries are kept for lookback (EMAs, floor change) but don't count
# toward data maturity because they used different scraper filters/blending.
DATA_EPOCH = "2026-02-02"


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

        # Count unique data days from DATA_EPOCH forward (earlier entries used
        # different scraper filters and don't count toward data maturity)
        data_days = len(set(
            e.get("date") for e in history
            if e.get("date") and e.get("date") >= DATA_EPOCH
            and (e.get("floor_price_usd") or e.get("boxes_sold_per_day"))
        ))
        has_30d_data = data_days >= 30
        days_until_30d = max(0, 30 - data_days)
        target_entry["data_days_collected"] = data_days
        target_entry["days_until_30d_metrics"] = days_until_30d

        # ── Helper: combined boxes added (TCGplayer + eBay) ───────────
        def _get_combined_added(e):
            return (e.get("boxes_added_today") or 0) + (e.get("ebay_boxes_added_today") or 0)

        # Store combined value on target entry
        target_entry["combined_boxes_added_today"] = _get_combined_added(target_entry)

        # ── 1. avg_boxes_added_per_day (30-day simple avg) ────────────
        boxes_added_vals = [
            _get_combined_added(e)
            for e in recent_30
            if e.get("boxes_added_today") is not None or e.get("ebay_boxes_added_today") is not None
        ]
        avg_boxes_added = (
            round(sum(boxes_added_vals) / len(boxes_added_vals), 2)
            if boxes_added_vals
            else None
        )
        # Gate behind 30 days of data
        target_entry["avg_boxes_added_per_day"] = avg_boxes_added if has_30d_data else None

        # ── 2. boxes_added_7d_ema (alpha=0.25) ───────────────────────
        ba_all = [
            _get_combined_added(e)
            for e in history
            if e.get("boxes_added_today") is not None or e.get("ebay_boxes_added_today") is not None
        ]
        ba_7d_ema = round(_ema(ba_all, 0.25), 2) if ba_all else None
        target_entry["boxes_added_7d_ema"] = ba_7d_ema

        # ── 3. boxes_added_30d_ema (alpha=0.065) ─────────────────────
        ba_30d_ema = round(_ema(ba_all, 0.065), 2) if ba_all else None
        target_entry["boxes_added_30d_ema"] = ba_30d_ema if has_30d_data else None

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
        tcg_active = target_entry.get("active_listings_count") or 0
        ebay_active = target_entry.get("ebay_active_listings") or 0
        active_listings = tcg_active + ebay_active
        target_entry["combined_active_listings"] = active_listings

        supply_10pct = target_entry.get("listings_within_10pct_floor") or 0
        ebay_10pct = target_entry.get("ebay_listings_within_10pct_floor") or 0
        supply = (supply_10pct + ebay_10pct) if (supply_10pct + ebay_10pct) > 0 else active_listings

        # 30-day average sales from daily entries
        # boxes_sold_per_day = 28-day avg from weekly buckets (most reliable)
        # boxes_sold_today = most recent week's daily rate (more responsive)
        sold_vals = [
            float(e.get("boxes_sold_per_day") or e.get("boxes_sold_today") or 0)
            + float(e.get("ebay_sold_today") or 0)
            for e in recent_30
        ]
        sold_30d_avg_raw = (
            round(sum(sold_vals) / len(sold_vals), 2) if sold_vals else None
        )
        # Gate behind 30 days of data
        target_entry["boxes_sold_30d_avg"] = sold_30d_avg_raw if has_30d_data else None

        # avg_added for internal use (use raw value even pre-30d for time-to-sale calc)
        avg_added = avg_boxes_added or 0

        # ── 6. liquidity_label ──────────────────────────────────────
        # Derived from expected_time_to_sale_days (computed below)
        # Stored after metric 8

        # ── 7. days_to_20pct_increase (needs 30d data) ──────────────
        if has_30d_data and sold_30d_avg_raw and sold_30d_avg_raw > 0 and active_listings and active_listings > 0:
            net_burn = sold_30d_avg_raw - avg_added
            if net_burn > 0.05:
                d20 = round(active_listings / net_burn, 2)
                target_entry["days_to_20pct_increase"] = min(d20, 180.0)
            elif net_burn <= 0:
                target_entry["days_to_20pct_increase"] = None
            else:
                target_entry["days_to_20pct_increase"] = 180.0
        else:
            target_entry["days_to_20pct_increase"] = None

        # ── 8. expected_time_to_sale_days (shows immediately with daily data) ──
        tcg_sales = float(
            target_entry.get("boxes_sold_per_day")
            or target_entry.get("boxes_sold_today")
            or sold_30d_avg_raw
            or 0
        )
        ebay_sales = float(target_entry.get("ebay_sold_today") or 0)
        sales_per_day = tcg_sales + ebay_sales
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

        # ── 6b. liquidity_label (from expected_time_to_sale_days) ────
        ets = target_entry.get("expected_time_to_sale_days")
        if ets is not None:
            if ets < 5:
                target_entry["liquidity_label"] = "High"
            elif ets <= 15:
                target_entry["liquidity_label"] = "Medium"
            else:
                target_entry["liquidity_label"] = "Low"
        else:
            target_entry["liquidity_label"] = None
        # Keep numeric score for backward compat / DB but null when gated
        target_entry["liquidity_score"] = None

        # ── 9. Volume metrics (built from our own daily data) ────────
        # Daily volume = (TCGplayer sold × price) + eBay daily volume
        # Then sum over 7d and 30d windows for rolling totals
        def _get_daily_vol(e):
            """Blended daily volume: TCGplayer + eBay (additive)."""
            sold = e.get("boxes_sold_today") or e.get("boxes_sold_per_day") or 0
            price = e.get("market_price_usd") or e.get("floor_price_usd") or 0
            sold = float(sold) if sold else 0
            price = float(price) if price else 0
            tcg_vol = sold * price
            ebay_vol = float(e.get("ebay_daily_volume_usd") or 0)
            return tcg_vol + ebay_vol

        # Compute and store today's daily volume (blended TCG + eBay)
        today_vol = _get_daily_vol(target_entry)
        target_entry["daily_volume_usd"] = round(today_vol, 2) if today_vol > 0 else None

        # Store breakdown for transparency
        tcg_sold = float(target_entry.get("boxes_sold_today") or target_entry.get("boxes_sold_per_day") or 0)
        tcg_price = float(target_entry.get("market_price_usd") or target_entry.get("floor_price_usd") or 0)
        tcg_daily_vol = tcg_sold * tcg_price
        ebay_daily_vol = float(target_entry.get("ebay_daily_volume_usd") or 0)
        target_entry["daily_volume_tcg_usd"] = round(tcg_daily_vol, 2) if tcg_daily_vol > 0 else None
        target_entry["daily_volume_ebay_usd"] = round(ebay_daily_vol, 2) if ebay_daily_vol > 0 else None

        # Combined boxes sold (TCG + eBay)
        ebay_sold_today = float(target_entry.get("ebay_sold_today") or 0)
        if ebay_sold_today > 0:
            target_entry["combined_boxes_sold_today"] = round(tcg_sold + ebay_sold_today, 2)
        else:
            target_entry["combined_boxes_sold_today"] = None

        # 7-day rolling volume: sum daily volumes from last 7 entries
        target_dt_obj = datetime.strptime(target_date, "%Y-%m-%d")
        cutoff_7d = (target_dt_obj - timedelta(days=7)).strftime("%Y-%m-%d")
        entries_7d = [e for e in history if (e.get("date") or "") > cutoff_7d]
        vol_7d = sum(_get_daily_vol(e) for e in entries_7d)
        target_entry["volume_7d"] = round(vol_7d, 2) if vol_7d > 0 else None

        # 30-day rolling volume: sum daily volumes from last 30 entries
        entries_30d = [e for e in history if (e.get("date") or "") > cutoff_30d]
        vol_30d = sum(_get_daily_vol(e) for e in entries_30d)
        target_entry["unified_volume_usd"] = round(vol_30d, 2) if vol_30d > 0 else None

        # Volume 7d EMA (smoothed trend)
        daily_vols = [_get_daily_vol(e) for e in history]
        daily_vols = [v for v in daily_vols if v > 0]
        uv7_ema = round(_ema(daily_vols, 0.3), 2) if daily_vols else None
        target_entry["unified_volume_7d_ema"] = uv7_ema

        updated += 1

    _save_json(data)

    # Write Phase 3 metrics to DB
    db_updated = 0
    try:
        from app.services.box_metrics_writer import upsert_daily_metrics

        for box_id, entries in data.items():
            entry = _get_entry_for_date(entries, target_date)
            if entry is None:
                continue
            # box_id in the JSON IS the DB UUID — use directly, don't remap
            ok = upsert_daily_metrics(
                booster_box_id=box_id,
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
                # New fields passed through for API (stored in JSON, not all have DB columns)
            )
            # Store liquidity_label and days_until_30d in JSON (API reads from JSON cache)
            # These don't need DB columns — they're derived/display fields
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
