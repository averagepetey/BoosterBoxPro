"""
Rank History Service using DB metrics data.
Calculates rankings from box_metrics_unified volume data.
"""

from typing import Dict, List, Optional, Any


def _get_all_box_ids() -> List[str]:
    """Get all booster box IDs from the database."""
    try:
        from sqlalchemy import text
        from app.services.db_historical_reader import _get_sync_engine
        engine = _get_sync_engine()
        with engine.connect() as conn:
            rows = conn.execute(text("SELECT id FROM booster_boxes ORDER BY id")).fetchall()
        return [str(r[0]) for r in rows]
    except Exception:
        return []


def calculate_ranks_for_date(date_str: str, box_volumes: Dict[str, float]) -> Dict[str, int]:
    """
    Calculate ranks for all boxes on a specific date based on volume.
    Returns {box_id: rank} where rank 1 = highest volume.
    """
    valid_volumes = {bid: vol for bid, vol in box_volumes.items() if vol is not None and vol > 0}
    if not valid_volumes:
        return {}

    sorted_boxes = sorted(valid_volumes.items(), key=lambda x: x[1], reverse=True)

    ranks = {}
    current_rank = 1
    previous_volume: Optional[float] = None

    for box_id, volume in sorted_boxes:
        if previous_volume is not None and volume != previous_volume:
            current_rank = len(ranks) + 1
        ranks[box_id] = current_rank
        previous_volume = volume

    return ranks


def get_rank_history_for_box_optimized(box_id: str) -> List[Dict[str, Any]]:
    """
    Get rank history for a specific box from DB data.
    Returns list of {date, rank} sorted by date.
    """
    try:
        from app.services.db_historical_reader import get_all_boxes_historical_entries_from_db
    except ImportError:
        return []

    box_ids = _get_all_box_ids()
    if not box_ids:
        return []

    all_entries = get_all_boxes_historical_entries_from_db(box_ids)
    if not all_entries:
        return []

    # Collect all unique dates
    all_dates: set = set()
    for entries in all_entries.values():
        for e in entries:
            d = e.get("date")
            if d:
                all_dates.add(d)

    # For each date, collect unified_volume_7d_ema per box and rank
    rank_history = []
    for date_str in sorted(all_dates):
        box_volumes: Dict[str, float] = {}
        for bid, entries in all_entries.items():
            for e in entries:
                if e.get("date") == date_str:
                    vol = e.get("unified_volume_7d_ema")
                    if vol is not None:
                        box_volumes[bid] = vol
                    break

        date_ranks = calculate_ranks_for_date(date_str, box_volumes)
        if box_id in date_ranks:
            rank_history.append({"date": date_str, "rank": date_ranks[box_id]})

    return rank_history


# Public API
get_box_rank_history = get_rank_history_for_box_optimized
