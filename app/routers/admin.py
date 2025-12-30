"""
Admin Router
Endpoints for admin operations (box registration, manual metrics entry)
"""

from datetime import date
from uuid import UUID
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import uuid
import base64

from app.database import get_db
from app.config import settings
from app.schemas.booster_box import BoosterBoxCreate, BoosterBoxResponse, BoosterBoxListResponse
from app.schemas.metrics import ManualMetricsInput, BulkManualMetricsInput, MetricsResponse
from app.schemas.image_processing import ScreenshotProcessingResponse, ManualExtractionSubmission
from app.schemas.sales_extraction import (
    IndividualSaleExtraction,
    ListingDataExtraction,
    BulkSalesExtraction,
    ListingItem,
)
from app.repositories.booster_box_repository import BoosterBoxRepository
from app.repositories.unified_metrics_repository import UnifiedMetricsRepository
from app.services.metrics_calculator import MetricsCalculator
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
        "boxes_sold_per_day": metrics_data.units_sold_count,  # Map units_sold_count to boxes_sold_per_day
        "boxes_sold_30d_avg": metrics_data.units_sold_count,  # For single-day entry, use same for 30d avg initially
    }
    
    # Auto-calculate market cap if not provided
    if not unified_metrics_data.get("visible_market_cap_usd") and metrics_data.floor_price_usd and metrics_data.active_listings_count:
        from decimal import Decimal
        unified_metrics_data["visible_market_cap_usd"] = metrics_data.floor_price_usd * Decimal(str(metrics_data.active_listings_count))
    
    # Auto-calculate volume if not provided but we have units sold
    if not unified_metrics_data.get("unified_volume_usd") and metrics_data.units_sold_count and metrics_data.floor_price_usd:
        from decimal import Decimal
        unified_metrics_data["unified_volume_usd"] = metrics_data.floor_price_usd * Decimal(str(metrics_data.units_sold_count))
    
    # Create or update metrics
    metrics = await UnifiedMetricsRepository.create_or_update(db, unified_metrics_data)
    
    # Trigger metrics calculations (EMA, liquidity score, etc.)
    calculator = MetricsCalculator(db)
    updated_metrics = await calculator.update_metrics_with_calculations(
        metrics_data.booster_box_id,
        metrics_data.metric_date
    )
    
    # Return the updated metrics with all calculated fields
    if updated_metrics:
        return MetricsResponse.model_validate(updated_metrics)
    else:
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
                "boxes_sold_per_day": metrics_data.units_sold_count,
                "boxes_sold_30d_avg": metrics_data.units_sold_count,
            }
            
            # Auto-calculate market cap if not provided
            if not unified_metrics_data.get("visible_market_cap_usd") and metrics_data.floor_price_usd and metrics_data.active_listings_count:
                from decimal import Decimal
                unified_metrics_data["visible_market_cap_usd"] = metrics_data.floor_price_usd * Decimal(str(metrics_data.active_listings_count))
            
            # Auto-calculate volume if not provided
            if not unified_metrics_data.get("unified_volume_usd") and metrics_data.units_sold_count and metrics_data.floor_price_usd:
                from decimal import Decimal
                unified_metrics_data["unified_volume_usd"] = metrics_data.floor_price_usd * Decimal(str(metrics_data.units_sold_count))
            
            # Create or update metrics
            metrics = await UnifiedMetricsRepository.create_or_update(db, unified_metrics_data)
            
            # Trigger metrics calculations
            calculator = MetricsCalculator(db)
            updated_metrics = await calculator.update_metrics_with_calculations(
                metrics_data.booster_box_id,
                metrics_data.metric_date
            )
            
            if updated_metrics:
                created.append(MetricsResponse.model_validate(updated_metrics))
            else:
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


@router.get("/recent-metrics")
async def get_recent_metrics(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Get recent metrics entries
    
    Requires admin API key in header: X-API-Key
    """
    # Get recent metrics ordered by created_at
    result = await db.execute(
        select(UnifiedBoxMetrics)
        .order_by(desc(UnifiedBoxMetrics.created_at))
        .limit(limit)
    )
    recent_metrics = list(result.scalars().all())
    
    # Get box info for each metric
    entries = []
    for metric in recent_metrics:
        box = await BoosterBoxRepository.get_by_id(db, metric.booster_box_id)
        if box:
            entries.append({
                "id": str(metric.id),
                "box_name": box.product_name,
                "set_name": box.set_name,
                "metric_date": str(metric.metric_date),
                "floor_price_usd": float(metric.floor_price_usd) if metric.floor_price_usd else None,
                "active_listings_count": metric.active_listings_count,
                "created_at": metric.created_at.isoformat(),
            })
    
    return {
        "entries": entries,
        "total": len(entries)
    }


# In-memory storage for screenshot processing sessions (in production, use Redis or database)
_screenshot_sessions: Dict[str, dict] = {}


@router.post("/screenshot/upload", response_model=ScreenshotProcessingResponse)
async def upload_screenshot(
    file: UploadFile = File(..., description="Screenshot image file"),
    box_id: Optional[str] = Form(None, description="Optional box UUID"),
    box_name: Optional[str] = Form(None, description="Optional box name"),
    metric_date: Optional[str] = Form(None, description="Optional date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Upload a screenshot for manual data extraction
    
    This endpoint accepts an image file (screenshot) and creates a processing session.
    After viewing the screenshot, you can submit the extracted values via the confirmation endpoint.
    
    Requires admin API key in header: X-API-Key
    """
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create processing session
        processing_id = str(uuid.uuid4())
        
        # Store session (in production, use Redis or database)
        session_data = {
            "processing_id": processing_id,
            "image_bytes": image_bytes,
            "image_type": file.content_type,
            "filename": file.filename,
            "box_id": box_id,
            "box_name": box_name,
            "metric_date": metric_date,
            "timestamp": date.today().isoformat(),
        }
        _screenshot_sessions[processing_id] = session_data
        
        # For now, return session ID for manual extraction
        # In the future, this could use OCR to auto-extract
        return ScreenshotProcessingResponse(
            processing_id=processing_id,
            extracted_data=None,
            confidence=0.0,
            needs_review=True,
            suggested_values=None,
            message=f"Screenshot received. Image size: {len(image_bytes)} bytes. Please view the image and submit extracted values using the processing_id."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing screenshot: {str(e)}")


@router.get("/screenshot/{processing_id}")
async def get_screenshot(
    processing_id: str,
    api_key: str = Depends(verify_admin_key),
):
    """
    Get the screenshot image for a processing session
    
    Returns the image as base64-encoded data URL for display in the admin panel.
    
    Requires admin API key in header: X-API-Key
    """
    if processing_id not in _screenshot_sessions:
        raise HTTPException(status_code=404, detail="Processing session not found")
    
    session = _screenshot_sessions[processing_id]
    image_bytes = session["image_bytes"]
    image_type = session.get("image_type", "image/png")
    
    # Convert to base64 data URL
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    data_url = f"data:{image_type};base64,{base64_image}"
    
    return {
        "processing_id": processing_id,
        "image_data_url": data_url,
        "box_name": session.get("box_name"),
        "metric_date": session.get("metric_date"),
    }


@router.post("/screenshot/confirm", response_model=MetricsResponse, status_code=201)
async def confirm_screenshot_extraction(
    extraction: ManualExtractionSubmission,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Submit manually extracted values from a screenshot
    
    After viewing a screenshot, submit the extracted metrics data.
    The system will calculate derived metrics and save to the database.
    
    Requires admin API key in header: X-API-Key
    """
    # Verify processing session exists
    if extraction.processing_id not in _screenshot_sessions:
        raise HTTPException(status_code=404, detail="Processing session not found")
    
    # Verify box exists
    try:
        box_uuid = UUID(extraction.booster_box_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid box UUID format")
    
    box = await BoosterBoxRepository.get_by_id(db, box_uuid)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Parse date
    try:
        metric_date_obj = date.fromisoformat(extraction.metric_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Create metrics input
    from decimal import Decimal
    metrics_input = ManualMetricsInput(
        booster_box_id=box_uuid,
        metric_date=metric_date_obj,
        floor_price_usd=Decimal(str(extraction.floor_price_usd)),
        active_listings_count=extraction.active_listings_count,
        daily_volume_usd=Decimal(str(extraction.daily_volume_usd)) if extraction.daily_volume_usd else None,
        units_sold_count=extraction.units_sold_count,
        visible_market_cap_usd=Decimal(str(extraction.visible_market_cap_usd)) if extraction.visible_market_cap_usd else None,
    )
    
    # Use existing manual metrics endpoint logic
    from decimal import Decimal
    
    unified_metrics_data = {
        "booster_box_id": metrics_input.booster_box_id,
        "metric_date": metrics_input.metric_date,
        "floor_price_usd": metrics_input.floor_price_usd,
        "active_listings_count": metrics_input.active_listings_count,
        "unified_volume_usd": metrics_input.daily_volume_usd,
        "visible_market_cap_usd": metrics_input.visible_market_cap_usd,
        "boxes_sold_per_day": Decimal(str(metrics_input.units_sold_count)) if metrics_input.units_sold_count else None,
        "boxes_sold_30d_avg": Decimal(str(metrics_input.units_sold_count)) if metrics_input.units_sold_count else None,
    }
    
    # Auto-calculate market cap if not provided
    if not unified_metrics_data.get("visible_market_cap_usd") and metrics_input.floor_price_usd and metrics_input.active_listings_count:
        unified_metrics_data["visible_market_cap_usd"] = metrics_input.floor_price_usd * Decimal(str(metrics_input.active_listings_count))
    
    # Auto-calculate volume if not provided
    if not unified_metrics_data.get("unified_volume_usd") and metrics_input.units_sold_count and metrics_input.floor_price_usd:
        unified_metrics_data["unified_volume_usd"] = metrics_input.floor_price_usd * Decimal(str(metrics_input.units_sold_count))
    
    # Create or update metrics
    metrics = await UnifiedMetricsRepository.create_or_update(db, unified_metrics_data)
    
    # Trigger metrics calculations
    calculator = MetricsCalculator(db)
    updated_metrics = await calculator.update_metrics_with_calculations(
        metrics_input.booster_box_id,
        metrics_input.metric_date
    )
    
    # Clean up session (optional - can keep for audit trail)
    # del _screenshot_sessions[extraction.processing_id]
    
    # Return the updated metrics
    if updated_metrics:
        return MetricsResponse.model_validate(updated_metrics)
    else:
        return MetricsResponse.model_validate(metrics)


@router.post("/screenshot/listings/extract", status_code=201)
async def extract_listing_data(
    extraction: ListingDataExtraction,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Extract and save listing data from screenshot
    
    For screenshots showing active listings on TCGplayer.
    Saves multiple listings to tcg_listings_raw table.
    
    Requires admin API key in header: X-API-Key
    """
    # Verify processing session exists (optional - allow test processing_ids)
    if extraction.processing_id not in _screenshot_sessions:
        # Allow test processing_ids that start with "test_"
        if not extraction.processing_id.startswith("test_"):
            raise HTTPException(status_code=404, detail="Processing session not found")
    
    # Verify box exists
    try:
        box_uuid = UUID(extraction.booster_box_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid box UUID format")
    
    box = await BoosterBoxRepository.get_by_id(db, box_uuid)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Parse date
    try:
        snapshot_date_obj = date.fromisoformat(extraction.snapshot_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Save listings to database
    from datetime import datetime
    from sqlalchemy import text
    
    saved_listings = []
    errors = []
    
    for listing in extraction.listings:
        try:
            from decimal import Decimal
            
            listing_id = listing.get("listing_id") or f"manual_{extraction.processing_id}_{len(saved_listings)}"
            listed_price = Decimal(str(listing.get("listed_price_usd", 0)))
            quantity = listing.get("quantity", 1)
            seller_id = listing.get("seller_id")
            
            insert_query = text("""
                INSERT INTO tcg_listings_raw (
                    booster_box_id,
                    snapshot_date,
                    listing_id,
                    seller_id,
                    listed_price_usd,
                    quantity,
                    snapshot_timestamp,
                    is_active,
                    created_at
                ) VALUES (
                    :booster_box_id,
                    :snapshot_date,
                    :listing_id,
                    :seller_id,
                    :listed_price_usd,
                    :quantity,
                    :snapshot_timestamp,
                    true,
                    NOW()
                )
                ON CONFLICT (booster_box_id, listing_id, snapshot_date) DO UPDATE
                SET listed_price_usd = EXCLUDED.listed_price_usd,
                    quantity = EXCLUDED.quantity,
                    snapshot_timestamp = EXCLUDED.snapshot_timestamp
                RETURNING id
            """)
            
            result = await db.execute(
                insert_query,
                {
                    "booster_box_id": str(box_uuid),
                    "snapshot_date": snapshot_date_obj,
                    "listing_id": listing_id,
                    "seller_id": seller_id,
                    "listed_price_usd": listed_price,
                    "quantity": quantity,
                    "snapshot_timestamp": datetime.combine(snapshot_date_obj, datetime.now().time()),
                }
            )
            
            listing_db_id = result.scalar()
            saved_listings.append({
                "id": str(listing_db_id) if listing_db_id else None,
                "listing_id": listing_id,
                "price": float(listed_price),
                "quantity": quantity,
            })
            
        except Exception as e:
            errors.append({
                "listing": listing,
                "error": str(e)
            })
    
    await db.commit()
    
    return {
        "message": f"Saved {len(saved_listings)} listings, {len(errors)} errors",
        "saved": saved_listings,
        "errors": errors,
        "total_processed": len(extraction.listings),
        "booster_box_id": str(box_uuid),
        "snapshot_date": str(snapshot_date_obj),
    }


@router.post("/screenshot/sales/bulk-extract", status_code=201)
async def extract_bulk_sales(
    extraction: BulkSalesExtraction,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_admin_key),
):
    """
    Extract and save multiple sales from a single screenshot
    
    For screenshots showing multiple completed sales (e.g., sales history page).
    
    Requires admin API key in header: X-API-Key
    """
    # Verify processing session exists (optional - allow test processing_ids)
    if extraction.processing_id not in _screenshot_sessions:
        # Allow test processing_ids that start with "test_"
        if not extraction.processing_id.startswith("test_"):
            raise HTTPException(status_code=404, detail="Processing session not found")
    
    # Verify box exists
    try:
        box_uuid = UUID(extraction.booster_box_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid box UUID format")
    
    box = await BoosterBoxRepository.get_by_id(db, box_uuid)
    if not box:
        raise HTTPException(status_code=404, detail="Booster box not found")
    
    # Save all sales
    from datetime import datetime
    from sqlalchemy import text
    
    saved_sales = []
    errors = []
    
    for sale in extraction.sales:
        try:
            sale_date_obj = date.fromisoformat(sale.get("sale_date"))
            from decimal import Decimal
            
            insert_query = text("""
                INSERT INTO ebay_sales_raw (
                    booster_box_id,
                    sale_date,
                    sale_timestamp,
                    ebay_item_id,
                    sold_price_usd,
                    quantity,
                    seller_id,
                    listing_type,
                    created_at
                ) VALUES (
                    :booster_box_id,
                    :sale_date,
                    :sale_timestamp,
                    :ebay_item_id,
                    :sold_price_usd,
                    :quantity,
                    :seller_id,
                    :listing_type,
                    NOW()
                )
                ON CONFLICT (booster_box_id, ebay_item_id) DO NOTHING
                RETURNING id
            """)
            
            # Generate unique item ID for each sale
            item_id = f"manual_tcg_bulk_{extraction.processing_id}_{len(saved_sales)}_{int(datetime.now().timestamp())}"
            
            result = await db.execute(
                insert_query,
                {
                    "booster_box_id": str(box_uuid),
                    "sale_date": sale_date_obj,
                    "sale_timestamp": datetime.combine(sale_date_obj, datetime.min.time()),
                    "ebay_item_id": item_id,
                    "sold_price_usd": Decimal(str(sale.get("sold_price_usd", 0))),
                    "quantity": sale.get("quantity", 1),
                    "seller_id": sale.get("seller_id"),
                    "listing_type": sale.get("listing_type") or "TCGplayer",
                }
            )
            
            sale_id = result.scalar()
            if sale_id:
                saved_sales.append({
                    "id": str(sale_id),
                    "sale_date": str(sale_date_obj),
                    "sold_price_usd": float(sale.get("sold_price_usd", 0)),
                    "quantity": sale.get("quantity", 1),
                })
            
        except Exception as e:
            errors.append({
                "sale": sale,
                "error": str(e)
            })
    
    await db.commit()
    
    return {
        "message": f"Saved {len(saved_sales)} sales, {len(errors)} errors",
        "saved": saved_sales,
        "errors": errors,
        "total_processed": len(extraction.sales),
        "booster_box_id": str(box_uuid),
    }

