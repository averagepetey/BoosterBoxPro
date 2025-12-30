"""
Leaderboard Service
Handles ranking, sorting, and rank change calculations with caching
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
from app.services.cache_service import get_cache_service


class LeaderboardService:
    """Service for leaderboard ranking and sorting with Redis caching"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = get_cache_service()
    
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
        # Note: Caching is handled at the router level for better performance
        # This service just returns the raw data tuples
        
        # Cache miss - query database
        # Use optimized SQL query that already orders by volume_7d_ema when sorting by that
        sql_already_sorted = (
            target_date is not None and 
            sort_by == "unified_volume_7d_ema" and 
            sort_direction == "desc"
        )
        
        # Get latest metrics for all boxes (with SQL ordering if applicable)
        if sql_already_sorted:
            metrics_list = await UnifiedMetricsRepository.get_latest_for_all_boxes(
                self.db, target_date
            )
            # SQL already sorted by unified_volume_7d_ema DESC, no need to sort again
        else:
            metrics_list = await UnifiedMetricsRepository.get_latest_for_all_boxes(
                self.db, target_date
            )
            
            if not metrics_list:
                return []
            
            # Sort metrics in Python (only when SQL didn't already sort)
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
        
        if not metrics_list:
            return []
        
        # Get boxes for these metrics (limit query to what we need)
        metrics_to_fetch = metrics_list[offset:offset+limit]
        box_ids = [m.booster_box_id for m in metrics_to_fetch]
        
        result = await self.db.execute(
            select(BoosterBox).where(BoosterBox.id.in_(box_ids))
        )
        boxes = {box.id: box for box in result.scalars().all()}
        
        # Combine boxes with metrics and use stored rank data
        ranked_results = []
        for idx, metrics in enumerate(metrics_to_fetch):
            rank = offset + idx + 1
            box = boxes.get(metrics.booster_box_id)
            
            if not box:
                continue
            
            # Use stored rank_change from metrics instead of calculating
            rank_change_info = None
            if metrics.rank_change is not None:
                if metrics.rank_change > 0:
                    direction = "up"
                elif metrics.rank_change < 0:
                    direction = "down"
                else:
                    direction = "same"
                rank_change_info = {
                    "direction": direction,
                    "amount": abs(metrics.rank_change)
                }
            
            ranked_results.append((box, metrics, rank, rank_change_info))
        
        # Note: Caching is handled at the router level after formatting
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

