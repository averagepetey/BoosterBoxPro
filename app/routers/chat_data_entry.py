"""
Chat Data Entry Router
API endpoint for processing data sent via chat (text or screenshots)
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from scripts.chat_data_entry import process_data_entry

router = APIRouter(prefix="/api/chat-data-entry", tags=["chat-data-entry"])


class ChatDataRequest(BaseModel):
    """Request model for chat data entry (text)"""
    text: str
    description: str = "Data entry text from chat"


@router.post("/process-text")
async def process_chat_data_text(request: ChatDataRequest) -> Dict[str, Any]:
    """
    Process data entry from chat text
    
    This endpoint allows the AI assistant to process text data sent via chat,
    check for duplicates, and update the database/JSON files.
    
    Example request:
    {
        "text": "OP-01: Floor $100, Volume $5000, Sales 10"
    }
    """
    try:
        result = process_data_entry(request.text, is_image=False)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing data: {str(e)}"
        )


@router.post("/process-screenshot")
async def process_chat_data_screenshot(
    file: UploadFile = File(...),
    use_ai: bool = True,
    entry_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process data entry from a screenshot image
    
    This endpoint processes TCGPlayer screenshots, extracts data using AI,
    checks for duplicates, and updates the database/JSON files.
    
    Args:
        file: Image file (PNG, JPEG, JPG)
        use_ai: Whether to use AI extraction (default: True)
    
    Returns:
        Result dict with extraction and update status
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image (PNG, JPEG, JPG)"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        # Process the screenshot
        result = process_data_entry(image_bytes, is_image=True, use_ai=use_ai, entry_date=entry_date)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing screenshot: {str(e)}"
        )

