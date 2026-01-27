"""
Write one day of metrics into box_metrics_unified.
Used by listings_scraper, tcgplayer_apify, historical_data_manager so new data
shows on the live site without commits.
"""

from typing import Optional

from sqlalchemy import text

from app.services.db_historical_reader import _get_sync_engine

_upsert_sql = text("""
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


def upsert_daily_metrics(
    booster_box_id: str,
    metric_date: str,
    floor_price_usd: Optional[float] = None,
    boxes_sold_per_day: Optional[float] = None,
    active_listings_count: Optional[int] = None,
    unified_volume_usd: Optional[float] = None,
    unified_volume_7d_ema: Optional[float] = None,
    boxes_sold_30d_avg: Optional[float] = None,
    boxes_added_today: Optional[int] = None,
) -> bool:
    """Upsert one row into box_metrics_unified. Returns True on success, False on FK/error."""
    try:
        engine = _get_sync_engine()
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(_upsert_sql, {
                    "bid": booster_box_id,
                    "md": metric_date,
                    "fp": floor_price_usd,
                    "bspd": boxes_sold_per_day,
                    "alc": active_listings_count,
                    "uvu": unified_volume_usd,
                    "uv7": unified_volume_7d_ema,
                    "bs30": boxes_sold_30d_avg,
                    "bat": boxes_added_today,
                })
        return True
    except Exception:
        return False
