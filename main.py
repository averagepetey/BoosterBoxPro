"""
BoosterBoxPro - FastAPI Application Entry Point
Main entry point for running the API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import init_db


# Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        await init_db()
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is set correctly")
    yield
    # Shutdown (if needed in future)
    pass


# Create FastAPI app
app = FastAPI(
    title="BoosterBoxPro API",
    description="Market intelligence platform for sealed TCG booster boxes",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
# In development, allow all origins for mobile testing
# In production, restrict to specific domains
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
if settings.environment == "development":
    # Allow all origins in development for mobile testing
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicitly allow OPTIONS for preflight
    allow_headers=["*"],
    expose_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"message": "BoosterBoxPro API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import routers (when they're created)
# from app.routers import booster_boxes, auth, users
# app.include_router(booster_boxes.router, prefix="/api/v1/booster-boxes", tags=["booster-boxes"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

# Import admin router for data entry
try:
    from app.routers import admin
    app.include_router(admin.router)
except ImportError:
    pass  # Admin router not available

# Import chat data entry router
try:
    from app.routers import chat_data_entry
    app.include_router(chat_data_entry.router)
except ImportError:
    pass  # Chat data entry router not available


def get_box_image_url(product_name: str | None) -> str | None:
    """
    Generate image URL for a booster box based on its product name.
    Matches the frontend getBoxImageUrl function logic.
    """
    if not product_name:
        return None
    
    import re
    
    # Extract set identifier (e.g., OP-01, OP-02, EB-01, PRB-01)
    set_match = re.search(r'(OP|EB|PRB)-\d+', product_name, re.IGNORECASE)
    if not set_match:
        return None
    
    set_code = set_match.group(0).upper()
    
    # Check if it's a variant (Blue/White)
    variant = ''
    if '(Blue)' in product_name:
        if set_code == 'OP-01':
            # OP-01 Blue uses op-01blue.png
            filename = f"{set_code.lower()}blue.png"
        else:
            variant = '-blue'
            filename = f"{set_code.lower()}{variant}.png"
    elif '(White)' in product_name:
        if set_code == 'OP-01':
            # OP-01 White uses op-01white.png
            filename = f"{set_code.lower()}white.png"
        else:
            variant = '-white'
            filename = f"{set_code.lower()}{variant}.png"
    else:
        # No variant - use base filename
        filename = f"{set_code.lower()}.png"
    
    # Return path - frontend will handle case sensitivity
    # Most files seem to be lowercase, but some are uppercase
    return f"/images/boxes/{filename}"


# Temporary mock endpoint for leaderboard (until real endpoints are built)
@app.get("/booster-boxes")
async def get_booster_boxes(
    sort: str = "unified_volume_usd",
    limit: int = 10,
    offset: int = 0,
):
    """
    Leaderboard endpoint - combines static box info with live database metrics
    """
    import json
    from pathlib import Path
    from datetime import date
    from sqlalchemy import select, desc
    from app.database import AsyncSessionLocal
    from app.models.booster_box import BoosterBox
    from app.models.unified_box_metrics import UnifiedBoxMetrics
    
    # Load base data from JSON for box info
    data_file = Path(__file__).parent / "data" / "leaderboard.json"
    mock_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
    
    if data_file.exists():
        with open(data_file, "r") as f:
            mock_data = json.load(f)
    elif mock_file.exists():
        with open(mock_file, "r") as f:
            mock_data = json.load(f)
    else:
        mock_data = {"data": []}
    
    boxes = mock_data.get("data", [])
    
    # Create a lookup by product_name for the JSON data
    json_boxes_by_name = {box.get("product_name"): box for box in boxes}
    
    # Query database for all boxes and their latest metrics
    async with AsyncSessionLocal() as db:
        # Get all booster boxes from database
        stmt = select(BoosterBox)
        result = await db.execute(stmt)
        db_boxes = result.scalars().all()
        
        # Build result list with live metrics from database
        result_boxes = []
        seen_product_names = set()  # Track seen product names to prevent duplicates
        
        for db_box in db_boxes:
            # Skip test boxes
            if "(Test)" in db_box.product_name or "Test Box" in db_box.product_name:
                continue
            
            # Skip if we've already added this product_name (prevent duplicates)
            if db_box.product_name in seen_product_names:
                continue
            seen_product_names.add(db_box.product_name)
            # Get the latest metrics for this box
            metrics_stmt = select(UnifiedBoxMetrics).where(
                UnifiedBoxMetrics.booster_box_id == db_box.id
            ).order_by(desc(UnifiedBoxMetrics.metric_date)).limit(1)
            
            metrics_result = await db.execute(metrics_stmt)
            latest_metrics = metrics_result.scalar_one_or_none()
            
            # Start with JSON data if available, otherwise build from DB
            json_box = json_boxes_by_name.get(db_box.product_name, {})
            
            box_data = {
                "id": str(db_box.id),
                "product_name": db_box.product_name,
                "set_name": db_box.set_name or json_box.get("set_name"),
                "game_type": db_box.game_type or json_box.get("game_type", "One Piece"),
                "image_url": get_box_image_url(db_box.product_name),
                "reprint_risk": db_box.reprint_risk or json_box.get("reprint_risk", "MEDIUM"),
                "metrics": {}
            }
            
            # Use database metrics if available, otherwise fall back to JSON
            if latest_metrics:
                box_data["metric_date"] = latest_metrics.metric_date.isoformat() if latest_metrics.metric_date else None
                box_data["metrics"] = {
                    "floor_price_usd": float(latest_metrics.floor_price_usd) if latest_metrics.floor_price_usd else json_box.get("metrics", {}).get("floor_price_usd"),
                    "floor_price_1d_change_pct": float(latest_metrics.floor_price_1d_change_pct) if latest_metrics.floor_price_1d_change_pct else 0.0,
                    "unified_volume_usd": float(latest_metrics.unified_volume_usd) if latest_metrics.unified_volume_usd else json_box.get("metrics", {}).get("unified_volume_usd"),
                    "unified_volume_7d_ema": float(latest_metrics.unified_volume_7d_ema) if latest_metrics.unified_volume_7d_ema else json_box.get("metrics", {}).get("unified_volume_7d_ema"),
                    "active_listings_count": latest_metrics.active_listings_count if latest_metrics.active_listings_count else json_box.get("metrics", {}).get("active_listings_count"),
                    "liquidity_score": float(latest_metrics.liquidity_score) if latest_metrics.liquidity_score else json_box.get("metrics", {}).get("liquidity_score"),
                    "days_to_20pct_increase": float(latest_metrics.days_to_20pct_increase) if latest_metrics.days_to_20pct_increase else json_box.get("metrics", {}).get("days_to_20pct_increase"),
                    "boxes_sold_per_day": float(latest_metrics.boxes_sold_per_day) if latest_metrics.boxes_sold_per_day else json_box.get("metrics", {}).get("boxes_sold_per_day"),
                    "boxes_added_today": latest_metrics.boxes_added_today if latest_metrics.boxes_added_today else json_box.get("metrics", {}).get("boxes_added_today"),
                    "boxes_sold_30d_avg": float(latest_metrics.boxes_sold_30d_avg) if latest_metrics.boxes_sold_30d_avg else json_box.get("metrics", {}).get("boxes_sold_30d_avg"),
                }
            elif json_box.get("metrics"):
                box_data["metrics"] = json_box["metrics"]
                box_data["metric_date"] = json_box.get("metric_date")
            else:
                # Skip boxes with no metrics and no JSON data
                continue
            
            # Add 30d change and get accurate metrics from historical data service
            from app.services.historical_data import get_box_month_over_month_price_change, get_box_price_history, get_box_30d_avg_sales
            
            price_change_mom = get_box_month_over_month_price_change(str(db_box.id))
            if price_change_mom is not None:
                box_data["metrics"]["floor_price_30d_change_pct"] = price_change_mom
            
            # Calculate 30d average sales from historical data
            avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
            if avg_sales_30d is not None:
                box_data["metrics"]["boxes_sold_30d_avg"] = avg_sales_30d
            
            # Get the most recent historical entry with calculated metrics
            # This is more accurate than the database value for boxes with sparse data
            historical_data = get_box_price_history(str(db_box.id), days=90)
            if historical_data:
                latest_historical = historical_data[-1]
                
                # Use historical EMA if it's more significant
                hist_ema = latest_historical.get("unified_volume_7d_ema")
                if hist_ema and hist_ema > 0:
                    current_ema = box_data["metrics"].get("unified_volume_7d_ema", 0) or 0
                    if hist_ema > current_ema:
                        box_data["metrics"]["unified_volume_7d_ema"] = hist_ema
                
                # Use historical daily volume if available
                hist_daily_vol = latest_historical.get("daily_volume_usd")
                if hist_daily_vol and hist_daily_vol > 0:
                    box_data["metrics"]["daily_volume_usd"] = hist_daily_vol
                
                # Also update unified_volume_usd (30-day estimate) if available
                # Always use historical data when available for accurate sorting
                hist_vol = latest_historical.get("unified_volume_usd")
                if hist_vol is not None and hist_vol > 0:
                    box_data["metrics"]["unified_volume_usd"] = hist_vol
                elif hist_daily_vol and hist_daily_vol > 0:
                    # Calculate 30-day volume from daily volume if unified_volume_usd not available
                    box_data["metrics"]["unified_volume_usd"] = hist_daily_vol * 30
                
                # Use historical boxes_sold_per_day if available
                hist_sold = latest_historical.get("boxes_sold_per_day")
                if hist_sold and hist_sold > 0:
                    current_sold = box_data["metrics"].get("boxes_sold_per_day", 0) or 0
                    if hist_sold > current_sold:
                        box_data["metrics"]["boxes_sold_per_day"] = hist_sold
                
                # Use historical boxes_sold_30d_avg if available
                hist_30d_avg = latest_historical.get("boxes_sold_30d_avg")
                if hist_30d_avg is not None and hist_30d_avg > 0:
                    box_data["metrics"]["boxes_sold_30d_avg"] = hist_30d_avg
                
                # Use historical boxes_added_today if available
                hist_added = latest_historical.get("boxes_added_today")
                if hist_added and hist_added > 0:
                    current_added = box_data["metrics"].get("boxes_added_today", 0) or 0
                    if hist_added > current_added:
                        box_data["metrics"]["boxes_added_today"] = hist_added
            
            result_boxes.append(box_data)
    
    # Sort by the requested field (default: unified_volume_usd)
    def get_sort_value(box):
        val = box.get("metrics", {}).get(sort)
        if val is None:
            return -1  # Put None values at the end (negative so they sort last)
        try:
            return float(val) if isinstance(val, (int, float, str)) else -1
        except (ValueError, TypeError):
            return -1
    
    result_boxes.sort(key=get_sort_value, reverse=True)
    
    # Add ranks
    for i, box in enumerate(result_boxes):
        box["rank"] = i + 1
        box["rank_change_direction"] = "same"
        box["rank_change_amount"] = 0
    
    total = len(result_boxes)
    paginated_boxes = result_boxes[offset:offset + limit]
    
    return {
        "data": paginated_boxes,
        "meta": {
            "total": total,
            "sort": sort,
            "sort_direction": "desc",
            "limit": limit,
            "offset": offset,
        }
    }


# Temporary mock endpoint for box detail (until real endpoint is built)
@app.get("/booster-boxes/{box_id}")
async def get_box_detail(box_id: str):
    """
    Box detail endpoint - fetches from database with historical data for accurate metrics
    Supports both UUID and numeric rank-based lookups
    """
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.booster_box import BoosterBox
    from app.services.historical_data import get_box_price_history, get_box_month_over_month_price_change
    
    async with AsyncSessionLocal() as db:
        # Try to find box by UUID
        try:
            from uuid import UUID
            box_uuid = UUID(box_id)
            stmt = select(BoosterBox).where(BoosterBox.id == box_uuid)
            result = await db.execute(stmt)
            db_box = result.scalar_one_or_none()
        except (ValueError, TypeError):
            db_box = None
        
        # If not found and box_id is numeric, find by rank from leaderboard
        if not db_box and box_id.isdigit():
            # Get all boxes sorted by volume to find by rank
            all_boxes_stmt = select(BoosterBox)
            all_result = await db.execute(all_boxes_stmt)
            all_boxes = all_result.scalars().all()
            
            # Filter test boxes and sort by historical volume
            valid_boxes = []
            for b in all_boxes:
                if "(Test)" in b.product_name or "Test Box" in b.product_name:
                    continue
                hist = get_box_price_history(str(b.id), days=90)
                vol = hist[-1].get("unified_volume_7d_ema", 0) if hist else 0
                valid_boxes.append((b, vol or 0))
            
            valid_boxes.sort(key=lambda x: x[1], reverse=True)
            rank = int(box_id)
            if 1 <= rank <= len(valid_boxes):
                db_box = valid_boxes[rank - 1][0]
        
        if not db_box:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Box with ID {box_id} not found"}
            )
        
        # Get accurate metrics from historical data service
        historical_data = get_box_price_history(str(db_box.id), days=90)
        
        box_metrics = {}
        if historical_data:
            latest = historical_data[-1]
            box_metrics = {
                "floor_price_usd": latest.get("floor_price_usd"),
                "floor_price_1d_change_pct": latest.get("floor_price_1d_change_pct"),
                "active_listings_count": latest.get("active_listings_count"),
                "daily_volume_usd": latest.get("daily_volume_usd"),
                "unified_volume_usd": latest.get("unified_volume_usd"),
                "unified_volume_7d_ema": latest.get("unified_volume_7d_ema"),
                "boxes_sold_per_day": latest.get("boxes_sold_per_day"),
                "boxes_added_today": latest.get("boxes_added_today"),
                "days_to_20pct_increase": latest.get("days_to_20pct_increase"),
                "liquidity_score": latest.get("liquidity_score"),
            }
        
        # Add 30d price change
        price_change_30d = get_box_month_over_month_price_change(str(db_box.id))
        if price_change_30d is not None:
            box_metrics["floor_price_30d_change_pct"] = price_change_30d
        
        # Add 30d average sales (same logic as leaderboard - use from latest historical entry if available)
        if historical_data and latest.get("boxes_sold_30d_avg") is not None:
            box_metrics["boxes_sold_30d_avg"] = latest.get("boxes_sold_30d_avg")
        else:
            # Fallback to calculated value
            from app.services.historical_data import get_box_30d_avg_sales
            avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
            if avg_sales_30d is not None:
                box_metrics["boxes_sold_30d_avg"] = avg_sales_30d
        
        return {
            "data": {
                "id": str(db_box.id),
                "product_name": db_box.product_name,
                "set_name": db_box.set_name,
                "game_type": db_box.game_type or "One Piece",
                "image_url": get_box_image_url(db_box.product_name),
                "release_date": None,
                "external_product_id": None,
                "estimated_total_supply": box_metrics.get("estimated_total_supply"),
                "reprint_risk": db_box.reprint_risk or "UNKNOWN",
                "current_rank_by_volume": None,
                "current_rank_by_market_cap": None,
                "rank_change_direction": "same",
                "rank_change_amount": 0,
                "is_favorited": False,
                "metrics": box_metrics,
            }
        }


# Historical time-series data endpoint
@app.get("/booster-boxes/{box_id}/time-series")
async def get_box_time_series(
    box_id: str,
    metric: str = "floor_price",
    days: int = 30,
    one_per_month: bool = False
):
    """
    Get historical time-series data for a box from historical_entries.json
    """
    import json
    from pathlib import Path
    
    try:
        from app.services.historical_data import get_box_price_history
        
        # Handle numeric box_id (rank) by finding the actual box ID
        if box_id.isdigit():
            # Load leaderboard to find box by rank
            data_file = Path(__file__).parent / "data" / "leaderboard.json"
            leaderboard_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
            
            leaderboard_data = None
            if data_file.exists():
                with open(data_file, "r") as f:
                    leaderboard_data = json.load(f)
            elif leaderboard_file.exists():
                with open(leaderboard_file, "r") as f:
                    leaderboard_data = json.load(f)
            
            if leaderboard_data:
                boxes = leaderboard_data.get("data", [])
                rank = int(box_id)
                box = next((b for b in boxes if b.get("rank") == rank), None)
                if box:
                    box_id = box.get("id")
        
        # Get historical price data (includes all fields needed for AdvancedMetricsTable)
        price_history = get_box_price_history(box_id, days=days if days > 0 else None, one_per_month=one_per_month)
        
        # Format based on requested metric
        if metric == "floor_price":
            # Return all data for AdvancedMetricsTable (includes floor_price and other fields)
            data_points = price_history
        elif metric == "volume":
            # Return volume-focused data
            data_points = [
                {
                    "date": entry["date"],
                    "unified_volume_usd": entry.get("unified_volume_usd"),
                    "unified_volume_7d_ema": entry.get("unified_volume_7d_ema"),
                }
                for entry in price_history
            ]
        elif metric == "listings":
            data_points = [
                {
                    "date": entry["date"],
                    "active_listings_count": entry.get("active_listings_count"),
                }
                for entry in price_history
            ]
        else:
            # Default: return all available data
            data_points = price_history
        
        return {"data": data_points}
    
    except Exception as e:
        print(f"Error fetching time-series data: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to empty data
        return {"data": []}


# Rank history endpoint - DISABLED for now
# @app.get("/booster-boxes/{box_id}/rank-history")
# async def get_box_rank_history(
#     box_id: str,
#     days: int = None
# ):
#     """Rank history endpoint disabled"""
#     return {"data": []}


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info",
    )

