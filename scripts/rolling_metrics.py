#!/usr/bin/env python3
"""
Phase 3: Rolling Metrics Computation
-------------------------------------
After Phase 1 (Apify sales) and Phase 2 (Scraper listings) write raw data to DB,
this module computes all derived/rolling metrics from the database.

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

Data source: Database (box_metrics_unified + ebay_box_metrics_daily)
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Data epoch: only count entries from this date forward toward the 30-day gate.
# Earlier entries are kept for lookback (EMAs, floor change) but don't count
# toward data maturity because they used different scraper filters/blending.
DATA_EPOCH = "2026-02-02"


def _get_sync_engine():
    """Get SQLAlchemy sync engine for database queries."""
    from sqlalchemy import create_engine
    from app.config import settings
    url = settings.database_url
    if "+asyncpg" in url:
        url = url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    elif "postgresql://" in url and "+" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600)


def _get_all_box_ids() -> List[str]:
    """Get all booster box IDs from the database."""
    from sqlalchemy import text
    engine = _get_sync_engine()
    with engine.connect() as conn:
        q = text("SELECT id FROM booster_boxes ORDER BY id")
        rows = conn.execute(q).fetchall()
    return [str(r[0]) for r in rows]


def _get_tcg_history(box_id: str) -> List[Dict[str, Any]]:
    """Get TCGplayer historical data from box_metrics_unified."""
    from sqlalchemy import text
    engine = _get_sync_engine()
    with engine.connect() as conn:
        q = text("""
            SELECT metric_date, floor_price_usd, boxes_sold_per_day,
                   active_listings_count, unified_volume_usd, unified_volume_7d_ema,
                   boxes_sold_30d_avg, boxes_added_today, liquidity_score,
                   days_to_20pct_increase, avg_boxes_added_per_day,
                   expected_days_to_sell, floor_price_1d_change_pct
            FROM box_metrics_unified
            WHERE booster_box_id = :bid
            ORDER BY metric_date ASC
        """)
        rows = conn.execute(q, {"bid": box_id}).fetchall()

    entries = []
    for r in rows:
        d = r._mapping if hasattr(r, "_mapping") else dict(r)
        metric_date = d.get("metric_date")
        date_str = metric_date.isoformat() if hasattr(metric_date, "isoformat") else str(metric_date) if metric_date else None
        entries.append({
            "date": date_str,
            "floor_price_usd": float(d["floor_price_usd"]) if d.get("floor_price_usd") is not None else None,
            "boxes_sold_per_day": float(d["boxes_sold_per_day"]) if d.get("boxes_sold_per_day") is not None else None,
            "boxes_sold_today": float(d["boxes_sold_per_day"]) if d.get("boxes_sold_per_day") is not None else None,
            "active_listings_count": int(d["active_listings_count"]) if d.get("active_listings_count") is not None else None,
            "unified_volume_usd": float(d["unified_volume_usd"]) if d.get("unified_volume_usd") is not None else None,
            "boxes_added_today": int(d["boxes_added_today"]) if d.get("boxes_added_today") is not None else None,
        })
    return entries


def _get_ebay_history(box_id: str) -> Dict[str, Dict[str, Any]]:
    """Get eBay historical data from ebay_box_metrics_daily, keyed by date.

    Note: Handles missing columns gracefully (e.g., ebay_active_listings_count
    may not exist if DB migration hasn't been run).
    """
    from sqlalchemy import text
    try:
        engine = _get_sync_engine()
        with engine.connect() as conn:
            # Query only columns that are guaranteed to exist
            # ebay_active_listings_count may not exist in older schemas
            q = text("""
                SELECT metric_date, ebay_sales_count, ebay_volume_usd,
                       ebay_units_sold_count, ebay_listings_added_today
                FROM ebay_box_metrics_daily
                WHERE booster_box_id = :bid
                ORDER BY metric_date ASC
            """)
            rows = conn.execute(q, {"bid": box_id}).fetchall()

        by_date = {}
        for r in rows:
            d = r._mapping if hasattr(r, "_mapping") else dict(r)
            metric_date = d.get("metric_date")
            date_str = metric_date.isoformat() if hasattr(metric_date, "isoformat") else str(metric_date) if metric_date else None
            if date_str:
                by_date[date_str] = {
                    "ebay_sold_today": float(d["ebay_units_sold_count"]) if d.get("ebay_units_sold_count") is not None else 0,
                    "ebay_daily_volume_usd": float(d["ebay_volume_usd"]) if d.get("ebay_volume_usd") is not None else 0,
                    "ebay_active_listings": 0,  # Not available until DB migration adds column
                    "ebay_boxes_added_today": int(d["ebay_listings_added_today"]) if d.get("ebay_listings_added_today") is not None else 0,
                }
        return by_date
    except Exception as e:
        logger.warning(f"Failed to get eBay history for {box_id}: {e}")
        return {}


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
    Reads from database, computes metrics, writes back to database.

    Args:
        target_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Summary dict with counts of boxes updated, skipped, etc.
    """
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Phase 3: Computing rolling metrics for {target_date}")

    # Get all box IDs from database
    box_ids = _get_all_box_ids()
    logger.info(f"Found {len(box_ids)} boxes in database")

    updated = 0
    skipped = 0
    db_updated = 0

    for box_id in box_ids:
        # Get TCGplayer history from DB
        tcg_entries = _get_tcg_history(box_id)
        if not tcg_entries:
            skipped += 1
            continue

        # Get eBay history from DB (keyed by date for easy lookup)
        ebay_by_date = _get_ebay_history(box_id)

        # Merge eBay data into TCG entries
        for entry in tcg_entries:
            date_str = entry.get("date")
            if date_str and date_str in ebay_by_date:
                entry.update(ebay_by_date[date_str])
            else:
                # Set eBay fields to 0 if no data for this date
                entry.setdefault("ebay_sold_today", 0)
                entry.setdefault("ebay_daily_volume_usd", 0)
                entry.setdefault("ebay_active_listings", 0)
                entry.setdefault("ebay_boxes_added_today", 0)

        sorted_ents = _sorted_entries(tcg_entries)
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

        # Count unique data days from DATA_EPOCH forward
        data_days = len(set(
            e.get("date") for e in history
            if e.get("date") and e.get("date") >= DATA_EPOCH
            and (e.get("floor_price_usd") or e.get("boxes_sold_per_day"))
        ))
        has_30d_data = data_days >= 30
        days_until_30d = max(0, 30 - data_days)

        # ── Helper: combined boxes added (TCGplayer + eBay) ───────────
        def _get_combined_added(e):
            return (e.get("boxes_added_today") or 0) + (e.get("ebay_boxes_added_today") or 0)

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
        avg_boxes_added_per_day = avg_boxes_added if has_30d_data else None

        # ── 2. boxes_added_7d_ema (alpha=0.25) ───────────────────────
        ba_all = [
            _get_combined_added(e)
            for e in history
            if e.get("boxes_added_today") is not None or e.get("ebay_boxes_added_today") is not None
        ]
        boxes_added_7d_ema = round(_ema(ba_all, 0.25), 2) if ba_all else None

        # ── 3. boxes_added_30d_ema (alpha=0.065) ─────────────────────
        boxes_added_30d_ema = round(_ema(ba_all, 0.065), 2) if ba_all and has_30d_data else None

        # ── 4. floor_price_1d_change_pct ──────────────────────────────
        fp_today = target_entry.get("floor_price_usd")
        fp_prev = prev_entry.get("floor_price_usd") if prev_entry else None
        floor_price_1d_change_pct = None
        if fp_today and fp_prev and fp_prev > 0:
            floor_price_1d_change_pct = round(((fp_today - fp_prev) / fp_prev) * 100, 2)

        # ── 5. floor_price_30d_change_pct ─────────────────────────────
        fp_30d = entry_30d_ago.get("floor_price_usd") if entry_30d_ago else None
        floor_price_30d_change_pct = None
        if fp_today and fp_30d and fp_30d > 0:
            floor_price_30d_change_pct = round(((fp_today - fp_30d) / fp_30d) * 100, 2)

        # ── Shared inputs for metrics 6-8 ─────────────────────────────
        tcg_active = target_entry.get("active_listings_count") or 0
        ebay_active = target_entry.get("ebay_active_listings") or 0
        active_listings = tcg_active + ebay_active

        # 30-day average sales from daily entries
        sold_vals = [
            float(e.get("boxes_sold_per_day") or e.get("boxes_sold_today") or 0)
            + float(e.get("ebay_sold_today") or 0)
            for e in recent_30
        ]
        sold_30d_avg_raw = (
            round(sum(sold_vals) / len(sold_vals), 2) if sold_vals else None
        )
        # Gate behind 30 days of data
        boxes_sold_30d_avg = sold_30d_avg_raw if has_30d_data else None

        # avg_added for internal use
        avg_added = avg_boxes_added or 0

        # ── 7. days_to_20pct_increase (needs 30d data) ──────────────
        days_to_20pct_increase = None
        if has_30d_data and sold_30d_avg_raw and sold_30d_avg_raw > 0 and active_listings > 0:
            net_burn = sold_30d_avg_raw - avg_added
            if net_burn > 0.05:
                d20 = round(active_listings / net_burn, 2)
                days_to_20pct_increase = min(d20, 180.0)
            elif net_burn <= 0:
                days_to_20pct_increase = None
            else:
                days_to_20pct_increase = 180.0

        # ── 8. expected_time_to_sale_days ──────────────────────────────
        tcg_sales = float(
            target_entry.get("boxes_sold_per_day")
            or target_entry.get("boxes_sold_today")
            or sold_30d_avg_raw
            or 0
        )
        ebay_sales = float(target_entry.get("ebay_sold_today") or 0)
        sales_per_day = tcg_sales + ebay_sales

        # Use active_listings as supply proxy
        supply = active_listings
        expected_time_to_sale_days = None
        if supply and supply > 0 and sales_per_day and sales_per_day > 0:
            net_burn = sales_per_day - avg_added
            if net_burn > 0.05:
                raw_days = supply / net_burn
                expected_time_to_sale_days = round(max(1.0, min(365.0, raw_days)), 2)

        # ── 6b. liquidity_label (from expected_time_to_sale_days) ────
        liquidity_label = None
        if expected_time_to_sale_days is not None:
            if expected_time_to_sale_days < 5:
                liquidity_label = "High"
            elif expected_time_to_sale_days <= 15:
                liquidity_label = "Medium"
            else:
                liquidity_label = "Low"

        # ── 9. Volume metrics ────────────────────────────────────────
        def _get_daily_vol(e):
            """Blended daily volume: TCGplayer + eBay (additive)."""
            sold = e.get("boxes_sold_today") or e.get("boxes_sold_per_day") or 0
            price = e.get("floor_price_usd") or 0
            sold = float(sold) if sold else 0
            price = float(price) if price else 0
            tcg_vol = sold * price
            ebay_vol = float(e.get("ebay_daily_volume_usd") or 0)
            return tcg_vol + ebay_vol

        # 7-day rolling volume
        cutoff_7d = (target_dt - timedelta(days=7)).strftime("%Y-%m-%d")
        entries_7d = [e for e in history if (e.get("date") or "") > cutoff_7d]
        vol_7d = sum(_get_daily_vol(e) for e in entries_7d)
        volume_7d = round(vol_7d, 2) if vol_7d > 0 else None

        # 30-day rolling volume
        entries_30d = [e for e in history if (e.get("date") or "") > cutoff_30d]
        vol_30d = sum(_get_daily_vol(e) for e in entries_30d)
        unified_volume_usd = round(vol_30d, 2) if vol_30d > 0 else None

        # Volume 7d EMA (smoothed trend)
        daily_vols = [_get_daily_vol(e) for e in history]
        daily_vols = [v for v in daily_vols if v > 0]
        unified_volume_7d_ema = round(_ema(daily_vols, 0.3), 2) if daily_vols else None

        updated += 1

        # ── Write computed metrics to DB ──────────────────────────────
        try:
            from app.services.box_metrics_writer import upsert_daily_metrics

            ok = upsert_daily_metrics(
                booster_box_id=box_id,
                metric_date=target_date,
                floor_price_usd=target_entry.get("floor_price_usd"),
                boxes_sold_per_day=target_entry.get("boxes_sold_per_day"),
                active_listings_count=target_entry.get("active_listings_count"),
                unified_volume_usd=unified_volume_usd,
                unified_volume_7d_ema=unified_volume_7d_ema,
                boxes_sold_30d_avg=boxes_sold_30d_avg,
                boxes_added_today=target_entry.get("boxes_added_today"),
                liquidity_score=None,  # Deprecated, use liquidity_label
                days_to_20pct_increase=days_to_20pct_increase,
                avg_boxes_added_per_day=avg_boxes_added_per_day,
                expected_days_to_sell=expected_time_to_sale_days,
                floor_price_1d_change_pct=floor_price_1d_change_pct,
            )
            if ok:
                db_updated += 1
        except Exception as e:
            logger.warning(f"DB write failed for {box_id}: {e}")

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
