"""
Image Processing Service
Handles OCR and AI extraction from screenshots
Supports both Anthropic (Claude) and OpenAI APIs
"""

import base64
import os
from typing import Dict, Any, Optional
from io import BytesIO

# Make PIL optional - only needed for admin screenshot feature
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None  # Type stub
    print("⚠️  Pillow not installed. Install with: pip install Pillow (optional - only needed for admin screenshot feature)")

# Make Anthropic optional - preferred for AI screenshot extraction
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None
    print("⚠️  Anthropic not installed. Install with: pip install anthropic (for Claude AI screenshot extraction)")

# Make OpenAI optional - fallback for AI screenshot extraction
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None  # Type stub


class ImageProcessingService:
    """Service for processing images and extracting structured data using Claude (Anthropic) or OpenAI"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self.ai_provider = None
        
        # Prefer Anthropic (Claude) over OpenAI
        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                self.ai_provider = "claude"
                print("✅ Using Claude (Anthropic) for screenshot processing")
            else:
                print("⚠️  ANTHROPIC_API_KEY not set.")
        
        # Fallback to OpenAI if Anthropic not available
        if not self.anthropic_client and OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                self.ai_provider = "openai"
                print("✅ Using OpenAI for screenshot processing")
            else:
                print("⚠️  OPENAI_API_KEY not set.")
        
        if not self.anthropic_client and not self.openai_client:
            print("⚠️  No AI API configured. Screenshot extraction will require manual entry.")
            print("   Set ANTHROPIC_API_KEY for Claude or OPENAI_API_KEY for OpenAI")
    
    def _get_extraction_prompt(self) -> str:
        """Get the prompt for extracting data from screenshots"""
        return """Analyze this screenshot of a TCG marketplace (TCGplayer, eBay, etc.) showing booster box data.

Extract the following information if visible:
1. Product name / Box name (e.g., "OP-01", "One Piece OP-02", etc.)
2. Floor price (lowest listing price in USD)
3. Active listings count (number of listings shown)
4. Boxes sold today (if visible)
5. Daily volume USD (if visible)
6. Visible market cap (if visible)
7. Boxes added today (if visible)
8. Estimated total supply (if visible)
9. Any other relevant metrics

Return the data as a JSON object with these fields:
{
  "product_name": "string or null",
  "floor_price_usd": number or null,
  "active_listings_count": number or null,
  "boxes_sold_today": number or null,
  "daily_volume_usd": number or null,
  "visible_market_cap_usd": number or null,
  "boxes_added_today": number or null,
  "estimated_total_supply": number or null,
  "other_metrics": {}
}

Only include fields that are clearly visible in the image. Use null for missing data.
Be precise with numbers - extract exact values shown.
Return ONLY the JSON object, no other text."""
    
    def _process_with_claude(self, image_bytes: bytes) -> Dict[str, Any]:
        """Process screenshot using Claude (Anthropic) API"""
        import json
        import re
        
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        # Detect image type
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            media_type = "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            media_type = "image/jpeg"
        elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
            media_type = "image/webp"
        else:
            media_type = "image/png"  # Default
        
        response = self.anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": self._get_extraction_prompt()
                        }
                    ],
                }
            ],
        )
        
        content = response.content[0].text
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return json.loads(content)
    
    def _process_with_openai(self, image_bytes: bytes) -> Dict[str, Any]:
        """Process screenshot using OpenAI Vision API"""
        import json
        import re
        
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self._get_extraction_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.1,
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return json.loads(content)
    
    def process_screenshot(self, image_bytes: bytes, use_ai: bool = True) -> Dict[str, Any]:
        """
        Process a screenshot and extract structured data
        
        Args:
            image_bytes: Raw image bytes
            use_ai: If True, use AI Vision API. If False, return empty structure for manual entry.
            
        Returns:
            Dictionary with extracted data and metadata
        """
        # If AI is disabled or not available, return empty structure for manual entry
        if not use_ai or (not self.anthropic_client and not self.openai_client):
            return {
                "success": True,
                "errors": [],
                "extracted_data": {
                    "product_name": None,
                    "floor_price_usd": None,
                    "active_listings_count": None,
                    "boxes_sold_today": None,
                    "daily_volume_usd": None,
                    "visible_market_cap_usd": None,
                    "boxes_added_today": None,
                    "estimated_total_supply": None,
                },
                "confidence_scores": {},
                "raw_text": "AI extraction disabled or not configured. Please enter data manually.",
                "ai_provider": None,
            }
        
        try:
            # Use Claude (preferred) or OpenAI
            if self.anthropic_client:
                extracted_json = self._process_with_claude(image_bytes)
            else:
                extracted_json = self._process_with_openai(image_bytes)
            
            # Calculate confidence scores (simplified - could be enhanced)
            confidence_scores = {}
            for key, value in extracted_json.items():
                if value is not None:
                    # Higher confidence for numeric values (more likely to be accurate)
                    if isinstance(value, (int, float)):
                        confidence_scores[key] = 0.85
                    else:
                        confidence_scores[key] = 0.70
                else:
                    confidence_scores[key] = 0.0
            
            return {
                "success": True,
                "extracted_data": extracted_json,
                "confidence_scores": confidence_scores,
                "detected_box": extracted_json.get("product_name"),
                "ai_provider": self.ai_provider,
                "errors": [],
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Error processing image: {str(e)}"],
                "extracted_data": {},
                "confidence_scores": {},
            }
    
    def validate_image(self, image_bytes: bytes) -> tuple[bool, Optional[str]]:
        """
        Validate that the uploaded file is a valid image
        
        Returns:
            (is_valid, error_message)
        """
        if not PIL_AVAILABLE:
            # Basic validation without PIL
            # Check file size (max 10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                return False, "Image file too large. Maximum size is 10MB."
            # Basic magic number check for common image formats
            if image_bytes[:4] not in [b'\x89PNG', b'\xff\xd8\xff', b'GIF8']:
                return False, "File does not appear to be a valid image (PNG, JPEG, GIF)"
            return True, None
        
        try:
            image = Image.open(BytesIO(image_bytes))
            image.verify()
            
            # Check file size (max 10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                return False, "Image file too large. Maximum size is 10MB."
            
            # Check format
            if image.format not in ['PNG', 'JPEG', 'JPG']:
                return False, f"Unsupported image format: {image.format}. Supported formats: PNG, JPEG, JPG"
            
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"


# Global service instance
image_processing_service = ImageProcessingService()

