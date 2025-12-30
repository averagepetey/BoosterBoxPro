"""
Box Detail Response Schemas
Pydantic models for box detail and analytics endpoints
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.leaderboard import LeaderboardBoxResponse, BoxMetricsSummary


class TimeSeriesDataPoint(BaseModel):
    """Single time-series data point"""
    
    date: date
    floor_price_usd: Optional[Decimal] = None
    volume: Optional[Decimal] = None
    listings_count: Optional[int] = None
    sales_count: Optional[int] = None
    market_cap: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


class RankHistoryPoint(BaseModel):
    """Single rank history point"""
    
    date: date
    rank: int
    rank_change: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class BoxDetailMetrics(BoxMetricsSummary):
    """Extended metrics for box detail view"""
    
    visible_market_cap_usd: Optional[Decimal] = None
    absorption_rate: Optional[Decimal] = None
    momentum_score: Optional[Decimal] = None
    boxes_sold_per_day: Optional[Decimal] = None
    boxes_sold_30d_avg: Optional[Decimal] = None
    unified_volume_30d_sma: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


class BoxDetailResponse(BaseModel):
    """Full box detail response with advanced analytics"""
    
    # Basic info (from LeaderboardBoxResponse)
    id: UUID
    product_name: str
    set_name: Optional[str] = None
    game_type: Optional[str] = None
    image_url: Optional[str] = None
    release_date: Optional[date] = None
    reprint_risk: str
    estimated_total_supply: Optional[int] = None
    
    # Current metrics
    rank: Optional[int] = None
    rank_change_direction: Optional[str] = None
    rank_change_amount: Optional[int] = None
    metrics: BoxDetailMetrics
    metric_date: date
    
    # Advanced analytics
    time_series_data: Optional[List[TimeSeriesDataPoint]] = None
    rank_history: Optional[List[RankHistoryPoint]] = None
    
    model_config = ConfigDict(from_attributes=True)

