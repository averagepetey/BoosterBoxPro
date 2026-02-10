#!/usr/bin/env python3
"""
One-time migration: Create the market_index_daily table in Supabase.
Uses the same DB connection as the rest of the project.

Run:  python scripts/create_market_index_table.py
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.services.db_historical_reader import _get_sync_engine

CREATE_SQL = text("""
CREATE TABLE IF NOT EXISTS market_index_daily (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_date     DATE NOT NULL UNIQUE,

    -- Index value
    index_value             NUMERIC(10, 2),
    index_1d_change_pct     NUMERIC(6, 2),
    index_7d_change_pct     NUMERIC(6, 2),
    index_30d_change_pct    NUMERIC(6, 2),

    -- Sentiment
    sentiment               VARCHAR(10),
    fear_greed_score        INTEGER,

    -- Price movement
    floors_up_count         INTEGER,
    floors_down_count       INTEGER,
    floors_flat_count       INTEGER,
    biggest_gainer_box_id   UUID REFERENCES booster_boxes(id) ON DELETE SET NULL,
    biggest_gainer_pct      NUMERIC(6, 2),
    biggest_loser_box_id    UUID REFERENCES booster_boxes(id) ON DELETE SET NULL,
    biggest_loser_pct       NUMERIC(6, 2),

    -- Volume & liquidity
    total_daily_volume_usd  NUMERIC(12, 2),
    total_7d_volume_usd     NUMERIC(12, 2),
    total_30d_volume_usd    NUMERIC(12, 2),
    volume_1d_change_pct    NUMERIC(6, 2),
    volume_7d_change_pct    NUMERIC(6, 2),
    avg_liquidity_score     NUMERIC(8, 2),
    total_boxes_sold_today  NUMERIC(8, 2),

    -- Supply
    total_active_listings   INTEGER,
    total_boxes_added_today INTEGER,
    net_supply_change       INTEGER,
    listings_1d_change      INTEGER,

    -- Timestamps
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for date lookups
CREATE INDEX IF NOT EXISTS idx_market_index_daily_date ON market_index_daily (metric_date);
""")


def main():
    print("Connecting to Supabase...")
    engine = _get_sync_engine()

    with engine.connect() as conn:
        with conn.begin():
            conn.execute(CREATE_SQL)
    print("✅ market_index_daily table created successfully!")

    # Verify
    with engine.connect() as conn:
        row = conn.execute(text("SELECT COUNT(*) FROM market_index_daily")).fetchone()
        print(f"   Table exists with {row[0]} rows.")


if __name__ == "__main__":
    main()
