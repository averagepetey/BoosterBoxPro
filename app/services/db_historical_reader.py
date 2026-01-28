"""
DB-backed historical data reader.
Returns the same list-of-dict shape as historical_entries.json so callers
(get_box_price_history, get_rolling_volume_sum, etc.) see no change.

Used when prefer_db=True: read from box_metrics_unified instead of JSON.
No calculations or formulas change—only the source of the rows.
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
    # daily_volume_usd: treat unified_volume_usd as 30d volume, so daily = vol/30
    daily_volume_usd = (uv / 30.0) if uv else None
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
        "boxes_sold_per_day": _f(d.get("boxes_sold_per_day")),
        "boxes_sold_today": _f(d.get("boxes_sold_per_day")),
        "active_listings_count": _f(d.get("active_listings_count"), int) if d.get("active_listings_count") is not None else None,
        "unified_volume_usd": uv,
        "unified_volume_7d_ema": _f(d.get("unified_volume_7d_ema")),
        "daily_volume_usd": daily_volume_usd,
        "boxes_sold_30d_avg": _f(d.get("boxes_sold_30d_avg")),
        "boxes_added_today": _f(d.get("boxes_added_today"), int) if d.get("boxes_added_today") is not None else None,
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
                       unified_volume_7d_ema, boxes_sold_30d_avg, boxes_added_today
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
                       unified_volume_7d_ema, boxes_sold_30d_avg, boxes_added_today
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
            ent = {
                "date": d["metric_date"].isoformat() if hasattr(d.get("metric_date"), "isoformat") else str(d.get("metric_date") or ""),
                "floor_price_usd": float(d["floor_price_usd"]) if d.get("floor_price_usd") is not None else None,
                "floor_price_1d_change_pct": float(d["floor_price_1d_change_pct"]) if d.get("floor_price_1d_change_pct") is not None else None,
                "boxes_sold_per_day": float(d["boxes_sold_per_day"]) if d.get("boxes_sold_per_day") is not None else None,
                "boxes_sold_today": float(d["boxes_sold_per_day"]) if d.get("boxes_sold_per_day") is not None else None,
                "active_listings_count": int(d["active_listings_count"]) if d.get("active_listings_count") is not None else None,
                "unified_volume_usd": uv,
                "unified_volume_7d_ema": float(d["unified_volume_7d_ema"]) if d.get("unified_volume_7d_ema") is not None else None,
                "daily_volume_usd": (uv / 30.0) if uv is not None else None,
                "boxes_sold_30d_avg": float(d["boxes_sold_30d_avg"]) if d.get("boxes_sold_30d_avg") is not None else None,
                "boxes_added_today": int(d["boxes_added_today"]) if d.get("boxes_added_today") is not None else None,
            }
            out.setdefault(bid, []).append(ent)
        return out
    except Exception:
        return {}
