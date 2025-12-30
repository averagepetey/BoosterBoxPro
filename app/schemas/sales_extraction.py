"""
Sales and Listing Extraction Schemas
For extracting individual sales and listing data from TCGplayer screenshots
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class IndividualSaleExtraction(BaseModel):
    """Schema for extracting individual sale data from screenshot"""
    
    processing_id: str = Field(..., description="Processing ID from screenshot upload")
    booster_box_id: str = Field(..., description="Booster box UUID")
    sale_date: str = Field(..., description="Date of sale (YYYY-MM-DD)")
    sold_price_usd: float = Field(..., ge=0, description="Price the box sold for")
    quantity: int = Field(1, ge=1, description="Number of boxes sold (usually 1 for booster boxes)")
    seller_id: Optional[str] = Field(None, description="Seller ID/username (if visible)")
    listing_type: Optional[str] = Field(None, description="Listing type (e.g., 'Buy It Now', 'Auction')")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processing_id": "abc123",
                "booster_box_id": "550e8400-e29b-41d4-a716-446655440001",
                "sale_date": "2024-01-15",
                "sold_price_usd": 245.99,
                "quantity": 1,
                "seller_id": "seller123",
                "listing_type": "Buy It Now"
            }
        }
    )


class ListingDataExtraction(BaseModel):
    """Schema for extracting listing data from screenshot"""
    
    processing_id: str = Field(..., description="Processing ID from screenshot upload")
    booster_box_id: str = Field(..., description="Booster box UUID")
    snapshot_date: str = Field(..., description="Date of listing snapshot (YYYY-MM-DD)")
    listings: List[dict] = Field(..., description="Array of individual listings")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processing_id": "abc123",
                "booster_box_id": "550e8400-e29b-41d4-a716-446655440001",
                "snapshot_date": "2024-01-15",
                "listings": [
                    {
                        "listing_id": "listing123",
                        "listed_price_usd": 245.99,
                        "quantity": 5,
                        "seller_id": "seller1"
                    },
                    {
                        "listing_id": "listing456",
                        "listed_price_usd": 248.50,
                        "quantity": 3,
                        "seller_id": "seller2"
                    }
                ]
            }
        }
    )


class ListingItem(BaseModel):
    """Individual listing item"""
    
    listing_id: Optional[str] = Field(None, description="Listing ID (if visible)")
    listed_price_usd: float = Field(..., ge=0, description="Listed price in USD")
    quantity: int = Field(1, ge=1, description="Quantity available")
    seller_id: Optional[str] = Field(None, description="Seller ID (if visible)")


class BulkSalesExtraction(BaseModel):
    """Schema for extracting multiple sales from a single screenshot"""
    
    processing_id: str = Field(..., description="Processing ID from screenshot upload")
    booster_box_id: str = Field(..., description="Booster box UUID")
    sales: List[dict] = Field(..., description="Array of individual sales")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "processing_id": "abc123",
                "booster_box_id": "550e8400-e29b-41d4-a716-446655440001",
                "sales": [
                    {
                        "sale_date": "2024-01-15",
                        "sold_price_usd": 245.99,
                        "quantity": 1
                    },
                    {
                        "sale_date": "2024-01-14",
                        "sold_price_usd": 242.50,
                        "quantity": 1
                    }
                ]
            }
        }
    )

