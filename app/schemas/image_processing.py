"""
Image Processing Schemas
Pydantic models for screenshot-based manual entry
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ScreenshotUploadRequest(BaseModel):
    """Request schema for screenshot upload"""
    
    box_id: Optional[str] = Field(None, description="Optional box UUID if known")
    box_name: Optional[str] = Field(None, description="Optional box name to help identify")
    metric_date: Optional[str] = Field(None, description="Optional date for metrics (YYYY-MM-DD)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "box_name": "OP-01 Romance Dawn",
                "metric_date": "2024-01-15"
            }
        }
    )


class ScreenshotProcessingResponse(BaseModel):
    """Response after initial screenshot processing"""
    
    processing_id: str = Field(..., description="Unique ID for this processing session")
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Extracted data (if OCR available)")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score for extraction")
    needs_review: bool = Field(True, description="Whether manual review/confirmation is needed")
    suggested_values: Optional[Dict[str, Any]] = Field(None, description="Suggested values for manual entry")
    message: str = Field(..., description="Status message")
    
    model_config = ConfigDict(from_attributes=True)


class ManualExtractionSubmission(BaseModel):
    """Schema for submitting manually extracted values after viewing screenshot"""
    
    processing_id: str = Field(..., description="Processing ID from screenshot upload")
    booster_box_id: str = Field(..., description="Booster box UUID")
    metric_date: str = Field(..., description="Date for metrics (YYYY-MM-DD)")
    floor_price_usd: float = Field(..., ge=0, description="Floor price in USD")
    active_listings_count: int = Field(..., ge=0, description="Active listings count")
    daily_volume_usd: Optional[float] = Field(None, ge=0, description="Daily volume in USD")
    units_sold_count: Optional[int] = Field(None, ge=0, description="Units sold count")
    visible_market_cap_usd: Optional[float] = Field(None, ge=0, description="Visible market cap in USD")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processing_id": "abc123",
                "booster_box_id": "550e8400-e29b-41d4-a716-446655440001",
                "metric_date": "2024-01-15",
                "floor_price_usd": 245.99,
                "active_listings_count": 3044,
                "daily_volume_usd": 45230.50,
                "units_sold_count": 18
            }
        }
    )

