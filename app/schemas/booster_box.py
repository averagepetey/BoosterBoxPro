"""
BoosterBox Pydantic Schemas
Request and response models for booster box endpoints
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class BoosterBoxCreate(BaseModel):
    """Schema for creating a new booster box"""
    
    product_name: str = Field(..., min_length=1, max_length=500, description="Full product name")
    set_name: Optional[str] = Field(None, max_length=255, description="Set name")
    game_type: Optional[str] = Field("One Piece", max_length=100, description="Game type (default: One Piece)")
    release_date: Optional[date] = Field(None, description="Release date")
    image_url: Optional[str] = Field(None, max_length=500, description="URL to box image")
    estimated_total_supply: Optional[int] = Field(None, ge=0, description="Estimated total supply")
    reprint_risk: Optional[str] = Field("LOW", pattern="^(LOW|MEDIUM|HIGH)$", description="Reprint risk level")
    external_product_id: Optional[str] = Field(None, max_length=255, description="External product ID (for future API integration)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_name": "One Piece - OP-01 Romance Dawn Booster Box",
                "set_name": "Romance Dawn",
                "game_type": "One Piece",
                "release_date": "2023-03-31",
                "image_url": "https://example.com/op01.jpg",
                "estimated_total_supply": 36600,
                "reprint_risk": "LOW"
            }
        }
    )


class BoosterBoxResponse(BaseModel):
    """Schema for booster box response"""
    
    id: UUID
    external_product_id: Optional[str] = None
    product_name: str
    set_name: Optional[str] = None
    game_type: Optional[str] = None
    release_date: Optional[date] = None
    image_url: Optional[str] = None
    estimated_total_supply: Optional[int] = None
    reprint_risk: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class BoosterBoxListResponse(BaseModel):
    """Schema for list of booster boxes"""
    
    boxes: list[BoosterBoxResponse]
    total: int

