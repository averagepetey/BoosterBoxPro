"""
Shared box detail metrics and response builder.
Single source of truth for box detail page and Chrome extension API.
"""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booster_box import BoosterBox
from app.models.unified_box_metrics import UnifiedBoxMetrics


# Manual Top 10 cards value (USD) per set - from spreadsheet
TOP_10_VALUE_USD: dict[str, float] = {
    "One Piece - OP-01 Romance Dawn Booster Box (White)": 3824.96,
    "One Piece - OP-02 Paramount War Booster Box": 1802.86,
    "One Piece - OP-03 Pillars of Strength Booster Box": 1897.50,
    "One Piece - OP-04 Kingdoms of Intrigue Booster Box": 1972.72,
    "One Piece - OP-05 Awakening of the New Era Booster Box": 9478.29,
    "One Piece - OP-06 Wings of the Captain Booster Box": 2860.39,
    "One Piece - EB-01 Memorial Collection Booster Box": 1979.89,
    "One Piece - OP-07 500 Years in the Future Booster Box": 2127.59,
    "One Piece - OP-08 Two Legends Booster Box": 1587.60,
    "One Piece - PRB-01 Premium Booster Booster Box": 8164.56,
    "One Piece - OP-09 Emperors in the New World Booster Box": 11547.80,
    "One Piece - OP-10 Royal Blood Booster Box": 1420.75,
    "One Piece - EB-02 Anime 25th Collection Booster Box": 4894.15,
    "One Piece - OP-11 A Fist of Divine Speed Booster Box": 6110.98,
    "One Piece - OP-12 Legacy of the Master Booster Box": 3241.99,
    "One Piece - PRB-02 Premium Booster Booster Box": 4019.20,
    "One Piece - OP-13 Carrying on His Will Booster Box": 23386.16,
}

MANUAL_LIQUIDITY_REPRINT: dict[str, tuple[int, str]] = {
    "OP-01": (50, "LOW"),
    "OP-02": (25, "LOW"),
    "OP-03": (25, "LOW"),
    "OP-04": (25, "LOW"),
    "OP-05": (65, "MEDIUM"),
    "OP-06": (35, "MEDIUM"),
    "OP-07": (35, "MEDIUM"),
    "OP-08": (25, "MEDIUM"),
    "OP-09": (75, "MEDIUM"),
    "OP-10": (50, "HIGH"),
    "OP-11": (65, "HIGH"),
    "OP-12": (75, "HIGH"),
    "OP-13": (90, "HIGH"),
    "EB-01": (50, "LOW"),
    "EB-02": (50, "LOW"),
    "PRB-01": (65, "LOW"),
    "PRB-02": (65, "MEDIUM"),
}

MANUAL_COMMUNITY_SENTIMENT: dict[str, int] = {
    "OP-01 Blue": 97,
    "OP-01 White": 93,
    "OP-02": 39,
    "OP-03": 38,
    "OP-04": 40,
    "OP-05": 83,
    "OP-06": 70,
    "OP-07": 43,
    "OP-08": 37,
    "OP-09": 86,
    "OP-10": 51,
    "OP-11": 74,
    "OP-12": 63,
    "OP-13": 90,
    "EB-01": 45,
    "EB-02": 70,
    "PRB-01": 80,
    "PRB-02": 60,
}


def _set_code_from_product_name(product_name: str | None) -> str | None:
    if not product_name:
        return None
    m = re.search(r"(OP|EB|PRB)-\d+", product_name, re.IGNORECASE)
    return m.group(0).upper() if m else None


def set_code_from_product_name(product_name: str | None) -> str | None:
    """Public alias for use by leaderboard and others."""
    return _set_code_from_product_name(product_name)


def get_manual_community_sentiment(product_name: str | None) -> int | None:
    if not product_name:
        return None
    set_code = _set_code_from_product_name(product_name)
    if not set_code:
        return None
    if set_code == "OP-01":
        if "White" in product_name:
            return MANUAL_COMMUNITY_SENTIMENT.get("OP-01 White")
        if "Blue" in product_name:
            return MANUAL_COMMUNITY_SENTIMENT.get("OP-01 Blue")
    return MANUAL_COMMUNITY_SENTIMENT.get(set_code)


def get_manual_liquidity_reprint(product_name: str | None) -> tuple[int | None, str | None]:
    set_code = _set_code_from_product_name(product_name)
    if not set_code:
        return None, None
    pair = MANUAL_LIQUIDITY_REPRINT.get(set_code)
    if not pair:
        return None, None
    return pair[0], pair[1]


def get_top_10_value_usd(product_name: str | None) -> float | None:
    if not product_name:
        return None
    if product_name in TOP_10_VALUE_USD:
        return TOP_10_VALUE_USD[product_name]
    m = re.search(r"(OP|EB|PRB)-\d+", product_name, re.IGNORECASE)
    if not m:
        return None
    set_code = m.group(0).upper()
    for key, val in TOP_10_VALUE_USD.items():
        if set_code in key.upper():
            return val
    return None


def get_box_image_url(product_name: str | None) -> str | None:
    if not product_name:
        return None
    set_match = re.search(r"(OP|EB|PRB)-\d+", product_name, re.IGNORECASE)
    if not set_match:
        return None
    set_code = set_match.group(0).upper()
    if "(Blue)" in product_name:
        if set_code == "OP-01":
            filename = f"{set_code.lower()}blue.png"
        else:
            filename = f"{set_code.lower()}-blue.png"
    elif "(White)" in product_name:
        if set_code == "OP-01":
            filename = f"{set_code.lower()}white.png"
        else:
            filename = f"{set_code.lower()}-white.png"
    else:
        filename = f"{set_code.lower()}.png"
    return f"/images/boxes/{filename}"


async def build_box_detail_data(db: AsyncSession, db_box: BoosterBox) -> dict[str, Any]:
    """
    Build the full box detail payload (same as GET /booster-boxes/{box_id} response["data"]).
    Single source of truth for dashboard box detail page and extension API.
    """
    from app.services.historical_data import (
        get_box_price_history,
        get_box_month_over_month_price_change,
        get_box_30d_avg_sales,
        get_box_30d_volume_or_ramp,
        get_box_volume_change_pcts,
    )

    latest_metric_stmt = (
        select(UnifiedBoxMetrics)
        .where(UnifiedBoxMetrics.booster_box_id == db_box.id)
        .order_by(UnifiedBoxMetrics.metric_date.desc())
        .limit(1)
    )
    latest_metric_result = await db.execute(latest_metric_stmt)
    latest_db_metric = latest_metric_result.scalar_one_or_none()
    current_floor_override = float(latest_db_metric.floor_price_usd) if (latest_db_metric and latest_db_metric.floor_price_usd) else None

    historical_data = None
    try:
        historical_data = get_box_price_history(str(db_box.id), days=90)
    except Exception:
        historical_data = None

    box_metrics: dict[str, Any] = {}
    if historical_data:
        latest = historical_data[-1]
        active_listings = latest.get("active_listings_count") or 0
        if not active_listings and len(historical_data) > 1:
            for entry in reversed(historical_data[:-1]):
                alc = entry.get("active_listings_count")
                if alc is not None and alc > 0:
                    active_listings = int(alc)
                    break
        if not active_listings and latest_db_metric and (latest_db_metric.active_listings_count or 0) > 0:
            active_listings = int(latest_db_metric.active_listings_count)
        boxes_sold_per_day = latest.get("boxes_sold_per_day") or 0

        avg_sales_30d = latest.get("boxes_sold_30d_avg")
        if avg_sales_30d is None:
            try:
                avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
            except Exception:
                avg_sales_30d = None
        if avg_sales_30d is None and latest_db_metric and (latest_db_metric.boxes_sold_30d_avg or 0) > 0:
            avg_sales_30d = float(latest_db_metric.boxes_sold_30d_avg)

        avg_boxes_added_per_day = latest.get("avg_boxes_added_per_day")
        boxes_added_values: list[float] = []
        has_30_days_boxes_added = False
        if avg_boxes_added_per_day is None and len(historical_data) > 0:
            recent_entries = historical_data[-30:] if len(historical_data) >= 30 else historical_data
            boxes_added_values = [e.get("boxes_added_today", 0) for e in recent_entries if e.get("boxes_added_today") is not None]
            avg_boxes_added_per_day = sum(boxes_added_values) / len(boxes_added_values) if boxes_added_values else 0
            has_30_days_boxes_added = len(boxes_added_values) >= 30
        else:
            avg_boxes_added_per_day = avg_boxes_added_per_day or 0
        # Only expose 30-day average when we have 30 entries; otherwise UI shows daily (boxes_added_today)

        # Prefer pre-computed days_to_20pct from Phase 3
        days_to_20pct = latest.get("days_to_20pct_increase")
        if days_to_20pct is None:
            if avg_sales_30d and avg_sales_30d > 0 and active_listings:
                net_burn_rate = avg_sales_30d - avg_boxes_added_per_day
                if net_burn_rate > 0.05:
                    days_to_20pct = round(active_listings / net_burn_rate, 2)
                    if days_to_20pct > 180:
                        days_to_20pct = 180.0
                elif net_burn_rate <= 0:
                    days_to_20pct = None
                else:
                    days_to_20pct = 180.0

        liquidity_score = latest.get("liquidity_score")
        if liquidity_score is None and avg_sales_30d and avg_sales_30d > 0:
            if active_listings and active_listings > 0:
                raw_score = (avg_sales_30d / active_listings) * 100
                liquidity_score = round(min(raw_score, 10), 1)
            else:
                liquidity_score = 5.0

        daily_vol = latest.get("daily_volume_usd") or 0
        volume_7d = latest.get("volume_7d") or (daily_vol * 7 if daily_vol else 0)
        volume_30d = None
        try:
            volume_30d = get_box_30d_volume_or_ramp(str(db_box.id), current_floor_override=current_floor_override)
        except Exception:
            volume_30d = None
        if volume_30d is None:
            volume_30d = latest.get("unified_volume_usd") or (daily_vol * 30 if daily_vol else 0)

        unified_volume_7d_ema = latest.get("unified_volume_7d_ema")
        if unified_volume_7d_ema is None and len(historical_data) >= 2:
            recent_entries = historical_data[-7:] if len(historical_data) >= 7 else historical_data
            volumes = []
            for e in recent_entries:
                vol = e.get("unified_volume_usd")
                if vol is None:
                    daily = e.get("daily_volume_usd")
                    if daily:
                        vol = daily * 30
                if vol:
                    volumes.append(float(vol))
            if volumes:
                alpha = 0.3
                ema = volumes[0]
                for vol in volumes[1:]:
                    ema = (alpha * vol) + ((1 - alpha) * ema)
                unified_volume_7d_ema = round(ema, 2)

        supply_10pct = latest.get("listings_within_10pct_floor")
        supply = supply_10pct if supply_10pct is not None and supply_10pct > 0 else active_listings
        sales_per_day = boxes_sold_per_day or avg_sales_30d
        listings_added_per_day = avg_boxes_added_per_day or 0.0
        # Prefer pre-computed expected_time_to_sale_days from Phase 3
        expected_days_to_sell = latest.get("expected_time_to_sale_days")
        if expected_days_to_sell is None:
            if supply and supply > 0 and sales_per_day and sales_per_day > 0:
                net_burn = sales_per_day - listings_added_per_day
                if net_burn > 0.05:
                    expected_days_to_sell = round(max(1.0, min(365.0, supply / net_burn)), 2)

        boxes_added_today = latest.get("boxes_added_today")
        if boxes_added_today is None and latest_db_metric and latest_db_metric.boxes_added_today is not None:
            boxes_added_today = int(latest_db_metric.boxes_added_today)
        boxes_added_7d_ema = latest.get("boxes_added_7d_ema")
        boxes_added_30d_ema = latest.get("boxes_added_30d_ema")
        box_metrics = {
            "floor_price_usd": float(current_floor_override) if current_floor_override is not None else latest.get("floor_price_usd"),
            "floor_price_1d_change_pct": latest.get("floor_price_1d_change_pct"),
            "active_listings_count": active_listings,
            "daily_volume_usd": daily_vol,
            "volume_7d": volume_7d,
            "volume_30d": volume_30d,
            "unified_volume_usd": volume_30d,
            "unified_volume_7d_ema": unified_volume_7d_ema,
            "boxes_sold_per_day": boxes_sold_per_day,
            "boxes_sold_today": latest.get("boxes_sold_today"),
            "boxes_added_today": boxes_added_today,
            "avg_boxes_added_per_day": round(avg_boxes_added_per_day, 2) if (avg_boxes_added_per_day is not None and has_30_days_boxes_added) else None,
            "days_to_20pct_increase": days_to_20pct,
            "liquidity_score": liquidity_score,
            "boxes_sold_30d_avg": avg_sales_30d,
            "expected_days_to_sell": expected_days_to_sell,
            "expected_time_to_sale_days": expected_days_to_sell,
            "boxes_added_7d_ema": boxes_added_7d_ema,
            "boxes_added_30d_ema": boxes_added_30d_ema,
            "liquidity_label": latest.get("liquidity_label"),
            "data_days_collected": latest.get("data_days_collected"),
            "days_until_30d_metrics": latest.get("days_until_30d_metrics"),
            "listings_within_10pct_floor": latest.get("listings_within_10pct_floor"),
            # eBay marketplace data (from Phase 1b — 130point.com scraper)
            "ebay_sold_today": latest.get("ebay_sold_today"),
            "ebay_daily_volume_usd": latest.get("ebay_daily_volume_usd"),
            "ebay_median_price_usd": latest.get("ebay_median_price_usd"),
            "ebay_active_listings": latest.get("ebay_active_listings"),
            "ebay_active_low_price": latest.get("ebay_active_low_price"),
            "ebay_volume_30d_usd": latest.get("ebay_volume_30d_usd"),
            "ebay_boxes_added_today": latest.get("ebay_boxes_added_today"),
            "ebay_boxes_removed_today": latest.get("ebay_boxes_removed_today"),
            "combined_boxes_sold_today": latest.get("combined_boxes_sold_today"),
            "daily_volume_tcg_usd": latest.get("daily_volume_tcg_usd"),
            "daily_volume_ebay_usd": latest.get("daily_volume_ebay_usd"),
        }
        try:
            changes = get_box_volume_change_pcts(str(db_box.id))
            if changes.get("volume_1d_change_pct") is not None:
                box_metrics["volume_1d_change_pct"] = changes["volume_1d_change_pct"]
            if changes.get("volume_7d_change_pct") is not None:
                box_metrics["volume_7d_change_pct"] = changes["volume_7d_change_pct"]
            if changes.get("volume_30d_change_pct") is not None:
                box_metrics["volume_30d_change_pct"] = changes["volume_30d_change_pct"]
        except Exception:
            pass
    else:
        if latest_db_metric:
            alc = int(latest_db_metric.active_listings_count or 0)
            avg_30d = float(latest_db_metric.boxes_sold_30d_avg or 0) if latest_db_metric.boxes_sold_30d_avg else None
            avg_added = float(latest_db_metric.avg_boxes_added_per_day or 0) if latest_db_metric.avg_boxes_added_per_day else 0
            days_to_20pct = None
            if avg_30d and avg_30d > 0 and alc > 0:
                net_burn = avg_30d - avg_added
                if net_burn > 0.05:
                    days_to_20pct = round(alc / net_burn, 2)
                    if days_to_20pct > 180:
                        days_to_20pct = 180.0
                elif net_burn <= 0:
                    days_to_20pct = None
                else:
                    days_to_20pct = 180.0
            box_metrics = {
                "floor_price_usd": float(latest_db_metric.floor_price_usd) if latest_db_metric.floor_price_usd else None,
                "floor_price_1d_change_pct": float(latest_db_metric.floor_price_1d_change_pct) if latest_db_metric.floor_price_1d_change_pct else None,
                "active_listings_count": alc,
                "daily_volume_usd": float(latest_db_metric.daily_volume_usd) if latest_db_metric.daily_volume_usd else None,
                "volume_7d": None,
                "volume_30d": float(latest_db_metric.unified_volume_usd) if latest_db_metric.unified_volume_usd else None,
                "unified_volume_usd": float(latest_db_metric.unified_volume_usd) if latest_db_metric.unified_volume_usd else None,
                "unified_volume_7d_ema": float(latest_db_metric.unified_volume_7d_ema) if latest_db_metric.unified_volume_7d_ema else None,
                "boxes_sold_per_day": float(latest_db_metric.boxes_sold_per_day) if latest_db_metric.boxes_sold_per_day else None,
                "boxes_sold_30d_avg": avg_30d,
                "boxes_added_today": int(latest_db_metric.boxes_added_today) if latest_db_metric.boxes_added_today is not None else None,
                "avg_boxes_added_per_day": float(latest_db_metric.avg_boxes_added_per_day) if latest_db_metric.avg_boxes_added_per_day is not None else None,
                "days_to_20pct_increase": days_to_20pct if days_to_20pct is not None else (float(latest_db_metric.days_to_20pct_increase) if latest_db_metric.days_to_20pct_increase else None),
                "liquidity_score": float(latest_db_metric.liquidity_score) if latest_db_metric.liquidity_score else None,
                "expected_days_to_sell": None,
                "expected_time_to_sale_days": None,
            }

    price_change_30d = None
    try:
        price_change_30d = get_box_month_over_month_price_change(str(db_box.id))
    except Exception:
        price_change_30d = None
    if price_change_30d is not None:
        box_metrics["floor_price_30d_change_pct"] = price_change_30d

    if "boxes_sold_30d_avg" not in box_metrics or box_metrics["boxes_sold_30d_avg"] is None:
        try:
            avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
            if avg_sales_30d is not None:
                box_metrics["boxes_sold_30d_avg"] = avg_sales_30d
        except Exception:
            pass
        if box_metrics.get("boxes_sold_30d_avg") is None and latest_db_metric and (latest_db_metric.boxes_sold_30d_avg or 0) > 0:
            box_metrics["boxes_sold_30d_avg"] = float(latest_db_metric.boxes_sold_30d_avg)
    if box_metrics.get("days_to_20pct_increase") is None and latest_db_metric and latest_db_metric.days_to_20pct_increase is not None:
        box_metrics["days_to_20pct_increase"] = float(latest_db_metric.days_to_20pct_increase)

    is_op13 = "OP-13" in (db_box.product_name or "")
    if is_op13:
        box_metrics["liquidity_score"] = 90

    manual_liq, manual_reprint = get_manual_liquidity_reprint(db_box.product_name)
    if manual_liq is not None:
        box_metrics["liquidity_score"] = manual_liq
    if manual_reprint is not None:
        reprint_risk_for_response = manual_reprint
    else:
        reprint_risk_for_response = "HIGH" if is_op13 else (db_box.reprint_risk or "UNKNOWN")

    manual_sentiment = get_manual_community_sentiment(db_box.product_name)
    if manual_sentiment is not None:
        box_metrics["community_sentiment"] = manual_sentiment

    top_10 = get_top_10_value_usd(db_box.product_name)
    if top_10 is not None:
        box_metrics["top_10_value_usd"] = top_10

    notes = None
    if is_op13:
        notes = [
            "Official Bandai stores have removed seals on all booster boxes making supply of sealed OP-13 very rare which isn't affecting sealed pricing on secondary even with reprints.",
        ]

    return {
        "id": str(db_box.id),
        "product_name": db_box.product_name,
        "set_name": db_box.set_name,
        "game_type": db_box.game_type or "One Piece",
        "image_url": get_box_image_url(db_box.product_name),
        "release_date": None,
        "external_product_id": None,
        "estimated_total_supply": box_metrics.get("estimated_total_supply"),
        "reprint_risk": reprint_risk_for_response,
        "current_rank_by_volume": None,
        "current_rank_by_market_cap": None,
        "rank_change_direction": "same",
        "rank_change_amount": 0,
        "is_favorited": False,
        "notes": notes,
        "metrics": box_metrics,
    }
