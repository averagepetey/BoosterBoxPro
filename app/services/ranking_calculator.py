"""
Ranking Calculator Service
Calculates ranks and rank changes for booster boxes
"""

from datetime import date, timedelta
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from decimal import Decimal

from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository


class RankingCalculator:
    """Service for calculating and updating ranks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_ranks_for_date(
        self,
        target_date: date
    ) -> Dict[UUID, int]:
        """
        Calculate ranks for all boxes on a specific date
        
        Ranks are based on unified_volume_7d_ema (highest = rank 1)
        Handles ties: boxes with same volume get same rank
        
        Args:
            target_date: Date to calculate ranks for
            
        Returns:
            Dictionary mapping box_id -> rank (1 = highest volume)
        """
        # Get all metrics for this date, ordered by volume DESC
        result = await self.db.execute(
            select(UnifiedBoxMetrics)
            .where(UnifiedBoxMetrics.metric_date == target_date)
            .where(UnifiedBoxMetrics.unified_volume_7d_ema.isnot(None))
            .order_by(desc(UnifiedBoxMetrics.unified_volume_7d_ema))
        )
        
        metrics_list = result.scalars().all()
        
        if not metrics_list:
            return {}
        
        # Assign ranks, handling ties
        ranks = {}
        current_rank = 1
        previous_volume = None
        
        for metrics in metrics_list:
            volume = metrics.unified_volume_7d_ema
            
            # If volume is different from previous, increment rank
            # If same volume, keep same rank (tie)
            if previous_volume is not None and volume != previous_volume:
                # Count how many boxes have this volume or higher
                # This handles ties correctly
                current_rank = len([m for m in metrics_list if m.unified_volume_7d_ema > volume]) + 1
            
            ranks[metrics.booster_box_id] = current_rank
            previous_volume = volume
        
        return ranks
    
    async def calculate_rank_changes(
        self,
        target_date: date
    ) -> Dict[UUID, int]:
        """
        Calculate rank changes for all boxes
        
        Compares current rank to previous period's rank
        
        Args:
            target_date: Date to calculate rank changes for
            
        Returns:
            Dictionary mapping box_id -> rank_change
            Positive = moved up, negative = moved down, 0 = no change
        """
        # Get current ranks
        current_ranks = await self.calculate_ranks_for_date(target_date)
        
        # Get previous date (yesterday)
        previous_date = target_date - timedelta(days=1)
        
        # Get previous ranks from database (if they exist)
        previous_ranks = {}
        result = await self.db.execute(
            select(UnifiedBoxMetrics.booster_box_id, UnifiedBoxMetrics.current_rank)
            .where(UnifiedBoxMetrics.metric_date == previous_date)
            .where(UnifiedBoxMetrics.current_rank.isnot(None))
        )
        
        for row in result.all():
            previous_ranks[row[0]] = row[1]
        
        # Calculate changes
        rank_changes = {}
        for box_id, current_rank in current_ranks.items():
            previous_rank = previous_ranks.get(box_id)
            
            if previous_rank is not None:
                # Calculate change: positive = moved up, negative = moved down
                change = previous_rank - current_rank
                rank_changes[box_id] = change
            else:
                # No previous rank (new box or no data)
                rank_changes[box_id] = 0
        
        return rank_changes
    
    async def update_ranks_for_date(
        self,
        target_date: date
    ) -> int:
        """
        Calculate and update ranks for all boxes on a specific date
        
        This is the main method to call for daily rank updates
        
        Args:
            target_date: Date to update ranks for
            
        Returns:
            Number of boxes with ranks updated
        """
        # Calculate ranks
        ranks = await self.calculate_ranks_for_date(target_date)
        
        if not ranks:
            return 0
        
        # Get previous date for rank change calculation
        previous_date = target_date - timedelta(days=1)
        
        # Get previous ranks from database
        previous_ranks_result = await self.db.execute(
            select(UnifiedBoxMetrics.booster_box_id, UnifiedBoxMetrics.current_rank)
            .where(UnifiedBoxMetrics.metric_date == previous_date)
            .where(UnifiedBoxMetrics.current_rank.isnot(None))
        )
        previous_ranks = {row[0]: row[1] for row in previous_ranks_result.all()}
        
        # Update each box's rank
        updated_count = 0
        for box_id, rank in ranks.items():
            # Get metrics record
            metrics = await UnifiedMetricsRepository.get_by_box_and_date(
                self.db, box_id, target_date
            )
            
            if not metrics:
                continue
            
            # Store previous rank before updating
            previous_rank = previous_ranks.get(box_id)
            if previous_rank is not None:
                metrics.previous_rank = previous_rank
                # Calculate rank change
                metrics.rank_change = previous_rank - rank
            else:
                metrics.previous_rank = None
                metrics.rank_change = None
            
            # Update current rank
            metrics.current_rank = rank
            updated_count += 1
        
        await self.db.commit()
        
        return updated_count
    
    async def get_rank_for_box(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[int]:
        """
        Get current rank for a specific box on a date
        
        Args:
            box_id: Box UUID
            target_date: Date to get rank for
            
        Returns:
            Rank (1 = highest) or None if no metrics/rank
        """
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if not metrics:
            return None
        
        return metrics.current_rank

