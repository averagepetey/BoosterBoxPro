"""
UnifiedBoxMetrics SQLAlchemy Model
Single source of truth for all daily metrics per box.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from sqlalchemy import String, Integer, Date, Numeric, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models import Base


class UnifiedBoxMetrics(Base):
    """
    Unified metrics per box per day.
    All metrics calculated in rolling_metrics.py and stored here.
    API reads directly from this table - no calculations at query time.
    """

    __tablename__ = "box_metrics_unified"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    # Foreign key to booster_boxes
    booster_box_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("booster_boxes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Date for this metric
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # ═══════════════════════════════════════════════════════════════════
    # PRICE METRICS
    # ═══════════════════════════════════════════════════════════════════
    floor_price_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    floor_price_1d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # VOLUME METRICS (Daily)
    # ═══════════════════════════════════════════════════════════════════
    # Actual daily volume: TCG (estimated) + eBay (actual)
    daily_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    tcg_daily_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    ebay_daily_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)

    # Rolling volume metrics
    unified_volume_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)  # 30-day sum
    unified_volume_7d_ema: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True, index=True)

    # ═══════════════════════════════════════════════════════════════════
    # SALES METRICS
    # ═══════════════════════════════════════════════════════════════════
    boxes_sold_per_day: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)  # TCG
    ebay_units_sold_count: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)  # eBay
    boxes_sold_30d_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # LISTINGS/SUPPLY METRICS
    # ═══════════════════════════════════════════════════════════════════
    active_listings_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # TCG
    ebay_active_listings_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # eBay
    boxes_added_today: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_boxes_added_per_day: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)

    # ═══════════════════════════════════════════════════════════════════
    # DERIVED METRICS (calculated in rolling_metrics.py)
    # ═══════════════════════════════════════════════════════════════════
    liquidity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    days_to_20pct_increase: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    expected_days_to_sell: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)

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

    # Constraints
    __table_args__ = (
        UniqueConstraint("booster_box_id", "metric_date", name="uq_unified_metrics_date"),
    )

    def __repr__(self) -> str:
        return f"<UnifiedBoxMetrics(id={self.id}, box={self.booster_box_id}, date={self.metric_date}, daily_vol={self.daily_volume_usd})>"
