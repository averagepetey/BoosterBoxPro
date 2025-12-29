"""
Metrics Pydantic Schemas
Request and response models for metrics endpoints
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ManualMetricsInput(BaseModel):
    """Schema for manual metrics entry"""
    
    booster_box_id: UUID = Field(..., description="Booster box UUID")
    metric_date: date = Field(..., description="Date for these metrics")
    
    # Floor price (TCGplayer)
    floor_price_usd: Optional[Decimal] = Field(None, ge=0, description="Floor price in USD")
    active_listings_count: Optional[int] = Field(None, ge=0, description="Active listings count")
    
    # Volume (can be direct entry in manual mode)
    daily_volume_usd: Optional[Decimal] = Field(None, ge=0, description="Daily volume in USD")
    units_sold_count: Optional[int] = Field(None, ge=0, description="Units sold count")
    
    # Additional metrics (optional)
    visible_market_cap_usd: Optional[Decimal] = Field(None, ge=0, description="Visible market cap")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "booster_box_id": "550e8400-e29b-41d4-a716-446655440001",
                "metric_date": "2024-01-15",
                "floor_price_usd": 245.99,
                "active_listings_count": 3044,
                "daily_volume_usd": 45230.50,
                "units_sold_count": 18,
                "visible_market_cap_usd": 748476.56
            }
        }
    )


class BulkManualMetricsInput(BaseModel):
    """Schema for bulk metrics entry"""
    
    metrics: list[ManualMetricsInput] = Field(..., min_length=1, description="Array of metrics to insert")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metrics": [
                    {
                        "booster_box_id": "550e8400-e29b-41d4-a716-446655440001",
                        "metric_date": "2024-01-15",
                        "floor_price_usd": 245.99,
                        "active_listings_count": 3044,
                        "daily_volume_usd": 45230.50
                    }
                ]
            }
        }
    )


class MetricsResponse(BaseModel):
    """Schema for metrics response"""
    
    id: UUID
    booster_box_id: UUID
    metric_date: date
    floor_price_usd: Optional[Decimal] = None
    active_listings_count: Optional[int] = None
    unified_volume_usd: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

