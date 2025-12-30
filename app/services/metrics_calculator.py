"""
Unified Metrics Calculator Service
Calculates derived metrics from manual entry data
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.services.ema_calculator import EMACalculator
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.models.unified_box_metrics import UnifiedBoxMetrics


class MetricsCalculator:
    """Service for calculating unified metrics from manual entry data"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ema_calculator = EMACalculator()
    
    async def calculate_volume_ema(
        self,
        box_id: UUID,
        target_date: date,
        window_days: int = 7
    ) -> Optional[Decimal]:
        """
        Calculate EMA of volume for a specific box and date
        
        Gets historical volume data and calculates EMA
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate EMA for
            window_days: Window size for EMA (default: 7)
            
        Returns:
            EMA value or None if insufficient data
        """
        # Get historical volume data up to target_date
        # We need at least window_days of data
        start_date = target_date - timedelta(days=30)  # Get up to 30 days back
        
        result = await self.db.execute(
            select(UnifiedBoxMetrics.unified_volume_usd)
            .where(
                and_(
                    UnifiedBoxMetrics.booster_box_id == box_id,
                    UnifiedBoxMetrics.metric_date <= target_date,
                    UnifiedBoxMetrics.metric_date >= start_date,
                    UnifiedBoxMetrics.unified_volume_usd.isnot(None)
                )
            )
            .order_by(UnifiedBoxMetrics.metric_date.asc())
        )
        
        volumes = [row[0] for row in result.all()]
        
        if len(volumes) < window_days:
            return None
        
        # Calculate EMA
        if window_days == 7:
            return self.ema_calculator.calculate_volume_ema_7d(volumes)
        else:
            return self.ema_calculator.calculate_ema(volumes, window=window_days)
    
    async def calculate_volume_sma_30d(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[Decimal]:
        """
        Calculate 30-day SMA of volume
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate SMA for
            
        Returns:
            30-day SMA value or None if insufficient data
        """
        start_date = target_date - timedelta(days=30)
        
        result = await self.db.execute(
            select(UnifiedBoxMetrics.unified_volume_usd)
            .where(
                and_(
                    UnifiedBoxMetrics.booster_box_id == box_id,
                    UnifiedBoxMetrics.metric_date <= target_date,
                    UnifiedBoxMetrics.metric_date >= start_date,
                    UnifiedBoxMetrics.unified_volume_usd.isnot(None)
                )
            )
            .order_by(UnifiedBoxMetrics.metric_date.asc())
        )
        
        volumes = [row[0] for row in result.all()]
        
        return self.ema_calculator.calculate_volume_sma_30d(volumes)
    
    async def calculate_absorption_rate(
        self,
        box_id: UUID,
        target_date: date
    ) -> Decimal:
        """
        Calculate absorption rate
        
        Formula: absorption_rate = boxes_sold_per_day / active_listings_count
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate for
            
        Returns:
            Absorption rate (0.0 to 1.0)
        """
        # Get metrics for target date
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if not metrics:
            return Decimal('0')
        
        # Get boxes sold per day (or calculate from volume)
        boxes_sold = metrics.boxes_sold_per_day
        active_listings = metrics.active_listings_count
        
        if not boxes_sold or boxes_sold <= 0:
            return Decimal('0')
        
        if not active_listings or active_listings <= 0:
            return Decimal('0')
        
        # Calculate absorption rate
        absorption_rate = Decimal(str(boxes_sold)) / Decimal(str(active_listings))
        
        # Bound to 0.0-1.0 (can't absorb more than 100%)
        return min(absorption_rate, Decimal('1.0'))
    
    async def calculate_liquidity_score(
        self,
        box_id: UUID,
        target_date: date,
        max_expected_listings: int = 5000
    ) -> Decimal:
        """
        Calculate liquidity score (simplified for manual mode)
        
        Formula: absorption_rate × 0.5 + (normalized_listings_count × 0.3) + (volume_velocity × 0.2)
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate for
            max_expected_listings: Maximum expected listings for normalization (default: 5000)
            
        Returns:
            Liquidity score (0.0 to 1.0)
        """
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if not metrics:
            return Decimal('0')
        
        # 1. Absorption rate (50% weight)
        absorption_rate = await self.calculate_absorption_rate(box_id, target_date)
        absorption_component = absorption_rate * Decimal('0.5')
        
        # 2. Normalized listings count (30% weight)
        active_listings = metrics.active_listings_count or 0
        normalized_listings = min(
            Decimal(str(active_listings)) / Decimal(str(max_expected_listings)),
            Decimal('1.0')
        )
        listings_component = normalized_listings * Decimal('0.3')
        
        # 3. Volume velocity (20% weight) - normalized 7-day EMA
        volume_ema = await self.calculate_volume_ema(box_id, target_date, window_days=7)
        
        # Normalize volume EMA (assume max volume of $100,000 for normalization)
        max_volume = Decimal('100000')
        if volume_ema:
            volume_velocity = min(
                volume_ema / max_volume,
                Decimal('1.0')
            )
        else:
            volume_velocity = Decimal('0')
        
        volume_component = volume_velocity * Decimal('0.2')
        
        # Sum components
        liquidity_score = absorption_component + listings_component + volume_component
        
        # Bound to 0.0-1.0
        return max(Decimal('0'), min(liquidity_score, Decimal('1.0')))
    
    async def calculate_boxes_sold_30d_avg(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[Decimal]:
        """
        Calculate 30-day average of boxes sold per day
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate for
            
        Returns:
            30-day average boxes sold per day or None if insufficient data
        """
        start_date = target_date - timedelta(days=30)
        
        result = await self.db.execute(
            select(UnifiedBoxMetrics.boxes_sold_per_day)
            .where(
                and_(
                    UnifiedBoxMetrics.booster_box_id == box_id,
                    UnifiedBoxMetrics.metric_date <= target_date,
                    UnifiedBoxMetrics.metric_date >= start_date,
                    UnifiedBoxMetrics.boxes_sold_per_day.isnot(None)
                )
            )
            .order_by(UnifiedBoxMetrics.metric_date.asc())
        )
        
        boxes_sold_values = [row[0] for row in result.all()]
        
        if not boxes_sold_values:
            return None
        
        # Calculate average
        total = sum(boxes_sold_values)
        avg = total / Decimal(str(len(boxes_sold_values)))
        
        return avg
    
    async def calculate_expected_days_to_sell(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[Decimal]:
        """
        Calculate expected days to sell if listed today
        
        Formula: expected_days_to_sell = active_listings_count / boxes_sold_per_day_avg
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate for
            
        Returns:
            Expected days to sell (1-365) or None if insufficient data
        """
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if not metrics:
            return None
        
        active_listings = metrics.active_listings_count or 0
        if active_listings <= 0:
            return None
        
        # Get average boxes sold per day from last 30 days
        boxes_sold_avg = await self.calculate_boxes_sold_30d_avg(box_id, target_date)
        
        if not boxes_sold_avg or boxes_sold_avg <= 0:
            return None
        
        # Calculate expected days
        expected_days = Decimal(str(active_listings)) / boxes_sold_avg
        
        # Bound to 1-365 days
        expected_days = max(Decimal('1'), min(expected_days, Decimal('365')))
        
        return expected_days
    
    async def calculate_visible_market_cap(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[Decimal]:
        """
        Calculate visible market cap
        
        Formula: visible_market_cap = floor_price_usd × active_listings_count
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate for
            
        Returns:
            Visible market cap in USD or None
        """
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if not metrics:
            return None
        
        floor_price = metrics.floor_price_usd
        active_listings = metrics.active_listings_count or 0
        
        if not floor_price or active_listings <= 0:
            return None
        
        return floor_price * Decimal(str(active_listings))
    
    async def calculate_all_metrics(
        self,
        box_id: UUID,
        target_date: date
    ) -> dict:
        """
        Calculate all derived metrics for a box on a specific date
        
        This is the main method that calculates and returns all metrics
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate metrics for
            
        Returns:
            Dictionary with all calculated metrics
        """
        results = {}
        
        # Volume EMAs
        results['unified_volume_7d_ema'] = await self.calculate_volume_ema(
            box_id, target_date, window_days=7
        )
        results['unified_volume_30d_sma'] = await self.calculate_volume_sma_30d(
            box_id, target_date
        )
        
        # Other metrics
        results['absorption_rate'] = await self.calculate_absorption_rate(
            box_id, target_date
        )
        results['liquidity_score'] = await self.calculate_liquidity_score(
            box_id, target_date
        )
        results['boxes_sold_30d_avg'] = await self.calculate_boxes_sold_30d_avg(
            box_id, target_date
        )
        results['expected_days_to_sell'] = await self.calculate_expected_days_to_sell(
            box_id, target_date
        )
        results['visible_market_cap_usd'] = await self.calculate_visible_market_cap(
            box_id, target_date
        )
        
        return results
    
    async def update_metrics_with_calculations(
        self,
        box_id: UUID,
        target_date: date
    ) -> UnifiedBoxMetrics:
        """
        Calculate all metrics and update the database record
        
        This is the main method to call after manual entry to update calculated fields
        
        Args:
            box_id: Booster box UUID
            target_date: Date to calculate and update metrics for
            
        Returns:
            Updated UnifiedBoxMetrics record
        """
        # Get existing metrics
        metrics = await UnifiedMetricsRepository.get_by_box_and_date(
            self.db, box_id, target_date
        )
        
        if not metrics:
            raise ValueError(f"No metrics found for box {box_id} on {target_date}")
        
        # Calculate all derived metrics
        calculated = await self.calculate_all_metrics(box_id, target_date)
        
        # Update metrics with calculated values
        update_data = {
            'unified_volume_7d_ema': calculated.get('unified_volume_7d_ema'),
            'unified_volume_30d_sma': calculated.get('unified_volume_30d_sma'),
            'liquidity_score': calculated.get('liquidity_score'),
            'boxes_sold_30d_avg': calculated.get('boxes_sold_30d_avg'),
            'expected_days_to_sell': calculated.get('expected_days_to_sell'),
            'visible_market_cap_usd': calculated.get('visible_market_cap_usd'),
        }
        
        # Update existing record
        for key, value in update_data.items():
            if value is not None:
                setattr(metrics, key, value)
        
        await self.db.commit()
        await self.db.refresh(metrics)
        
        return metrics

