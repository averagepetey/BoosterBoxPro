"""
Write eBay metrics into ebay_box_metrics_daily and ebay_sales_raw tables.
Called by scripts/ebay_scraper.py (Phase 1b) after scraping 130point.com.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.services.db_historical_reader import _get_sync_engine

_upsert_daily_sql = text("""
    INSERT INTO ebay_box_metrics_daily (
        booster_box_id, metric_date,
        ebay_sales_count, ebay_volume_usd,
        ebay_median_sold_price_usd, ebay_units_sold_count,
        ebay_sales_acceleration, ebay_volume_7d_ema,
        ebay_active_listings_count, ebay_active_median_price_usd,
        ebay_active_low_price_usd, ebay_listings_added_today,
        ebay_listings_removed_today
    ) VALUES (
        CAST(:bid AS uuid), CAST(:md AS date),
        :esc, :evu, :emsp, :eusc, :esa, :ev7,
        :ealc, :eamp, :ealp, :elat, :elrt
    )
    ON CONFLICT (booster_box_id, metric_date)
    DO UPDATE SET
        ebay_sales_count = COALESCE(EXCLUDED.ebay_sales_count, ebay_box_metrics_daily.ebay_sales_count),
        ebay_volume_usd = COALESCE(EXCLUDED.ebay_volume_usd, ebay_box_metrics_daily.ebay_volume_usd),
        ebay_median_sold_price_usd = COALESCE(EXCLUDED.ebay_median_sold_price_usd, ebay_box_metrics_daily.ebay_median_sold_price_usd),
        ebay_units_sold_count = COALESCE(EXCLUDED.ebay_units_sold_count, ebay_box_metrics_daily.ebay_units_sold_count),
        ebay_sales_acceleration = COALESCE(EXCLUDED.ebay_sales_acceleration, ebay_box_metrics_daily.ebay_sales_acceleration),
        ebay_volume_7d_ema = COALESCE(EXCLUDED.ebay_volume_7d_ema, ebay_box_metrics_daily.ebay_volume_7d_ema),
        ebay_active_listings_count = COALESCE(EXCLUDED.ebay_active_listings_count, ebay_box_metrics_daily.ebay_active_listings_count),
        ebay_active_median_price_usd = COALESCE(EXCLUDED.ebay_active_median_price_usd, ebay_box_metrics_daily.ebay_active_median_price_usd),
        ebay_active_low_price_usd = COALESCE(EXCLUDED.ebay_active_low_price_usd, ebay_box_metrics_daily.ebay_active_low_price_usd),
        ebay_listings_added_today = COALESCE(EXCLUDED.ebay_listings_added_today, ebay_box_metrics_daily.ebay_listings_added_today),
        ebay_listings_removed_today = COALESCE(EXCLUDED.ebay_listings_removed_today, ebay_box_metrics_daily.ebay_listings_removed_today),
        updated_at = NOW()
""")

_insert_raw_sql = text("""
    INSERT INTO ebay_sales_raw (
        booster_box_id, sale_date, sale_timestamp,
        ebay_item_id, sold_price_usd, quantity,
        listing_type, raw_data
    ) VALUES (
        CAST(:bid AS uuid), CAST(:sd AS date), :st,
        :eid, :sp, :qty, :lt, CAST(:rd AS jsonb)
    )
    ON CONFLICT (booster_box_id, ebay_item_id)
    DO NOTHING
""")


def upsert_ebay_daily_metrics(
    booster_box_id: str,
    metric_date: str,
    ebay_sales_count: Optional[int] = None,
    ebay_volume_usd: Optional[float] = None,
    ebay_median_sold_price_usd: Optional[float] = None,
    ebay_units_sold_count: Optional[int] = None,
    ebay_sales_acceleration: Optional[float] = None,
    ebay_volume_7d_ema: Optional[float] = None,
    ebay_active_listings_count: Optional[int] = None,
    ebay_active_median_price_usd: Optional[float] = None,
    ebay_active_low_price_usd: Optional[float] = None,
    ebay_listings_added_today: Optional[int] = None,
    ebay_listings_removed_today: Optional[int] = None,
) -> bool:
    """Upsert one row into ebay_box_metrics_daily. Returns True on success."""
    try:
        engine = _get_sync_engine()
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(_upsert_daily_sql, {
                    "bid": booster_box_id,
                    "md": metric_date,
                    "esc": ebay_sales_count,
                    "evu": ebay_volume_usd,
                    "emsp": ebay_median_sold_price_usd,
                    "eusc": ebay_units_sold_count,
                    "esa": ebay_sales_acceleration,
                    "ev7": ebay_volume_7d_ema,
                    "ealc": ebay_active_listings_count,
                    "eamp": ebay_active_median_price_usd,
                    "ealp": ebay_active_low_price_usd,
                    "elat": ebay_listings_added_today,
                    "elrt": ebay_listings_removed_today,
                })
        return True
    except Exception:
        return False


def insert_ebay_sales_raw(
    booster_box_id: str,
    sold_items: List[Dict[str, Any]],
) -> int:
    """Insert individual eBay sales into ebay_sales_raw. Returns count inserted."""
    import json

    inserted = 0
    try:
        engine = _get_sync_engine()
        with engine.connect() as conn:
            with conn.begin():
                for item in sold_items:
                    ebay_item_id = item.get("ebay_item_id")
                    if not ebay_item_id:
                        continue
                    # Caller sends sold_price_usd (dollars, float)
                    price_usd = item.get("sold_price_usd") or 0
                    conn.execute(_insert_raw_sql, {
                        "bid": booster_box_id,
                        "sd": item.get("sold_date"),
                        "st": item.get("sold_date"),  # Use date as timestamp fallback
                        "eid": ebay_item_id,
                        "sp": float(price_usd),
                        "qty": 1,
                        "lt": item.get("sale_type"),
                        "rd": json.dumps({
                            "title": item.get("title"),
                            "item_url": item.get("item_url"),
                            "sale_type": item.get("sale_type"),
                        }),
                    })
                    inserted += 1
        return inserted
    except Exception:
        return inserted


_accumulated_sql = text("""
    SELECT
        COUNT(DISTINCT ebay_item_id) AS count,
        COALESCE(SUM(sold_price_usd), 0) AS volume,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sold_price_usd) AS median_price
    FROM ebay_sales_raw
    WHERE booster_box_id = CAST(:bid AS uuid)
      AND sale_date = CAST(:sd AS date)
""")


def query_accumulated_ebay_metrics(
    booster_box_id: str,
    sale_date: str,
) -> Dict[str, Any]:
    """Query ebay_sales_raw for the accumulated count/volume/median for a box+date.

    Returns dict with keys: count (int), volume (float), median_price (float|None).
    """
    try:
        engine = _get_sync_engine()
        with engine.connect() as conn:
            row = conn.execute(_accumulated_sql, {"bid": booster_box_id, "sd": sale_date}).fetchone()
            if row:
                return {
                    "count": int(row[0]),
                    "volume": float(row[1]),
                    "median_price": float(row[2]) if row[2] is not None else None,
                }
    except Exception:
        pass
    return {"count": 0, "volume": 0.0, "median_price": None}
