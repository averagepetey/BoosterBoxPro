"""
Admin Router
Endpoints for admin operations (box registration, manual metrics entry)
"""

from datetime import date
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.config import settings
from app.schemas.booster_box import BoosterBoxCreate, BoosterBoxResponse, BoosterBoxListResponse
from app.schemas.metrics import ManualMetricsInput, BulkManualMetricsInput, MetricsResponse
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.models.unified_box_metrics import UnifiedBoxMetrics

router = APIRouter(prefix="/admin", tags=["admin"])


async def verify_admin_key(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")) -> Optional[str]:
    """
    Simple API key authentication for admin endpoints
    In production, this should be more robust (JWT, OAuth, etc.)
    """
    # If no API key is configured in environment, allow access (development mode)
    # Check explicitly for None or empty string
    if settings.admin_api_key is None or settings.admin_api_key == "":
        # Development mode: allow any key or no key
        return x_api_key
    
    # If API key is configured, validate it
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return x_api_key


@router.post("/boxes", response_model=BoosterBoxResponse, status_code=201)
async def create_box(
    box_data: BoosterBoxCreate,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Create a new booster box
    
    Requires admin API key in header: X-API-Key
    """
    # Convert Pydantic model to dict (excluding None values that shouldn't be set)
    box_dict = box_data.model_dump(exclude_unset=True)
    
    # Create the box
    box = await BoosterBoxRepository.create(db, box_dict)
    
    return BoosterBoxResponse.model_validate(box)


@router.get("/boxes", response_model=BoosterBoxListResponse)
async def list_boxes(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    List all booster boxes
    
    Requires admin API key in header: X-API-Key
    """
    boxes = await BoosterBoxRepository.get_all(db, limit=limit, offset=offset)
    total = await BoosterBoxRepository.count(db)
    
    return BoosterBoxListResponse(
        boxes=[BoosterBoxResponse.model_validate(box) for box in boxes],
        total=total
    )


@router.get("/boxes/{box_id}", response_model=BoosterBoxResponse)
async def get_box(
    box_id: UUID,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Get a specific booster box by ID
    
    Requires admin API key in header: X-API-Key
    """
    box = await BoosterBoxRepository.get_by_id(db, box_id)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    return BoosterBoxResponse.model_validate(box)


@router.post("/manual-metrics", response_model=MetricsResponse, status_code=201)
async def create_manual_metrics(
    metrics_data: ManualMetricsInput,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Create or update manual metrics for a booster box
    
    Requires admin API key in header: X-API-Key
    """
    # Verify box exists
    box = await BoosterBoxRepository.get_by_id(db, metrics_data.booster_box_id)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Convert to unified metrics format
    # In manual mode, we store directly in unified_metrics table
    unified_metrics_data = {
        "booster_box_id": metrics_data.booster_box_id,
        "metric_date": metrics_data.metric_date,
        "floor_price_usd": metrics_data.floor_price_usd,
        "active_listings_count": metrics_data.active_listings_count,
        "unified_volume_usd": metrics_data.daily_volume_usd,  # Use daily volume as unified volume in manual mode
        "visible_market_cap_usd": metrics_data.visible_market_cap_usd,
    }
    
    # Create or update metrics
    metrics = await UnifiedMetricsRepository.create_or_update(db, unified_metrics_data)
    
    return MetricsResponse.model_validate(metrics)


@router.post("/manual-metrics/bulk", status_code=201)
async def create_bulk_manual_metrics(
    bulk_data: BulkManualMetricsInput,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Create or update multiple metrics entries in bulk
    
    Requires admin API key in header: X-API-Key
    """
    created = []
    errors = []
    
    for metrics_data in bulk_data.metrics:
        try:
            # Verify box exists
            box = await BoosterBoxRepository.get_by_id(db, metrics_data.booster_box_id)
            if not box:
                errors.append({
                    "booster_box_id": str(metrics_data.booster_box_id),
                    "metric_date": str(metrics_data.metric_date),
                    "error": "Booster box not found"
                })
                continue
            
            # Convert to unified metrics format
            unified_metrics_data = {
                "booster_box_id": metrics_data.booster_box_id,
                "metric_date": metrics_data.metric_date,
                "floor_price_usd": metrics_data.floor_price_usd,
                "active_listings_count": metrics_data.active_listings_count,
                "unified_volume_usd": metrics_data.daily_volume_usd,
                "visible_market_cap_usd": metrics_data.visible_market_cap_usd,
            }
            
            # Create or update metrics
            metrics = await UnifiedMetricsRepository.create_or_update(db, unified_metrics_data)
            created.append(MetricsResponse.model_validate(metrics))
            
        except Exception as e:
            errors.append({
                "booster_box_id": str(metrics_data.booster_box_id),
                "metric_date": str(metrics_data.metric_date),
                "error": str(e)
            })
    
    return {
        "created": created,
        "errors": errors,
        "total": len(bulk_data.metrics),
        "successful": len(created),
        "failed": len(errors)
    }

