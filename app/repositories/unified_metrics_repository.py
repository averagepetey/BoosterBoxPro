"""
Unified Metrics Repository
Data access layer for unified metrics operations
"""

from uuid import UUID
from datetime import date
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
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

