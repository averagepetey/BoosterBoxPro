"""
Image Processing Service
Processes screenshots/images to extract metrics data
"""

import base64
from io import BytesIO
from typing import Optional, Dict, Any
from PIL import Image
import pytesseract

# For OCR (optional - can use cloud services like Google Vision API instead)


class ImageProcessor:
    """Service for processing images to extract metrics data"""
    
    @staticmethod
    async def process_screenshot(
        image_bytes: bytes,
        box_name: Optional[str] = None,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process screenshot image to extract metrics data
        
        Args:
            image_bytes: Raw image bytes
            box_name: Optional box name to help identify the box in the image
            date: Optional date for the metrics
            
        Returns:
            Dictionary with extracted data structure:
            {
                "extracted_data": {...},  # Raw extracted fields
                "confidence": 0.0-1.0,    # Confidence score
                "needs_review": bool      # Whether manual review is needed
            }
        """
        try:
            # Load image
            image = Image.open(BytesIO(image_bytes))
            
            # For now, return structure for manual extraction
            # In production, this would use OCR (Tesseract, Google Vision, etc.)
            
            return {
                "extracted_data": None,  # Will be populated by OCR or manual review
                "confidence": 0.0,
                "needs_review": True,
                "image_format": image.format,
                "image_size": image.size,
                "message": "Image received. Please provide extracted values below."
            }
        except Exception as e:
            return {
                "error": str(e),
                "extracted_data": None,
                "confidence": 0.0,
                "needs_review": True
            }
    
    @staticmethod
    async def extract_with_manual_review(
        image_bytes: bytes,
        manual_extraction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process manual extraction data provided after viewing screenshot
        
        Args:
            image_bytes: Original image bytes (for reference)
            manual_extraction: Dictionary with manually extracted values
            
        Returns:
            Validated and structured metrics data
        """
        # Validate and structure the manual extraction
        validated = {
            "floor_price_usd": float(manual_extraction.get("floor_price_usd", 0)),
            "active_listings_count": int(manual_extraction.get("active_listings_count", 0)),
            "daily_volume_usd": manual_extraction.get("daily_volume_usd"),
            "units_sold_count": manual_extraction.get("units_sold_count"),
            "visible_market_cap_usd": manual_extraction.get("visible_market_cap_usd"),
        }
        
        # Remove None values
        validated = {k: v for k, v in validated.items() if v is not None}
        
        return validated

