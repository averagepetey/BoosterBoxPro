"""
Leaderboard Service
Handles ranking, sorting, and rank change calculations
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.models.booster_box import BoosterBox
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository


class LeaderboardService:
    """Service for leaderboard ranking and sorting"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_ranked_boxes(
        self,
        target_date: Optional[date] = None,
        sort_by: str = "unified_volume_7d_ema",
        sort_direction: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> List[Tuple[BoosterBox, UnifiedBoxMetrics, int, Optional[dict]]]:
        """
        Get ranked list of boxes with metrics and rank information
        
        Args:
            target_date: Date to rank for (None = latest for each box)
            sort_by: Field to sort by (default: unified_volume_7d_ema)
            sort_direction: "asc" or "desc"
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of tuples: (BoosterBox, UnifiedBoxMetrics, rank, rank_change_info)
        """
        # Get latest metrics for all boxes
        metrics_list = await UnifiedMetricsRepository.get_latest_for_all_boxes(
            self.db, target_date
        )
        
        if not metrics_list:
            return []
        
        # Sort metrics
        reverse = sort_direction.lower() == "desc"
        
        if sort_by == "unified_volume_7d_ema":
            metrics_list.sort(
                key=lambda m: m.unified_volume_7d_ema or Decimal('0'),
                reverse=reverse
            )
        elif sort_by == "liquidity_score":
            metrics_list.sort(
                key=lambda m: m.liquidity_score or Decimal('0'),
                reverse=reverse
            )
        elif sort_by == "floor_price_usd":
            metrics_list.sort(
                key=lambda m: m.floor_price_usd or Decimal('0'),
                reverse=reverse
            )
        elif sort_by == "active_listings_count":
            metrics_list.sort(
                key=lambda m: m.active_listings_count or 0,
                reverse=reverse
            )
        else:
            # Default to volume EMA
            metrics_list.sort(
                key=lambda m: m.unified_volume_7d_ema or Decimal('0'),
                reverse=True
            )
        
        # Get boxes for these metrics
        box_ids = [m.booster_box_id for m in metrics_list]
        
        result = await self.db.execute(
            select(BoosterBox)
            .where(BoosterBox.id.in_(box_ids))
        )
        boxes = {box.id: box for box in result.scalars().all()}
        
        # Combine boxes with metrics and calculate ranks
        ranked_results = []
        for idx, metrics in enumerate(metrics_list[offset:offset+limit]):
            rank = offset + idx + 1
            box = boxes.get(metrics.booster_box_id)
            
            if not box:
                continue
            
            # Calculate rank change if we have previous date
            rank_change_info = None
            if target_date:
                rank_change_info = await self._calculate_rank_change(
                    box.id,
                    target_date
                )
            
            ranked_results.append((box, metrics, rank, rank_change_info))
        
        return ranked_results
    
    async def _calculate_rank_change(
        self,
        box_id: UUID,
        current_date: date
    ) -> Optional[dict]:
        """
        Calculate rank change for a box
        
        Compares current rank to previous period's rank
        
        Returns:
            Dict with direction ("up", "down", "same") and amount (int)
        """
        from datetime import timedelta
        
        # Get current rank
        current_metrics_list = await UnifiedMetricsRepository.get_latest_for_all_boxes(
            self.db, current_date
        )
        
        if not current_metrics_list:
            return None
        
        # Find current rank
        current_rank = None
        for idx, m in enumerate(current_metrics_list):
            if m.booster_box_id == box_id:
                current_rank = idx + 1
                break
        
        if current_rank is None:
            return None
        
        # Get previous date (yesterday or previous available date)
        previous_date = current_date - timedelta(days=1)
        previous_metrics_list = await UnifiedMetricsRepository.get_latest_for_all_boxes(
            self.db, previous_date
        )
        
        if not previous_metrics_list:
            return {
                "direction": "same",
                "amount": 0
            }
        
        # Find previous rank
        previous_rank = None
        for idx, m in enumerate(previous_metrics_list):
            if m.booster_box_id == box_id:
                previous_rank = idx + 1
                break
        
        if previous_rank is None:
            return {
                "direction": "same",
                "amount": 0
            }
        
        # Calculate change
        rank_change = previous_rank - current_rank
        
        if rank_change > 0:
            direction = "up"
        elif rank_change < 0:
            direction = "down"
        else:
            direction = "same"
        
        return {
            "direction": direction,
            "amount": abs(rank_change)
        }
    
    async def get_box_rank(
        self,
        box_id: UUID,
        target_date: Optional[date] = None
    ) -> Optional[int]:
        """
        Get current rank for a specific box
        
        Args:
            box_id: Box UUID
            target_date: Date to get rank for (None = latest)
            
        Returns:
            Rank (1-based) or None if not found
        """
        ranked_results = await self.get_ranked_boxes(
            target_date=target_date,
            limit=1000  # Get all to find rank
        )
        
        for box, metrics, rank, _ in ranked_results:
            if box.id == box_id:
                return rank
        
        return None

