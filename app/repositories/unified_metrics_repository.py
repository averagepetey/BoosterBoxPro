"""
Unified Metrics Repository
Data access layer for unified metrics operations
"""

from uuid import UUID
from datetime import date, datetime, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import aliased
from decimal import Decimal

from app.models.unified_box_metrics import UnifiedBoxMetrics


class UnifiedMetricsRepository:
    """Repository for unified metrics database operations"""
    
    @staticmethod
    async def create_or_update(db: AsyncSession, metrics_data: dict) -> UnifiedBoxMetrics:
        """Create or update unified metrics for a box on a date"""
        # Check if metrics already exist
        existing = await UnifiedMetricsRepository.get_by_box_and_date(
            db,
            metrics_data["booster_box_id"],
            metrics_data["metric_date"]
        )
        
        if existing:
            # Update existing
            for key, value in metrics_data.items():
                if key != "booster_box_id" and key != "metric_date":
                    setattr(existing, key, value)
            await db.commit()
            await db.refresh(existing)
            return existing
        else:
            # Create new
            metrics = UnifiedBoxMetrics(**metrics_data)
            db.add(metrics)
            await db.commit()
            await db.refresh(metrics)
            return metrics
    
    @staticmethod
    async def get_by_box_and_date(
        db: AsyncSession,
        box_id: UUID,
        metric_date: date
    ) -> Optional[UnifiedBoxMetrics]:
        """Get unified metrics for a box on a specific date"""
        result = await db.execute(
            select(UnifiedBoxMetrics).where(
                and_(
                    UnifiedBoxMetrics.booster_box_id == box_id,
                    UnifiedBoxMetrics.metric_date == metric_date
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_box_date_range(
        db: AsyncSession,
        box_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[UnifiedBoxMetrics]:
        """Get unified metrics for a box within a date range"""
        result = await db.execute(
            select(UnifiedBoxMetrics).where(
                and_(
                    UnifiedBoxMetrics.booster_box_id == box_id,
                    UnifiedBoxMetrics.metric_date >= start_date,
                    UnifiedBoxMetrics.metric_date <= end_date
                )
            ).order_by(UnifiedBoxMetrics.metric_date.asc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_latest_for_box(db: AsyncSession, box_id: UUID) -> Optional[UnifiedBoxMetrics]:
        """Get the latest metrics for a box"""
        result = await db.execute(
            select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == box_id
            ).order_by(UnifiedBoxMetrics.metric_date.desc()).limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_latest_for_all_boxes(
        db: AsyncSession,
        target_date: Optional[date] = None
    ) -> List[UnifiedBoxMetrics]:
        """
        Get latest metrics for all boxes, optionally filtered by date
        
        If target_date is provided, gets metrics for that date.
        Otherwise, gets the most recent metrics for each box.
        """
        if target_date:
            # Get metrics for specific date
            result = await db.execute(
                select(UnifiedBoxMetrics).where(
                    UnifiedBoxMetrics.metric_date == target_date
                ).order_by(UnifiedBoxMetrics.unified_volume_7d_ema.desc().nulls_last())
            )
        else:
            # Get latest metrics for each box (most recent date per box)
            # Subquery to get max date per box
            subquery = (
                select(
                    UnifiedBoxMetrics.booster_box_id,
                    func.max(UnifiedBoxMetrics.metric_date).label("max_date")
                )
                .group_by(UnifiedBoxMetrics.booster_box_id)
                .subquery()
            )
            
            # Join to get the actual metrics
            result = await db.execute(
                select(UnifiedBoxMetrics)
                .join(
                    subquery,
                    and_(
                        UnifiedBoxMetrics.booster_box_id == subquery.c.booster_box_id,
                        UnifiedBoxMetrics.metric_date == subquery.c.max_date
                    )
                )
                .order_by(UnifiedBoxMetrics.unified_volume_7d_ema.desc().nulls_last())
            )
        
        return list(result.scalars().all())
    
    @staticmethod
    async def get_rank_history(
        db: AsyncSession,
        box_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[dict]:
        """
        Get rank history for a box over a date range
        
        Returns list of dicts with date, rank, and rank_change
        """
        # Get all metrics for the date range, ordered by date
        metrics = await UnifiedMetricsRepository.get_by_box_date_range(
            db, box_id, start_date, end_date
        )
        
        if not metrics:
            return []
        
        # Use stored current_rank from metrics (much faster than calculating)
        rank_history = []
        
        for metric in metrics:
            # Use stored rank if available, otherwise calculate (fallback)
            rank = metric.current_rank
            
            if rank is None:
                # Fallback: calculate rank (expensive query)
                result = await db.execute(
                    select(func.count(UnifiedBoxMetrics.id))
                    .where(
                        and_(
                            UnifiedBoxMetrics.metric_date == metric.metric_date,
                            UnifiedBoxMetrics.unified_volume_7d_ema.isnot(None),
                            or_(
                                UnifiedBoxMetrics.unified_volume_7d_ema > metric.unified_volume_7d_ema,
                                and_(
                                    UnifiedBoxMetrics.unified_volume_7d_ema == metric.unified_volume_7d_ema,
                                    UnifiedBoxMetrics.booster_box_id < box_id  # Tiebreaker
                                )
                            )
                        )
                    )
                )
                rank = result.scalar() + 1  # +1 because rank starts at 1
            
            # Use stored rank_change if available, otherwise calculate from previous
            rank_change = metric.rank_change
            if rank_change is None and rank_history:
                previous_rank = rank_history[-1]["rank"]
                rank_change = previous_rank - rank  # Positive = moved up, negative = moved down
            
            rank_history.append({
                "date": metric.metric_date,
                "rank": rank,
                "rank_change": rank_change
            })
        
        return rank_history
    
    @staticmethod
    async def get_sparkline_data(
        db: AsyncSession,
        box_id: UUID,
        days: int = 7
    ) -> List[dict]:
        """
        Get sparkline price data for a box
        
        Returns list of dicts with timestamp and price for the last N days
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        metrics = await UnifiedMetricsRepository.get_by_box_date_range(
            db, box_id, start_date, end_date
        )
        
        sparkline_data = []
        for metric in metrics:
            if metric.floor_price_usd:
                sparkline_data.append({
                    "timestamp": datetime.combine(metric.metric_date, datetime.min.time()),
                    "price": metric.floor_price_usd
                })
        
        return sparkline_data

