#!/usr/bin/env python3
"""
Backfill Market Index
---------------------
Iterates over all unique metric_date values in box_metrics_unified
and computes the market index for each date.

Run once after creating the market_index_daily table:
    python scripts/backfill_market_index.py
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def get_all_dates() -> list[str]:
    """Get all unique metric_date values from box_metrics_unified, oldest first."""
    from sqlalchemy import text
    from app.services.db_historical_reader import _get_sync_engine

    engine = _get_sync_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT DISTINCT metric_date
            FROM box_metrics_unified
            ORDER BY metric_date ASC
        """)).fetchall()
    return [str(r[0]) for r in rows]


def main():
    dates = get_all_dates()
    logger.info(f"Found {len(dates)} unique dates to backfill")

    if not dates:
        logger.warning("No dates found in box_metrics_unified")
        return

    from scripts.market_index import compute_market_index

    success = 0
    failed = 0
    for i, date_str in enumerate(dates):
        try:
            result = compute_market_index(target_date=date_str)
            if result.get("db_upserted"):
                success += 1
            else:
                failed += 1
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i + 1}/{len(dates)} dates processed")
        except Exception as e:
            logger.warning(f"Failed to compute index for {date_str}: {e}")
            failed += 1

    logger.info(f"Backfill complete: {success} succeeded, {failed} failed, {len(dates)} total")


if __name__ == "__main__":
    main()
