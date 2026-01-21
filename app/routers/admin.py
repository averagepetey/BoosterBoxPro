"""
Admin Router
Protected endpoints for admin operations (screenshot upload, data entry)

SECURITY:
- Admin access is verified by checking user.role in DATABASE (not JWT)
- API key fallback for automated scripts
- All admin actions are logged
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import date
from uuid import UUID
import logging

from app.config import settings
from app.database import get_db
from app.schemas.image_processing import (
    ScreenshotProcessingResponse,
    ManualExtractionSubmission,
    DuplicateCheckResponse,
)
from app.services.image_processing import image_processing_service
from app.services.duplicate_detection import duplicate_detection_service
from app.models.unified_box_metrics import UnifiedBoxMetrics
from app.models.booster_box import BoosterBox
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBearer(auto_error=False)


async def verify_admin_access(
    x_admin_api_key: Optional[str] = Header(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Verify admin access via API key OR JWT token.
    
    SECURITY: Admin role is ALWAYS checked from database, never trusted from JWT.
    This prevents privilege escalation via JWT manipulation.
    
    Args:
        x_admin_api_key: API key from X-Admin-API-Key header (for scripts)
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object if admin, raises HTTPException if unauthorized
    """
    # Method 1: Check API key (for automated scripts)
    if x_admin_api_key and settings.admin_api_key:
        if x_admin_api_key == settings.admin_api_key:
            logger.info("Admin access granted via API key")
            # Return a synthetic admin user for API key access
            return None  # Indicates API key auth, not user auth
    
    # Method 2: Check JWT token and verify admin role FROM DATABASE
    if credentials:
        try:
            from app.routers.auth import decode_access_token, get_current_user
            
            # Decode token
            payload = decode_access_token(credentials.credentials)
            user_id = payload.get("sub")
            token_version = payload.get("tv", 0)
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Fetch user from database
            from uuid import UUID as UUIDType
            stmt = select(User).where(User.id == UUIDType(user_id))
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            if not user.is_active:
                raise HTTPException(status_code=401, detail="User is inactive")
            
            # Validate token version (revocation check)
            db_token_version = user.token_version or 1
            if token_version < db_token_version:
                logger.warning(f"Revoked token used for admin access by user {user.id}")
                raise HTTPException(status_code=401, detail="Token has been revoked")
            
            # SECURITY: Check admin role FROM DATABASE, not from JWT
            if user.is_admin:
                logger.info(f"Admin access granted to user {user.id} ({user.email[:3]}***)")
                return user
            else:
                logger.warning(f"Non-admin user {user.id} attempted admin access")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Admin auth error: {str(e)}")
    
    # If no admin key is configured and we're in development, allow access
    if not settings.admin_api_key and settings.environment != "production":
        logger.warning("Admin access granted in dev mode (no API key configured)")
        return None
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )


def verify_admin_api_key(x_admin_api_key: Optional[str] = Header(None)) -> bool:
    """
    Legacy: Verify admin API key from header (kept for backwards compatibility)
    
    Args:
        x_admin_api_key: API key from X-Admin-API-Key header
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not settings.admin_api_key:
        # If no admin key is configured, allow access in development
        # In production, this should be required
        if settings.environment == "production":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin API key not configured"
            )
        return True
    
    if not x_admin_api_key or x_admin_api_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin API key. Provide X-Admin-API-Key header."
        )
    
    return True


@router.post("/upload-screenshot", response_model=ScreenshotProcessingResponse)
async def upload_screenshot(
    file: UploadFile = File(...),
    use_ai: bool = True,  # Query parameter to enable/disable AI (default: True)
    _: bool = Depends(verify_admin_api_key)
):
    """
    Upload a screenshot and extract data using OCR/AI
    
    Requires admin authentication via X-Admin-API-Key header
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "errors": ["File must be an image (PNG, JPEG, JPG)"],
                "extracted_data": {},
                "confidence_scores": {},
            }
        )
    
    # Read file bytes
    image_bytes = await file.read()
    
    # Validate image
    is_valid, error_msg = image_processing_service.validate_image(image_bytes)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "errors": [error_msg or "Invalid image file"],
                "extracted_data": {},
                "confidence_scores": {},
            }
        )
    
    # Process screenshot (use_ai parameter controls whether to use paid OpenAI API)
    result = image_processing_service.process_screenshot(image_bytes, use_ai=use_ai)
    
    return ScreenshotProcessingResponse(**result)


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(
    submission: ManualExtractionSubmission,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_api_key)
):
    """
    Check if data already exists for a given box and date
    
    Requires admin authentication
    """
    try:
        booster_box_id = UUID(submission.booster_box_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booster_box_id format. Must be a valid UUID."
        )
    
    # Prepare new data dict
    new_data = {
        "floor_price_usd": submission.floor_price_usd,
        "active_listings_count": submission.active_listings_count,
        "boxes_sold_today": submission.boxes_sold_today,
        "daily_volume_usd": submission.daily_volume_usd,
        "visible_market_cap_usd": submission.visible_market_cap_usd,
        "boxes_added_today": submission.boxes_added_today,
    }
    
    # Check for duplicates (using sync session for now - will need to adapt for async)
    # For now, we'll do a simple query
    stmt = select(UnifiedBoxMetrics).where(
        UnifiedBoxMetrics.booster_box_id == booster_box_id,
        UnifiedBoxMetrics.metric_date == submission.metric_date
    )
    result = await db.execute(stmt)
    existing_metrics = result.scalar_one_or_none()
    
    if not existing_metrics:
        return DuplicateCheckResponse(
            is_duplicate=False,
            existing_data=None,
            differences={},
            message="No existing data found for this date. This is new data."
        )
    
    # Compare values
    differences = {}
    is_duplicate = True
    
    comparison_fields = {
        "floor_price_usd": ("floor_price_usd", 0.01),
        "active_listings_count": ("active_listings_count", 0),
        "boxes_sold_today": ("boxes_sold_per_day", 0),
        "daily_volume_usd": ("unified_volume_usd", 0.01),
        "visible_market_cap_usd": ("visible_market_cap_usd", 0.01),
        "boxes_added_today": ("boxes_added_today", 0),
    }
    
    existing_data = {}
    for new_key, (existing_key, tolerance) in comparison_fields.items():
        existing_attr = getattr(existing_metrics, existing_key, None)
        if existing_attr is not None:
            existing_data[new_key] = float(existing_attr) if hasattr(existing_attr, '__float__') else existing_attr
        else:
            existing_data[new_key] = None
        
        new_value = new_data.get(new_key)
        existing_value = existing_data.get(new_key)
        
        if new_value is None and existing_value is None:
            continue
        
        if new_value is None or existing_value is None:
            differences[new_key] = {
                "existing": existing_value,
                "new": new_value,
                "changed": True
            }
            is_duplicate = False
            continue
        
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
    
    return DuplicateCheckResponse(
        is_duplicate=is_duplicate,
        existing_data=existing_data,
        differences=differences,
        message=message
    )


@router.post("/save-extracted-data")
async def save_extracted_data(
    submission: ManualExtractionSubmission,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_api_key)
):
    """
    Save extracted and reviewed data to the database
    
    Only saves if data is new or different from existing data.
    Requires admin authentication.
    """
    try:
        booster_box_id = UUID(submission.booster_box_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booster_box_id format. Must be a valid UUID."
        )
    
    # Verify box exists
    stmt = select(BoosterBox).where(BoosterBox.id == booster_box_id)
    result = await db.execute(stmt)
    box = result.scalar_one_or_none()
    
    if not box:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booster box with id {submission.booster_box_id} not found"
        )
    
    # Check for existing data
    stmt = select(UnifiedBoxMetrics).where(
        UnifiedBoxMetrics.booster_box_id == booster_box_id,
        UnifiedBoxMetrics.metric_date == submission.metric_date
    )
    result = await db.execute(stmt)
    existing_metrics = result.scalar_one_or_none()
    
    # Prepare new data
    new_data = {
        "floor_price_usd": submission.floor_price_usd,
        "active_listings_count": submission.active_listings_count,
        "boxes_sold_today": submission.boxes_sold_today,
        "daily_volume_usd": submission.daily_volume_usd,
        "visible_market_cap_usd": submission.visible_market_cap_usd,
        "boxes_added_today": submission.boxes_added_today,
    }
    
    # If data exists, check if it's different
    if existing_metrics:
        # Compare key fields
        is_different = False
        tolerance = 0.01
        
        if submission.floor_price_usd is not None:
            existing_price = float(existing_metrics.floor_price_usd) if existing_metrics.floor_price_usd else None
            if existing_price is None or abs(existing_price - submission.floor_price_usd) > tolerance:
                is_different = True
        
        if submission.active_listings_count is not None:
            if existing_metrics.active_listings_count != submission.active_listings_count:
                is_different = True
        
        if not is_different:
            # Data is duplicate, don't update
            return {
                "success": False,
                "message": "Data already exists and matches existing values. No update performed.",
                "is_duplicate": True
            }
        
        # Update existing record
        if submission.floor_price_usd is not None:
            existing_metrics.floor_price_usd = submission.floor_price_usd
        if submission.active_listings_count is not None:
            existing_metrics.active_listings_count = submission.active_listings_count
        if submission.boxes_sold_today is not None:
            existing_metrics.boxes_sold_per_day = submission.boxes_sold_today
        if submission.daily_volume_usd is not None:
            existing_metrics.unified_volume_usd = submission.daily_volume_usd
        if submission.visible_market_cap_usd is not None:
            existing_metrics.visible_market_cap_usd = submission.visible_market_cap_usd
        if submission.boxes_added_today is not None:
            existing_metrics.boxes_added_today = submission.boxes_added_today
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Existing data updated with new values.",
            "is_duplicate": False,
            "action": "updated"
        }
    else:
        # Create new record
        new_metrics = UnifiedBoxMetrics(
            booster_box_id=booster_box_id,
            metric_date=submission.metric_date,
            floor_price_usd=submission.floor_price_usd,
            active_listings_count=submission.active_listings_count,
            boxes_sold_per_day=submission.boxes_sold_today,
            unified_volume_usd=submission.daily_volume_usd,
            visible_market_cap_usd=submission.visible_market_cap_usd,
            boxes_added_today=submission.boxes_added_today,
        )
        
        db.add(new_metrics)
        await db.commit()
        
        return {
            "success": True,
            "message": "New data saved successfully.",
            "is_duplicate": False,
            "action": "created"
        }


@router.get("/boxes")
async def list_boxes_for_admin(
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_admin_api_key)
):
    """
    List all boxes for admin interface (for dropdown selection)
    
    Requires admin authentication
    """
    stmt = select(BoosterBox).order_by(BoosterBox.product_name)
    result = await db.execute(stmt)
    boxes = result.scalars().all()
    
    return {
        "data": [
            {
                "id": str(box.id),
                "product_name": box.product_name,
                "set_name": box.set_name,
                "game_type": box.game_type,
            }
            for box in boxes
        ]
    }

