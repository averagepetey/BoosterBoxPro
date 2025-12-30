"""
UnifiedBoxMetrics SQLAlchemy Model
Unified metrics table - PRIMARY table for leaderboard and rankings
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
    """Unified metrics per box per day - PRIMARY table for leaderboard"""
    
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
    
    # Floor price (TCGplayer ONLY - authoritative)
    floor_price_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    floor_price_1d_change_pct: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    
    # Unified Volume (Weighted: TCG × 0.7 + eBay × 0.3)
    unified_volume_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        server_default="0"
    )
    unified_volume_7d_ema: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        index=True  # PRIMARY RANKING METRIC
    )
    
    # Liquidity Score (Blended metric)
    liquidity_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Momentum (eBay-influenced, EMA smoothed)
    momentum_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Demand Velocity (combined)
    boxes_sold_per_day: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    boxes_sold_30d_avg: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Supply Metrics (TCGplayer ONLY)
    active_listings_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default="0"
    )
    visible_market_cap_usd: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    boxes_added_today: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        server_default="0"
    )
    
    # Time-to-Price-Pressure (TCG supply / unified demand)
    days_to_20pct_increase: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Listed percentage (TCGplayer)
    listed_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    
    # Expected days to sell (NEW metric)
    expected_days_to_sell: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    
    # Ranking fields (Phase 6)
    current_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    previous_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rank_change: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
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
    
    # Relationships
    # booster_box: Mapped["BoosterBox"] = relationship(back_populates="unified_metrics")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("booster_box_id", "metric_date", name="uq_unified_metrics_date"),
    )
    
    def __repr__(self) -> str:
        return f"<UnifiedBoxMetrics(id={self.id}, booster_box_id={self.booster_box_id}, date={self.metric_date}, volume_7d_ema={self.unified_volume_7d_ema})>"

