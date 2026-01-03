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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js dev server
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
    sort: str = "unified_volume_7d_ema",
    limit: int = 10,
    offset: int = 0,
):
    """
    Temporary mock endpoint for leaderboard
    Returns mock data until real database endpoints are implemented
    """
    import json
    from pathlib import Path
    
    # Load data - try data folder first, then mock_data
    data_file = Path(__file__).parent / "data" / "leaderboard.json"
    mock_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
    
    if data_file.exists():
        with open(data_file, "r") as f:
            mock_data = json.load(f)
    elif mock_file.exists():
        with open(mock_file, "r") as f:
            mock_data = json.load(f)
    else:
        return JSONResponse(
            status_code=503,
            content={"detail": "Data file not found. Please create data/leaderboard.json or mock_data/leaderboard.json"}
        )
    
    # Apply pagination
    boxes = mock_data.get("data", [])
    total = len(boxes)
    paginated_boxes = boxes[offset:offset + limit]
    
    # Transform image URLs from product names and add 30d average sales and month-over-month price change
    from app.services.historical_data import get_box_30d_avg_sales, get_box_month_over_month_price_change
    
    for box in paginated_boxes:
        product_name = box.get("product_name")
        if product_name:
            # Override the placeholder CDN URL with the actual local path
            box["image_url"] = get_box_image_url(product_name)
        
        # Calculate and add 30-day metrics
        box_id = box.get("id")
        if box_id:
            # Add to metrics if metrics dict exists
            if "metrics" not in box:
                box["metrics"] = {}
            
            # 30-day average sales
            avg_30d_sales = get_box_30d_avg_sales(box_id)
            if avg_30d_sales is not None:
                box["metrics"]["boxes_sold_30d_avg"] = avg_30d_sales
            
            # Month-over-month price change percentage (last two monthly entries)
            price_change_mom = get_box_month_over_month_price_change(box_id)
            if price_change_mom is not None:
                box["metrics"]["floor_price_30d_change_pct"] = price_change_mom
    
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
    Temporary mock endpoint for box detail
    Returns mock data until real database endpoint is implemented
    Supports both UUID and numeric rank-based lookups
    """
    import json
    from pathlib import Path
    
    # Try to load specific box detail mock data
    mock_file = Path(__file__).parent / "mock_data" / f"box_detail_{box_id}.json"
    
    if mock_file.exists():
        with open(mock_file, "r") as f:
            box_detail = json.load(f)
            # Transform image URL if product_name exists
            if "data" in box_detail and "product_name" in box_detail["data"]:
                product_name = box_detail["data"]["product_name"]
                box_detail["data"]["image_url"] = get_box_image_url(product_name)
            return box_detail
    
    # Fallback: try to find box in leaderboard data
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
            
            # Try to find by ID first
            box = next((b for b in boxes if b.get("id") == box_id), None)
            
            # If not found and box_id is numeric, try to find by rank
            if not box and box_id.isdigit():
                rank = int(box_id)
                box = next((b for b in boxes if b.get("rank") == rank), None)
            
            if box:
                # Transform leaderboard box to box detail format
                product_name = box.get("product_name")
                return {
                    "data": {
                        "id": box["id"],
                        "product_name": product_name,
                        "set_name": box.get("set_name"),
                        "game_type": box.get("game_type"),
                        "image_url": get_box_image_url(product_name),
                        "release_date": None,
                        "external_product_id": None,
                        "estimated_total_supply": box.get("metrics", {}).get("estimated_total_supply"),
                        "reprint_risk": box.get("reprint_risk", "UNKNOWN"),
                        "current_rank_by_volume": box.get("rank"),
                        "current_rank_by_market_cap": None,
                        "rank_change_direction": box.get("rank_change_direction"),
                        "rank_change_amount": box.get("rank_change_amount"),
                        "is_favorited": False,
                        "metrics": box.get("metrics", {}),
                    }
                }
    
    return JSONResponse(
        status_code=404,
        content={"detail": f"Box with ID {box_id} not found"}
    )


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


# Historical rank history endpoint
@app.get("/booster-boxes/{box_id}/rank-history")
async def get_box_rank_history(
    box_id: str,
    days: int = 30
):
    """
    Get historical rank history for a box based on monthly rankings calculated from historical data
    """
    import json
    from pathlib import Path
    
    try:
        from app.services.historical_data import get_box_rank_history
        
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
        
        # Get historical rank data
        rank_history = get_box_rank_history(box_id, days=days if days > 0 else None)
        
        return {"data": rank_history}
    
    except Exception as e:
        print(f"Error fetching rank history: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to empty data
        return {"data": []}


if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info",
    )

