"""
Write one day of market index data into market_index_daily.
Called by scripts/market_index.py after all aggregate data is computed.
"""

from typing import Optional

from sqlalchemy import text

from app.services.db_historical_reader import _get_sync_engine

_upsert_sql = text("""
    INSERT INTO market_index_daily (
        metric_date, index_value,
        index_1d_change_pct, index_7d_change_pct, index_30d_change_pct,
        sentiment, fear_greed_score,
        floors_up_count, floors_down_count, floors_flat_count,
        biggest_gainer_box_id, biggest_gainer_pct,
        biggest_loser_box_id, biggest_loser_pct,
        total_daily_volume_usd, total_7d_volume_usd, total_30d_volume_usd,
        volume_1d_change_pct, volume_7d_change_pct,
        avg_liquidity_score, total_boxes_sold_today,
        total_active_listings, total_boxes_added_today,
        net_supply_change, listings_1d_change
    ) VALUES (
        CAST(:md AS date), :iv,
        :i1d, :i7d, :i30d,
        :sent, :fg,
        :fup, :fdn, :ffl,
        CAST(:bg_id AS uuid), :bg_pct,
        CAST(:bl_id AS uuid), :bl_pct,
        :tdv, :t7v, :t30v,
        :v1d, :v7d,
        :aliq, :tbst,
        :tal, :tbat,
        :nsc, :l1d
    )
    ON CONFLICT (metric_date)
    DO UPDATE SET
        index_value = COALESCE(EXCLUDED.index_value, market_index_daily.index_value),
        index_1d_change_pct = COALESCE(EXCLUDED.index_1d_change_pct, market_index_daily.index_1d_change_pct),
        index_7d_change_pct = COALESCE(EXCLUDED.index_7d_change_pct, market_index_daily.index_7d_change_pct),
        index_30d_change_pct = COALESCE(EXCLUDED.index_30d_change_pct, market_index_daily.index_30d_change_pct),
        sentiment = COALESCE(EXCLUDED.sentiment, market_index_daily.sentiment),
        fear_greed_score = COALESCE(EXCLUDED.fear_greed_score, market_index_daily.fear_greed_score),
        floors_up_count = COALESCE(EXCLUDED.floors_up_count, market_index_daily.floors_up_count),
        floors_down_count = COALESCE(EXCLUDED.floors_down_count, market_index_daily.floors_down_count),
        floors_flat_count = COALESCE(EXCLUDED.floors_flat_count, market_index_daily.floors_flat_count),
        biggest_gainer_box_id = COALESCE(EXCLUDED.biggest_gainer_box_id, market_index_daily.biggest_gainer_box_id),
        biggest_gainer_pct = COALESCE(EXCLUDED.biggest_gainer_pct, market_index_daily.biggest_gainer_pct),
        biggest_loser_box_id = COALESCE(EXCLUDED.biggest_loser_box_id, market_index_daily.biggest_loser_box_id),
        biggest_loser_pct = COALESCE(EXCLUDED.biggest_loser_pct, market_index_daily.biggest_loser_pct),
        total_daily_volume_usd = COALESCE(EXCLUDED.total_daily_volume_usd, market_index_daily.total_daily_volume_usd),
        total_7d_volume_usd = COALESCE(EXCLUDED.total_7d_volume_usd, market_index_daily.total_7d_volume_usd),
        total_30d_volume_usd = COALESCE(EXCLUDED.total_30d_volume_usd, market_index_daily.total_30d_volume_usd),
        volume_1d_change_pct = COALESCE(EXCLUDED.volume_1d_change_pct, market_index_daily.volume_1d_change_pct),
        volume_7d_change_pct = COALESCE(EXCLUDED.volume_7d_change_pct, market_index_daily.volume_7d_change_pct),
        avg_liquidity_score = COALESCE(EXCLUDED.avg_liquidity_score, market_index_daily.avg_liquidity_score),
        total_boxes_sold_today = COALESCE(EXCLUDED.total_boxes_sold_today, market_index_daily.total_boxes_sold_today),
        total_active_listings = COALESCE(EXCLUDED.total_active_listings, market_index_daily.total_active_listings),
        total_boxes_added_today = COALESCE(EXCLUDED.total_boxes_added_today, market_index_daily.total_boxes_added_today),
        net_supply_change = COALESCE(EXCLUDED.net_supply_change, market_index_daily.net_supply_change),
        listings_1d_change = COALESCE(EXCLUDED.listings_1d_change, market_index_daily.listings_1d_change),
        updated_at = NOW()
""")


def upsert_market_index(
    metric_date: str,
    index_value: Optional[float] = None,
    index_1d_change_pct: Optional[float] = None,
    index_7d_change_pct: Optional[float] = None,
    index_30d_change_pct: Optional[float] = None,
    sentiment: Optional[str] = None,
    fear_greed_score: Optional[int] = None,
    floors_up_count: Optional[int] = None,
    floors_down_count: Optional[int] = None,
    floors_flat_count: Optional[int] = None,
    biggest_gainer_box_id: Optional[str] = None,
    biggest_gainer_pct: Optional[float] = None,
    biggest_loser_box_id: Optional[str] = None,
    biggest_loser_pct: Optional[float] = None,
    total_daily_volume_usd: Optional[float] = None,
    total_7d_volume_usd: Optional[float] = None,
    total_30d_volume_usd: Optional[float] = None,
    volume_1d_change_pct: Optional[float] = None,
    volume_7d_change_pct: Optional[float] = None,
    avg_liquidity_score: Optional[float] = None,
    total_boxes_sold_today: Optional[float] = None,
    total_active_listings: Optional[int] = None,
    total_boxes_added_today: Optional[int] = None,
    net_supply_change: Optional[int] = None,
    listings_1d_change: Optional[int] = None,
) -> bool:
    """Upsert one row into market_index_daily. Returns True on success, False on error."""
    try:
        engine = _get_sync_engine()
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(_upsert_sql, {
                    "md": metric_date,
                    "iv": index_value,
                    "i1d": index_1d_change_pct,
                    "i7d": index_7d_change_pct,
                    "i30d": index_30d_change_pct,
                    "sent": sentiment,
                    "fg": fear_greed_score,
                    "fup": floors_up_count,
                    "fdn": floors_down_count,
                    "ffl": floors_flat_count,
                    "bg_id": biggest_gainer_box_id,
                    "bg_pct": biggest_gainer_pct,
                    "bl_id": biggest_loser_box_id,
                    "bl_pct": biggest_loser_pct,
                    "tdv": total_daily_volume_usd,
                    "t7v": total_7d_volume_usd,
                    "t30v": total_30d_volume_usd,
                    "v1d": volume_1d_change_pct,
                    "v7d": volume_7d_change_pct,
                    "aliq": avg_liquidity_score,
                    "tbst": total_boxes_sold_today,
                    "tal": total_active_listings,
                    "tbat": total_boxes_added_today,
                    "nsc": net_supply_change,
                    "l1d": listings_1d_change,
                })
        return True
    except Exception:
        return False
