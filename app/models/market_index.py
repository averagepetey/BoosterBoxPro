"""
MarketIndexDaily SQLAlchemy Model
One row per day capturing the aggregate BoosterBox Index and market-wide stats.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy import String, Integer, Date, Numeric, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models import Base


class MarketIndexDaily(Base):
    """
    Daily market-wide aggregate metrics.
    One row per day, computed by scripts/market_index.py from box_metrics_unified.
    API reads directly from this table - no calculations at query time.
    """

    __tablename__ = "market_index_daily"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    # Date for this index entry (one row per day)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)

    # ═══════════════════════════════════════════════════════════════════
    # INDEX VALUE
    # ═══════════════════════════════════════════════════════════════════
    index_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    index_1d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    index_7d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    index_30d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # SENTIMENT
    # ═══════════════════════════════════════════════════════════════════
    sentiment: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # BULLISH / BEARISH / NEUTRAL
    fear_greed_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-100

    # ═══════════════════════════════════════════════════════════════════
    # PRICE MOVEMENT
    # ═══════════════════════════════════════════════════════════════════
    floors_up_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    floors_down_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    floors_flat_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    biggest_gainer_box_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("booster_boxes.id", ondelete="SET NULL"),
        nullable=True
    )
    biggest_gainer_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    biggest_loser_box_id: Mapped[Optional[UUID]] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("booster_boxes.id", ondelete="SET NULL"),
        nullable=True
    )
    biggest_loser_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # VOLUME & LIQUIDITY
    # ═══════════════════════════════════════════════════════════════════
    total_daily_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_7d_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_30d_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    volume_1d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    volume_7d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    avg_liquidity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    total_boxes_sold_today: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # SUPPLY
    # ═══════════════════════════════════════════════════════════════════
    total_active_listings: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_boxes_added_today: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    net_supply_change: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    listings_1d_change: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════════
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<MarketIndexDaily(date={self.metric_date}, index={self.index_value}, sentiment={self.sentiment})>"
