"""
Leaderboard Response Schemas
Pydantic models for leaderboard and ranking endpoints
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class BoxMetricsSummary(BaseModel):
    """Summary metrics for leaderboard view"""
    
    floor_price_usd: Optional[Decimal] = None
    floor_price_1d_change_pct: Optional[Decimal] = None
    daily_volume_usd: Optional[Decimal] = None
    unified_volume_7d_ema: Optional[Decimal] = None
    units_sold_count: Optional[int] = None
    active_listings_count: Optional[int] = None
    listed_percentage: Optional[Decimal] = None
    estimated_total_supply: Optional[int] = None
    liquidity_score: Optional[Decimal] = None
    days_to_20pct_increase: Optional[Decimal] = None
    expected_days_to_sell: Optional[Decimal] = None
    price_sparkline_1d: Optional[List[dict]] = None  # Array of {timestamp, price}
    
    model_config = ConfigDict(from_attributes=True)


class LeaderboardBoxResponse(BaseModel):
    """Individual box in leaderboard response"""
    
    id: UUID
    rank: int = Field(..., ge=1, description="Current rank position")
    rank_change_direction: Optional[str] = Field(None, pattern="^(up|down|same)$")
    rank_change_amount: Optional[int] = None
    product_name: str
    set_name: Optional[str] = None
    game_type: Optional[str] = None
    image_url: Optional[str] = None
    metrics: BoxMetricsSummary
    reprint_risk: str = Field(default="LOW", pattern="^(LOW|MEDIUM|HIGH)$")
    metric_date: date
    
    model_config = ConfigDict(from_attributes=True)


class ResponseMeta(BaseModel):
    """Metadata for paginated responses"""
    
    total: int = Field(..., ge=0)
    sort: str = "unified_volume_7d_ema"
    sort_direction: str = Field(default="desc", pattern="^(asc|desc)$")
    date: Optional[date] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class LeaderboardResponse(BaseModel):
    """Full leaderboard response"""
    
    data: List[LeaderboardBoxResponse]
    meta: ResponseMeta


class SparklineDataPoint(BaseModel):
    """Single sparkline data point"""
    
    timestamp: datetime
    price: Decimal
    
    model_config = ConfigDict(from_attributes=True)

