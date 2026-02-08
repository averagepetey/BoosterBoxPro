"""
DB-backed historical data reader — single source of truth for all historical data.
Reads from box_metrics_unified and returns list-of-dict rows for callers
(get_box_price_history, get_rolling_volume_sum, etc.).

All API endpoints read through this module. No calculations happen here;
derived metrics are pre-computed by rolling_metrics.py (Phase 3) and stored in DB.
"""

from __future__ import annotations

from typing import Any, Dict, List

# Lazy import to avoid loading SQLAlchemy sync at module level if not used
_engine = None


def _get_sync_engine():
    global _engine
    if _engine is not None:
        return _engine
    from sqlalchemy import create_engine
    from app.config import settings
    url = settings.database_url
    if "+asyncpg" in url:
        url = url.replace("postgresql+asyncpg", "postgresql+psycopg2", 1)
    elif "postgresql://" in url and "+" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    _engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=3,
        max_overflow=2,
    )
    return _engine


def _row_to_entry(row: Any) -> Dict[str, Any]:
    """
    Map box_metrics_unified row to the entry dict shape expected by
    get_box_price_history, get_rolling_volume_sum, get_box_30d_avg_sales, etc.
    Keeps keys and types compatible so no downstream logic changes.
    """
    d = row._mapping if hasattr(row, "_mapping") else dict(row)
    metric_date = d.get("metric_date")
    date_str = metric_date.isoformat() if hasattr(metric_date, "isoformat") else str(metric_date) if metric_date else None
    floor_price_usd = d.get("floor_price_usd")
    fp = float(floor_price_usd) if floor_price_usd is not None else None
    unified_volume_usd = d.get("unified_volume_usd")
    uv = float(unified_volume_usd) if unified_volume_usd is not None else None
    # Read daily_volume_usd directly from DB - no calculation
    daily_vol = d.get("daily_volume_usd")
    daily_volume_usd = float(daily_vol) if daily_vol is not None else None
    def _f(v, cast=float):
        if v is None:
            return None
        try:
            return cast(v)
        except (TypeError, ValueError):
            return None
    entry = {
        "date": date_str,
        "floor_price_usd": fp,
        "floor_price_1d_change_pct": _f(d.get("floor_price_1d_change_pct")),
        "boxes_sold_today": _f(d.get("boxes_sold_per_day")),
        "active_listings_count": _f(d.get("active_listings_count"), int) if d.get("active_listings_count") is not None else None,
        "unified_volume_usd": uv,
        "unified_volume_7d_ema": _f(d.get("unified_volume_7d_ema")),
        "daily_volume_usd": daily_volume_usd,
        "boxes_sold_30d_avg": _f(d.get("boxes_sold_30d_avg")),
        "boxes_added_today": _f(d.get("boxes_added_today"), int) if d.get("boxes_added_today") is not None else None,
        # Volume breakdown + eBay fields (written by rolling_metrics Phase 3)
        "tcg_daily_volume_usd": _f(d.get("tcg_daily_volume_usd")),
        "ebay_daily_volume_usd": _f(d.get("ebay_daily_volume_usd")),
        "ebay_units_sold_count": _f(d.get("ebay_units_sold_count")),
        "ebay_active_listings_count": _f(d.get("ebay_active_listings_count"), int) if d.get("ebay_active_listings_count") is not None else None,
        # Aliases expected by leaderboard / box detail
        "daily_volume_tcg_usd": _f(d.get("tcg_daily_volume_usd")),
        "daily_volume_ebay_usd": _f(d.get("ebay_daily_volume_usd")),
        "ebay_sold_today": _f(d.get("ebay_units_sold_count")),
        "ebay_active_listings": _f(d.get("ebay_active_listings_count"), int) if d.get("ebay_active_listings_count") is not None else None,
        "liquidity_score": _f(d.get("liquidity_score")),
        "days_to_20pct_increase": _f(d.get("days_to_20pct_increase")),
        "expected_days_to_sell": _f(d.get("expected_days_to_sell")),
        "avg_boxes_added_per_day": _f(d.get("avg_boxes_added_per_day")),
    }
    return entry


def get_box_historical_entries_from_db(booster_box_id: str) -> List[Dict[str, Any]]:
    """
    Load per-day history for a box from box_metrics_unified.
    booster_box_id must be the DB UUID (caller resolves leaderboard UUIDs).
    Returns the same structure as JSON entries so get_box_historical_data
    can swap source without changing callers.
    """
    try:
        from sqlalchemy import text
        engine = _get_sync_engine()
        with engine.connect() as conn:
            # Select columns that map to the entry shape used by historical_data callers
            q = text("""
                SELECT metric_date, floor_price_usd, floor_price_1d_change_pct,
                       boxes_sold_per_day, active_listings_count, unified_volume_usd,
                       unified_volume_7d_ema, boxes_sold_30d_avg, boxes_added_today,
                       daily_volume_usd, tcg_daily_volume_usd, ebay_daily_volume_usd,
                       ebay_units_sold_count, ebay_active_listings_count,
                       liquidity_score, days_to_20pct_increase,
                       expected_days_to_sell, avg_boxes_added_per_day
                FROM box_metrics_unified
                WHERE booster_box_id = :bid
                ORDER BY metric_date ASC
            """)
            rows = conn.execute(q, {"bid": booster_box_id}).fetchall()
        return [_row_to_entry(r) for r in rows]
    except Exception:
        return []


def get_all_boxes_historical_entries_from_db(box_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load per-day history for many boxes in one query. Used by leaderboard batch path.
    Returns {booster_box_id: [entries...]} with same entry shape as get_box_historical_entries_from_db.
    """
    if not box_ids:
        return {}
    try:
        from sqlalchemy import text, bindparam
        engine = _get_sync_engine()
        with engine.connect() as conn:
            # Expanding=True turns :ids into (id1, id2, ...) for IN
            q = text("""
                SELECT booster_box_id, metric_date, floor_price_usd, floor_price_1d_change_pct,
                       boxes_sold_per_day, active_listings_count, unified_volume_usd,
                       unified_volume_7d_ema, boxes_sold_30d_avg, boxes_added_today,
                       daily_volume_usd, tcg_daily_volume_usd, ebay_daily_volume_usd,
                       ebay_units_sold_count, ebay_active_listings_count,
                       liquidity_score, days_to_20pct_increase,
                       expected_days_to_sell, avg_boxes_added_per_day
                FROM box_metrics_unified
                WHERE booster_box_id IN :ids
                ORDER BY booster_box_id, metric_date ASC
            """).bindparams(bindparam("ids", expanding=True))
            rows = conn.execute(q, {"ids": box_ids}).fetchall()
        out: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            d = r._mapping if hasattr(r, "_mapping") else dict(r)
            bid = str(d["booster_box_id"])
            uv = float(d["unified_volume_usd"]) if d.get("unified_volume_usd") is not None else None
            def _f(v, cast=float):
                if v is None:
                    return None
                try:
                    return cast(v)
                except (TypeError, ValueError):
                    return None
            ent = {
                "date": d["metric_date"].isoformat() if hasattr(d.get("metric_date"), "isoformat") else str(d.get("metric_date") or ""),
                "floor_price_usd": _f(d.get("floor_price_usd")),
                "floor_price_1d_change_pct": _f(d.get("floor_price_1d_change_pct")),
                "boxes_sold_today": _f(d.get("boxes_sold_per_day")),
                "active_listings_count": _f(d.get("active_listings_count"), int),
                "unified_volume_usd": uv,
                "unified_volume_7d_ema": _f(d.get("unified_volume_7d_ema")),
                "daily_volume_usd": _f(d.get("daily_volume_usd")),
                "boxes_sold_30d_avg": _f(d.get("boxes_sold_30d_avg")),
                "boxes_added_today": _f(d.get("boxes_added_today"), int),
                # Volume breakdown + eBay fields
                "tcg_daily_volume_usd": _f(d.get("tcg_daily_volume_usd")),
                "ebay_daily_volume_usd": _f(d.get("ebay_daily_volume_usd")),
                "ebay_units_sold_count": _f(d.get("ebay_units_sold_count")),
                "ebay_active_listings_count": _f(d.get("ebay_active_listings_count"), int),
                # Aliases expected by leaderboard / box detail
                "daily_volume_tcg_usd": _f(d.get("tcg_daily_volume_usd")),
                "daily_volume_ebay_usd": _f(d.get("ebay_daily_volume_usd")),
                "ebay_sold_today": _f(d.get("ebay_units_sold_count")),
                "ebay_active_listings": _f(d.get("ebay_active_listings_count"), int),
                "liquidity_score": _f(d.get("liquidity_score")),
                "days_to_20pct_increase": _f(d.get("days_to_20pct_increase")),
                "expected_days_to_sell": _f(d.get("expected_days_to_sell")),
                "avg_boxes_added_per_day": _f(d.get("avg_boxes_added_per_day")),
            }
            out.setdefault(bid, []).append(ent)
        return out
    except Exception:
        return {}
