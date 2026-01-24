"""
Image Processing Schemas
For screenshot upload and OCR/AI data extraction
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import date


class ScreenshotUploadRequest(BaseModel):
    """Request schema for screenshot upload"""
    # File will be handled as UploadFile in the endpoint
    pass


class ExtractedMetric(BaseModel):
    """A single extracted metric value with confidence"""
    value: Optional[float] = None
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    raw_text: Optional[str] = None
    field_name: str


class ScreenshotProcessingResponse(BaseModel):
    """Response after processing a screenshot"""
    success: bool
    extracted_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured data extracted from screenshot"
    )
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence scores for each extracted field"
    )
    detected_box: Optional[str] = Field(
        None,
        description="Detected box name/product identifier"
    )
    raw_text: Optional[str] = Field(
        None,
        description="Raw OCR text extracted from image"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Any errors encountered during processing"
    )


class ManualExtractionSubmission(BaseModel):
    """User-reviewed and confirmed extracted data to save"""
    booster_box_id: str = Field(..., description="UUID of the booster box")
    metric_date: date = Field(..., description="Date for these metrics")
    
    # Core metrics
    floor_price_usd: Optional[float] = None
    active_listings_count: Optional[int] = None
    boxes_sold_today: Optional[int] = None
    daily_volume_usd: Optional[float] = None
    visible_market_cap_usd: Optional[float] = None
    boxes_added_today: Optional[int] = None
    
    # Additional metrics that might be extracted
    estimated_total_supply: Optional[int] = None
    
    # Metadata
    source: str = Field(default="screenshot_upload", description="Data source identifier")
    notes: Optional[str] = None


class DuplicateCheckResponse(BaseModel):
    """Response when checking for duplicate data"""
    is_duplicate: bool
    existing_data: Optional[Dict[str, Any]] = None
    differences: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Fields that differ between existing and new data"
    )
    message: str






