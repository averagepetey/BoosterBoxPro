"""
Duplicate Detection Service
Checks if incoming data duplicates existing data and identifies differences
"""

from datetime import date
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox


class DuplicateDetectionService:
    """Service for detecting duplicate data entries"""
    
    async def check_duplicate(
        self,
        db: AsyncSession,
        booster_box_id: UUID,
        metric_date: date,
        new_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if data already exists for this box and date, and compare values
        
        Args:
            db: Database session
            booster_box_id: UUID of the booster box
            metric_date: Date for the metrics
            new_data: New data to check against existing
            
        Returns:
            Dictionary with duplicate status and comparison results
        """
        # Query for existing metrics
        stmt = select(UnifiedBoxMetrics).where(
            UnifiedBoxMetrics.booster_box_id == booster_box_id,
            UnifiedBoxMetrics.metric_date == metric_date
        )
        result = await db.execute(stmt)
        existing_metrics = result.scalar_one_or_none()
        
        if not existing_metrics:
            return {
                "is_duplicate": False,
                "existing_data": None,
                "differences": {},
                "message": "No existing data found for this date. This is new data."
            }
        
        # Convert existing data to dict for comparison
        existing_data = {
            "floor_price_usd": float(existing_metrics.floor_price_usd) if existing_metrics.floor_price_usd else None,
            "active_listings_count": existing_metrics.active_listings_count,
            "boxes_sold_per_day": float(existing_metrics.boxes_sold_per_day) if existing_metrics.boxes_sold_per_day else None,
            "unified_volume_usd": float(existing_metrics.unified_volume_usd) if existing_metrics.unified_volume_usd else None,
            "visible_market_cap_usd": float(existing_metrics.visible_market_cap_usd) if existing_metrics.visible_market_cap_usd else None,
            "boxes_added_today": existing_metrics.boxes_added_today,
        }
        
        # Compare fields
        differences = {}
        is_duplicate = True
        
        # Fields to compare
        comparison_fields = {
            "floor_price_usd": ("floor_price_usd", 0.01),  # (new_key, tolerance)
            "active_listings_count": ("active_listings_count", 0),
            "boxes_sold_today": ("boxes_sold_per_day", 0),
            "daily_volume_usd": ("unified_volume_usd", 0.01),
            "visible_market_cap_usd": ("visible_market_cap_usd", 0.01),
            "boxes_added_today": ("boxes_added_today", 0),
        }
        
        for new_key, (existing_key, tolerance) in comparison_fields.items():
            new_value = new_data.get(new_key)
            existing_value = existing_data.get(existing_key)
            
            # Skip if both are None
            if new_value is None and existing_value is None:
                continue
            
            # If one is None and the other isn't, it's different
            if new_value is None or existing_value is None:
                differences[new_key] = {
                    "existing": existing_value,
                    "new": new_value,
                    "changed": True
                }
                is_duplicate = False
                continue
            
            # Compare numeric values with tolerance
            if isinstance(new_value, (int, float)) and isinstance(existing_value, (int, float)):
                diff = abs(new_value - existing_value)
                if diff > tolerance:
                    differences[new_key] = {
                        "existing": existing_value,
                        "new": new_value,
                        "difference": diff,
                        "changed": True
                    }
                    is_duplicate = False
        
        if is_duplicate:
            message = "Data already exists and matches existing values. No update needed."
        else:
            changed_fields = list(differences.keys())
            message = f"Data exists but differs in: {', '.join(changed_fields)}"
        
        return {
            "is_duplicate": is_duplicate,
            "existing_data": existing_data,
            "differences": differences,
            "message": message
        }


# Global service instance
duplicate_detection_service = DuplicateDetectionService()

