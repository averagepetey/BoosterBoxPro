#!/usr/bin/env python3
"""
Phase 3b: Market Index Computation
-----------------------------------
After Phase 3 (rolling_metrics) completes, this module computes the aggregate
BoosterBox Index and market-wide stats from box_metrics_unified.

Run standalone:  python scripts/market_index.py [--date 2026-02-10]
Called by daily_refresh.py after Phase 3.

Metrics computed:
  1. index_value          – equal-weight avg of all floor prices
  2. index_*_change_pct   – compare to stored values 1/7/30 days ago
  3. sentiment            – BULLISH / BEARISH / NEUTRAL
  4. fear_greed_score     – 4-factor score (price, volume, listing, sales)
  5. floors up/down/flat  – count boxes by 1d price direction
  6. biggest gainer/loser – by floor_price_1d_change_pct
  7. volume/supply totals – sums across all boxes
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


def _get_sync_engine():
    """Reuse the shared sync engine from db_historical_reader (single pool)."""
    from app.services.db_historical_reader import _get_sync_engine as _shared_engine
    return _shared_engine()


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def _get_boxes_for_date(target_date: str) -> List[Dict[str, Any]]:
    """Get latest metrics for all boxes on or before target_date."""
    from sqlalchemy import text
    engine = _get_sync_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT DISTINCT ON (bmu.booster_box_id)
                bmu.booster_box_id,
                bmu.metric_date,
                bmu.floor_price_usd,
                bmu.floor_price_1d_change_pct,
                bmu.floor_price_7d_change_pct,
                bmu.daily_volume_usd,
                bmu.unified_volume_usd,
                bmu.unified_volume_7d_ema,
                bmu.boxes_sold_per_day,
                bmu.boxes_sold_30d_avg,
                bmu.active_listings_count,
                bmu.boxes_added_today,
                bmu.liquidity_score,
                bb.product_name
            FROM box_metrics_unified bmu
            JOIN booster_boxes bb ON bb.id = bmu.booster_box_id
            WHERE bmu.metric_date <= CAST(:td AS date)
              AND bb.product_name NOT LIKE '%%(Test)%%'
              AND bb.product_name NOT LIKE '%%Test Box%%'
              AND bb.product_name != 'One Piece - OP-01 Romance Dawn Booster Box'
            ORDER BY bmu.booster_box_id, bmu.metric_date DESC
        """), {"td": target_date}).fetchall()

    result = []
    for r in rows:
        d = r._mapping if hasattr(r, "_mapping") else dict(r)
        result.append({
            "booster_box_id": str(d["booster_box_id"]),
            "metric_date": str(d["metric_date"]),
            "floor_price_usd": float(d["floor_price_usd"]) if d.get("floor_price_usd") is not None else None,
            "floor_price_1d_change_pct": float(d["floor_price_1d_change_pct"]) if d.get("floor_price_1d_change_pct") is not None else None,
            "floor_price_7d_change_pct": float(d["floor_price_7d_change_pct"]) if d.get("floor_price_7d_change_pct") is not None else None,
            "daily_volume_usd": float(d["daily_volume_usd"]) if d.get("daily_volume_usd") is not None else 0,
            "unified_volume_usd": float(d["unified_volume_usd"]) if d.get("unified_volume_usd") is not None else 0,
            "unified_volume_7d_ema": float(d["unified_volume_7d_ema"]) if d.get("unified_volume_7d_ema") is not None else 0,
            "boxes_sold_per_day": float(d["boxes_sold_per_day"]) if d.get("boxes_sold_per_day") is not None else 0,
            "boxes_sold_30d_avg": float(d["boxes_sold_30d_avg"]) if d.get("boxes_sold_30d_avg") is not None else 0,
            "active_listings_count": int(d["active_listings_count"]) if d.get("active_listings_count") is not None else 0,
            "boxes_added_today": int(d["boxes_added_today"]) if d.get("boxes_added_today") is not None else 0,
            "liquidity_score": float(d["liquidity_score"]) if d.get("liquidity_score") is not None else 0,
            "product_name": d.get("product_name", ""),
        })
    return result


def _get_historical_index(date_str: str) -> Optional[float]:
    """Get stored index_value from market_index_daily for a past date."""
    from sqlalchemy import text
    engine = _get_sync_engine()
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT index_value FROM market_index_daily
            WHERE metric_date = CAST(:d AS date)
        """), {"d": date_str}).fetchone()
    if row and row[0] is not None:
        return float(row[0])
    return None


def _get_previous_day_totals(target_date: str):
    """Get previous day's aggregate totals for change calculations."""
    from sqlalchemy import text
    engine = _get_sync_engine()
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    prev_str = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT total_daily_volume_usd, total_active_listings
            FROM market_index_daily
            WHERE metric_date = CAST(:d AS date)
        """), {"d": prev_str}).fetchone()
    if row:
        return {
            "total_daily_volume_usd": float(row[0]) if row[0] is not None else None,
            "total_active_listings": int(row[1]) if row[1] is not None else None,
        }
    return None


def compute_fear_greed(boxes: List[Dict[str, Any]]) -> int:
    """
    4-factor Fear & Greed score (0-100).
    Ported from MarketOverviewBar.tsx computeFearGreedIndex().
    """
    if not boxes:
        return 50

    # 1. Price Momentum (25%): avg floor_price_1d_change_pct, mapped -5% to +5% -> 0-100
    price_changes = [b["floor_price_1d_change_pct"] for b in boxes if b.get("floor_price_1d_change_pct") is not None]
    avg_price_change = sum(price_changes) / len(price_changes) if price_changes else 0
    price_momentum = _clamp((avg_price_change + 5) / 10, 0, 1) * 100

    # 2. Volume Momentum (25%): daily vol sum vs 7d EMA sum, mapped -50% to +50% -> 0-100
    daily_vol_sum = sum(b.get("daily_volume_usd", 0) for b in boxes)
    vol_7d_sum = sum(b.get("unified_volume_7d_ema", 0) for b in boxes)
    # unified_volume_7d_ema is a daily EMA, use as proxy for avg daily
    vol_change_pct = ((daily_vol_sum - vol_7d_sum) / vol_7d_sum * 100) if vol_7d_sum > 0 else 0
    volume_momentum = _clamp((vol_change_pct + 50) / 100, 0, 1) * 100

    # 3. Listing Trend (25%): inverted - more additions = fear
    added_values = [b.get("boxes_added_today", 0) for b in boxes if b.get("boxes_added_today") is not None]
    avg_added = sum(added_values) / len(added_values) if added_values else 0
    listing_trend = _clamp((-avg_added + 5) / 10, 0, 1) * 100

    # 4. Sales Velocity (25%): avg boxes_sold_per_day, mapped 0-3 -> 0-100
    sales_values = [b.get("boxes_sold_per_day", 0) for b in boxes if b.get("boxes_sold_per_day") is not None]
    avg_sales = sum(sales_values) / len(sales_values) if sales_values else 0
    sales_velocity = _clamp(avg_sales / 3, 0, 1) * 100

    score = (price_momentum * 0.25) + (volume_momentum * 0.25) + (listing_trend * 0.25) + (sales_velocity * 0.25)
    return round(_clamp(score, 0, 100))


def compute_market_index(target_date: str | None = None) -> dict:
    """
    Compute market-wide aggregate metrics for target_date and upsert to DB.

    Returns summary dict with computed values.
    """
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    logger.info(f"Phase 3b: Computing market index for {target_date}")

    boxes = _get_boxes_for_date(target_date)
    if not boxes:
        logger.warning("No box data found for market index computation")
        return {"target_date": target_date, "status": "no_data"}

    logger.info(f"Found {len(boxes)} boxes for market index")

    # ── Index value: sum of all floor prices ──────────
    floor_prices = [b["floor_price_usd"] for b in boxes if b.get("floor_price_usd") is not None and b["floor_price_usd"] > 0]
    index_value = round(sum(floor_prices), 2) if floor_prices else None

    # ── Change percentages: compare to stored historical values ───
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    index_1d_change_pct = None
    index_7d_change_pct = None
    index_30d_change_pct = None

    if index_value is not None:
        for days_back, attr_name in [(1, "index_1d_change_pct"), (7, "index_7d_change_pct"), (30, "index_30d_change_pct")]:
            past_str = (dt - timedelta(days=days_back)).strftime("%Y-%m-%d")
            past_val = _get_historical_index(past_str)
            if past_val and past_val > 0:
                pct = round(((index_value - past_val) / past_val) * 100, 2)
                if attr_name == "index_1d_change_pct":
                    index_1d_change_pct = pct
                elif attr_name == "index_7d_change_pct":
                    index_7d_change_pct = pct
                else:
                    index_30d_change_pct = pct

    # ── Sentiment ─────────────────────────────────────────────────
    # BULLISH if index_7d > +2% AND volume_7d > 0%
    # BEARISH if index_7d < -2% AND volume_7d < 0%
    # else NEUTRAL
    vol_7d_sum = sum(b.get("unified_volume_usd", 0) for b in boxes)
    prev_totals = _get_previous_day_totals(target_date)
    # Compute volume 7d change from stored historical
    past_7d_str = (dt - timedelta(days=7)).strftime("%Y-%m-%d")
    from sqlalchemy import text as _text
    engine = _get_sync_engine()
    with engine.connect() as conn:
        row = conn.execute(_text("""
            SELECT total_7d_volume_usd FROM market_index_daily
            WHERE metric_date = CAST(:d AS date)
        """), {"d": past_7d_str}).fetchone()
    past_7d_vol = float(row[0]) if row and row[0] is not None else None

    # Current 7d volume
    total_7d_volume_usd = vol_7d_sum  # This is sum of individual box 30d volumes; estimate 7d as daily * 7
    # Better: sum daily_volume_usd across boxes gives today's total
    total_daily_vol = sum(b.get("daily_volume_usd", 0) for b in boxes)

    # For volume trend, use volume_7d_change_pct from individual boxes
    vol_changes = [b.get("floor_price_7d_change_pct") for b in boxes if b.get("floor_price_7d_change_pct") is not None]
    avg_vol_7d_change = sum(vol_changes) / len(vol_changes) if vol_changes else 0

    sentiment = "NEUTRAL"
    if index_7d_change_pct is not None:
        if index_7d_change_pct > 2 and avg_vol_7d_change > 0:
            sentiment = "BULLISH"
        elif index_7d_change_pct < -2 and avg_vol_7d_change < 0:
            sentiment = "BEARISH"

    # ── Fear & Greed ──────────────────────────────────────────────
    fear_greed_score = compute_fear_greed(boxes)

    # ── Price movers ──────────────────────────────────────────────
    floors_up = 0
    floors_down = 0
    floors_flat = 0
    biggest_gainer_id = None
    biggest_gainer_pct = None
    biggest_loser_id = None
    biggest_loser_pct = None

    for b in boxes:
        change = b.get("floor_price_1d_change_pct")
        if change is None:
            floors_flat += 1
            continue
        if change > 0.5:
            floors_up += 1
        elif change < -0.5:
            floors_down += 1
        else:
            floors_flat += 1

        if biggest_gainer_pct is None or (change is not None and change > biggest_gainer_pct):
            biggest_gainer_pct = change
            biggest_gainer_id = b["booster_box_id"]
        if biggest_loser_pct is None or (change is not None and change < biggest_loser_pct):
            biggest_loser_pct = change
            biggest_loser_id = b["booster_box_id"]

    # ── Volume totals ─────────────────────────────────────────────
    total_daily_volume_usd = round(total_daily_vol, 2)
    total_30d_volume_usd = round(sum(b.get("unified_volume_usd", 0) for b in boxes), 2)

    # 7d volume estimate: daily * 7 (approximate since we don't store per-box 7d volume separately)
    total_7d_vol_est = round(total_daily_vol * 7, 2) if total_daily_vol else None

    # Volume change percentages
    volume_1d_change_pct = None
    volume_7d_change_pct_val = None
    if prev_totals and prev_totals.get("total_daily_volume_usd") and prev_totals["total_daily_volume_usd"] > 0:
        volume_1d_change_pct = round(
            ((total_daily_volume_usd - prev_totals["total_daily_volume_usd"]) / prev_totals["total_daily_volume_usd"]) * 100, 2
        )
    if past_7d_vol and past_7d_vol > 0 and total_7d_vol_est:
        volume_7d_change_pct_val = round(((total_7d_vol_est - past_7d_vol) / past_7d_vol) * 100, 2)

    # ── Liquidity & Sales ─────────────────────────────────────────
    liq_scores = [b.get("liquidity_score", 0) for b in boxes if b.get("liquidity_score") is not None and b["liquidity_score"] > 0]
    avg_liquidity = round(sum(liq_scores) / len(liq_scores), 2) if liq_scores else None

    total_boxes_sold = round(sum(b.get("boxes_sold_per_day", 0) for b in boxes), 2)

    # ── Supply ────────────────────────────────────────────────────
    total_active_listings = sum(b.get("active_listings_count", 0) for b in boxes)
    total_boxes_added = sum(b.get("boxes_added_today", 0) for b in boxes)
    net_supply = total_boxes_added - int(total_boxes_sold) if total_boxes_sold else total_boxes_added

    listings_1d_change_val = None
    if prev_totals and prev_totals.get("total_active_listings") is not None:
        listings_1d_change_val = total_active_listings - prev_totals["total_active_listings"]

    # ── Write to DB ───────────────────────────────────────────────
    from app.services.market_index_writer import upsert_market_index

    ok = upsert_market_index(
        metric_date=target_date,
        index_value=index_value,
        index_1d_change_pct=index_1d_change_pct,
        index_7d_change_pct=index_7d_change_pct,
        index_30d_change_pct=index_30d_change_pct,
        sentiment=sentiment,
        fear_greed_score=fear_greed_score,
        floors_up_count=floors_up,
        floors_down_count=floors_down,
        floors_flat_count=floors_flat,
        biggest_gainer_box_id=biggest_gainer_id,
        biggest_gainer_pct=biggest_gainer_pct,
        biggest_loser_box_id=biggest_loser_id,
        biggest_loser_pct=biggest_loser_pct,
        total_daily_volume_usd=total_daily_volume_usd,
        total_7d_volume_usd=total_7d_vol_est,
        total_30d_volume_usd=total_30d_volume_usd,
        volume_1d_change_pct=volume_1d_change_pct,
        volume_7d_change_pct=volume_7d_change_pct_val,
        avg_liquidity_score=avg_liquidity,
        total_boxes_sold_today=total_boxes_sold,
        total_active_listings=total_active_listings,
        total_boxes_added_today=total_boxes_added,
        net_supply_change=net_supply,
        listings_1d_change=listings_1d_change_val,
    )

    summary = {
        "target_date": target_date,
        "index_value": index_value,
        "sentiment": sentiment,
        "fear_greed_score": fear_greed_score,
        "boxes_counted": len(boxes),
        "db_upserted": ok,
    }
    logger.info(f"Phase 3b complete: index={index_value}, sentiment={sentiment}, F&G={fear_greed_score}")
    return summary


if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    parser = argparse.ArgumentParser(description="Phase 3b: Market Index Computation")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Target date (YYYY-MM-DD). Defaults to today.",
    )
    args = parser.parse_args()

    result = compute_market_index(target_date=args.date)
    print(json.dumps(result, indent=2))
