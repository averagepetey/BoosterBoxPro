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
        variant = '-blue'
    elif '(White)' in product_name:
        variant = '-white'
    
    # Generate filename: op-02.png, op-05.png, etc.
    # Try lowercase first (matches most files), but also check uppercase
    filename_lower = f"{set_code.lower()}{variant}.png"
    filename_upper = f"{set_code}{variant}.png"
    
    # Return path - frontend will handle case sensitivity
    # Most files seem to be lowercase, but some are uppercase
    return f"/images/boxes/{filename_lower}"


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
    
    # Load mock data
    mock_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
    
    if not mock_file.exists():
        return JSONResponse(
            status_code=503,
            content={"detail": "Mock data file not found. Please create mock_data/leaderboard.json"}
        )
    
    with open(mock_file, "r") as f:
        mock_data = json.load(f)
    
    # Apply pagination
    boxes = mock_data.get("data", [])
    total = len(boxes)
    paginated_boxes = boxes[offset:offset + limit]
    
    # Transform image URLs from product names
    for box in paginated_boxes:
        product_name = box.get("product_name")
        if product_name:
            # Override the placeholder CDN URL with the actual local path
            box["image_url"] = get_box_image_url(product_name)
    
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
    
    # Fallback: try to find box in leaderboard mock data
    leaderboard_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
    if leaderboard_file.exists():
        with open(leaderboard_file, "r") as f:
            leaderboard_data = json.load(f)
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


# Temporary mock endpoint for time-series data
@app.get("/booster-boxes/{box_id}/time-series")
async def get_box_time_series(
    box_id: str,
    metric: str = "floor_price",
    days: int = 30
):
    """
    Temporary mock endpoint for time-series data
    Returns mock data until real database endpoint is implemented
    """
    import json
    from pathlib import Path
    
    # Try to load time-series mock data
    # First try with UUID, then try with rank if numeric
    mock_file = None
    if not box_id.isdigit():
        mock_file = Path(__file__).parent / "mock_data" / f"time_series_{box_id}.json"
    
    if not mock_file or not mock_file.exists():
        # If not found or box_id is numeric, try to find box in leaderboard and use first box's data
        leaderboard_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
        if leaderboard_file.exists():
            with open(leaderboard_file, "r") as f:
                leaderboard_data = json.load(f)
                boxes = leaderboard_data.get("data", [])
                
                # Find box by ID or rank
                box = None
                if box_id.isdigit():
                    rank = int(box_id)
                    box = next((b for b in boxes if b.get("rank") == rank), None)
                else:
                    box = next((b for b in boxes if b.get("id") == box_id), None)
                
                if box:
                    # Use first box's time-series data as template
                    first_box_id = boxes[0].get("id") if boxes else None
                    if first_box_id:
                        mock_file = Path(__file__).parent / "mock_data" / f"time_series_{first_box_id}.json"
    
    if mock_file and mock_file.exists():
        with open(mock_file, "r") as f:
            time_series_data = json.load(f)
            # Filter by days if needed
            data_points = time_series_data.get("data", [])
            if days and days < len(data_points):
                data_points = data_points[-days:]
            return {"data": data_points}
    
    # Return empty data if no mock file found
    return {"data": []}


# Temporary mock endpoint for rank history
@app.get("/booster-boxes/{box_id}/rank-history")
async def get_box_rank_history(
    box_id: str,
    days: int = 30
):
    """
    Temporary mock endpoint for rank history
    Returns mock data until real database endpoint is implemented
    """
    import json
    from pathlib import Path
    from datetime import datetime, timedelta
    
    # Try to find box in leaderboard
    leaderboard_file = Path(__file__).parent / "mock_data" / "leaderboard.json"
    if leaderboard_file.exists():
        with open(leaderboard_file, "r") as f:
            leaderboard_data = json.load(f)
            boxes = leaderboard_data.get("data", [])
            
            # Find box by ID or rank
            box = None
            if box_id.isdigit():
                rank = int(box_id)
                box = next((b for b in boxes if b.get("rank") == rank), None)
            else:
                box = next((b for b in boxes if b.get("id") == box_id), None)
            
            if box:
                current_rank = box.get("rank", 1)
                # Generate mock rank history (slight variations around current rank)
                rank_history = []
                base_date = datetime.now() - timedelta(days=days)
                
                for i in range(days):
                    date = base_date + timedelta(days=i)
                    # Simulate rank fluctuations (±2 positions)
                    variation = (i % 7) - 3  # Cycle through -3 to +3
                    rank = max(1, current_rank + variation)
                    rank_history.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "rank": rank
                    })
                
                return {"data": rank_history}
    
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

