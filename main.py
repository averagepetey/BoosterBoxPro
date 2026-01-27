"""
BoosterBoxPro - FastAPI Application Entry Point
Main entry point for running the API server

Security Features:
- Security headers (HSTS, X-Frame-Options, CSP, etc.)
- CORS lockdown in production
- Rate limiting on all endpoints
- Request logging with correlation IDs
- Docs disabled in production
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import uvicorn
import traceback
import logging

from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    logger.info(f"🚀 Starting BoosterBoxPro API in {settings.environment} mode")
    try:
        await init_db()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"⚠️  Database connection failed: {e}")
        logger.error("   Make sure PostgreSQL is running and DATABASE_URL is set correctly")
    yield
    # Shutdown
    logger.info("👋 Shutting down BoosterBoxPro API")


# Determine if docs should be enabled
# In production, disable Swagger/OpenAPI to reduce attack surface
docs_url = "/docs" if settings.environment != "production" else None
redoc_url = "/redoc" if settings.environment != "production" else None
openapi_url = "/openapi.json" if settings.environment != "production" else None

if settings.environment == "production":
    logger.info("🔒 API documentation disabled in production mode")

# Create FastAPI app
app = FastAPI(
    title="BoosterBoxPro API",
    description="Market intelligence platform for sealed TCG booster boxes",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

# ============================================================================
# SECURITY MIDDLEWARE (Order matters - applied in reverse order)
# ============================================================================

# 1. Security Headers Middleware
try:
    from app.middleware.security import SecurityHeadersMiddleware, RequestLoggingMiddleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("✅ Security headers middleware loaded")
except ImportError as e:
    logger.warning(f"⚠️  Security middleware not available: {e}")

# 2. Rate Limiting
try:
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
    
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
        logger.info("✅ Rate limiting enabled")
    else:
        logger.warning("⚠️  Rate limiting disabled")
except ImportError as e:
    logger.warning(f"⚠️  Rate limiting not available (install slowapi): {e}")

# 3. Admin IP Allowlist (restricts /admin/* to specific IPs)
try:
    from app.middleware.admin_ip_allowlist import AdminIPAllowlistMiddleware
    app.add_middleware(AdminIPAllowlistMiddleware)
    logger.info("✅ Admin IP allowlist middleware loaded")
except ImportError as e:
    logger.warning(f"⚠️  Admin IP allowlist not available: {e}")

# 4. CORS Configuration
# In development, allow all origins (for ease of development)
# In production, restrict to specific domains only
if settings.environment == "development":
    # Development: allow all origins but disable credentials to work with wildcard
    cors_origins = ["*"]
    cors_credentials = False
    logger.info("🔓 CORS: Development mode - allowing all origins")
else:
    # Production: specific origins from config
    cors_origins = settings.cors_origins_list
    cors_credentials = True
    logger.info(f"🔒 CORS: Production mode - allowed origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Admin-API-Key"],
    expose_headers=["X-Request-ID", "X-RateLimit-Limit", "Retry-After"],
)


# Health check endpoints (GET and HEAD so UptimeRobot / monitors work)
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    """Root endpoint - health check"""
    return {"message": "BoosterBoxPro API", "status": "running"}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Global exception handler to ensure CORS headers are included in error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that:
    1. Logs the full error internally
    2. Returns sanitized error to client (no internal details in production)
    3. Ensures CORS headers are included
    """
    import traceback
    error_detail = str(exc)
    error_traceback = traceback.format_exc()
    
    # Get request context for logging
    request_id = getattr(request.state, 'request_id', 'unknown')
    client_ip = getattr(request.state, 'client_ip', 'unknown')
    
    # Log the full error internally (always)
    logger.error(
        f"[{request_id}] Unhandled exception from {client_ip}: "
        f"{request.method} {request.url.path}"
    )
    logger.error(f"[{request_id}] Error: {error_detail}")
    logger.error(f"[{request_id}] Traceback:\n{error_traceback}")
    
    # Build response - sanitize in production
    if settings.environment == "production":
        # Production: Never expose internal error details
        response_content = {
            "detail": "An internal error occurred. Please try again later.",
            "request_id": request_id,  # Include for support reference
        }
    else:
        # Development: Include error details for debugging
        response_content = {
            "detail": "Internal server error",
            "error": error_detail,
            "request_id": request_id,
        }
    
    response = JSONResponse(
        status_code=500,
        content=response_content
    )
    
    # Add CORS headers manually if needed (CORS middleware should handle this, but ensure it)
    origin = request.headers.get("origin")
    if origin or settings.environment == "development":
        response.headers["Access-Control-Allow-Origin"] = "*" if settings.environment == "development" else origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    
    # Add request ID header
    response.headers["X-Request-ID"] = request_id
    
    return response


# Import auth router and dependencies
get_current_user = None
require_active_subscription = None
try:
    from app.routers import auth
    from app.routers.auth import get_current_user
    from app.dependencies.paywall import require_active_subscription
    app.include_router(auth.router, prefix="/api/v1")
    print("✅ Auth router loaded successfully")
except ImportError as e:
    print(f"⚠️  Auth router not available: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"⚠️  Error loading auth router: {e}")
    import traceback
    traceback.print_exc()

# Optional user dependency - returns None if auth is not available
# These endpoints work without authentication, but can use user info if available
async def get_optional_user():
    """Optional user dependency - returns None (endpoints work without auth)"""
    return None

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

# Import payment router
try:
    from app.routers import payment
    app.include_router(payment.router, prefix="/api/v1")
except ImportError:
    pass  # Payment router not available

# Import user router (subscription management)
try:
    from app.routers import user
    app.include_router(user.router, prefix="/api/v1")
    print("✅ User router loaded successfully")
except ImportError as e:
    print(f"⚠️  User router not available: {e}")

# Import extension router (for Chrome extension)
try:
    from app.routers import extension
    app.include_router(extension.router)
    print("✅ Extension router loaded successfully")
except ImportError as e:
    print(f"⚠️  Extension router not available: {e}")


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


# Leaderboard endpoint - requires authentication and active subscription
@app.get("/booster-boxes")
async def get_booster_boxes(
    sort: str = "unified_volume_7d_ema",  # Primary ranking metric: 7-day EMA volume
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(require_active_subscription) if require_active_subscription is not None else Depends(get_optional_user),
):
    """
    Get leaderboard of booster boxes.
    Requires authentication and active subscription (trial or paid).
    Default sort: unified_volume_7d_ema (7-day EMA volume - most accurate ranking metric)
    """
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
                
                # Calculate daily_volume_usd - prefer from historical data, or estimate from 30d volume
                # NOTE: Do NOT use unified_volume_7d_ema to calculate daily volume - EMA is not a sum!
                daily_vol = None
                # First try to get from historical data (most accurate)
                # If not available, estimate from unified_volume_usd (which is typically daily * 30)
                if latest_metrics.unified_volume_usd:
                    # unified_volume_usd is typically calculated as daily_volume_usd * 30
                    daily_vol = float(latest_metrics.unified_volume_usd) / 30
                
                box_data["metrics"] = {
                    "floor_price_usd": float(latest_metrics.floor_price_usd) if latest_metrics.floor_price_usd else json_box.get("metrics", {}).get("floor_price_usd"),
                    "floor_price_1d_change_pct": float(latest_metrics.floor_price_1d_change_pct) if latest_metrics.floor_price_1d_change_pct else 0.0,
                    "daily_volume_usd": daily_vol if daily_vol else json_box.get("metrics", {}).get("daily_volume_usd"),
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
                
                # Ensure daily_volume_usd exists - calculate from available metrics
                # NOTE: Do NOT use unified_volume_7d_ema - it's an EMA, not a sum
                if not box_data["metrics"].get("daily_volume_usd"):
                    if box_data["metrics"].get("unified_volume_usd"):
                        # unified_volume_usd is typically daily_volume_usd * 30
                        box_data["metrics"]["daily_volume_usd"] = float(box_data["metrics"]["unified_volume_usd"]) / 30
                
                # Ensure unified_volume_usd exists - calculate from available metrics
                if not box_data["metrics"].get("unified_volume_usd"):
                    if box_data["metrics"].get("daily_volume_usd"):
                        box_data["metrics"]["unified_volume_usd"] = float(box_data["metrics"]["daily_volume_usd"]) * 30
            else:
                # Skip boxes with no metrics and no JSON data
                continue
            
            # Add 30d change and get accurate metrics from historical data service
            try:
                from app.services.historical_data import (
                    get_box_month_over_month_price_change, 
                    get_box_price_history, 
                    get_box_30d_avg_sales,
                    get_rolling_volume_sum
                )
            except ImportError as e:
                # If import fails, set functions to None
                get_box_month_over_month_price_change = None
                get_box_price_history = None
                get_box_30d_avg_sales = None
                get_rolling_volume_sum = None
                print(f"⚠️  Warning: Could not import historical_data functions: {e}")
            
            price_change_mom = None
            if get_box_month_over_month_price_change:
                try:
                    price_change_mom = get_box_month_over_month_price_change(str(db_box.id))
                except Exception as e:
                    print(f"⚠️  Error getting price change: {e}")
                    price_change_mom = None
            if price_change_mom is not None:
                box_data["metrics"]["floor_price_30d_change_pct"] = price_change_mom
            
            # Calculate 30d average sales from historical data
            avg_sales_30d = None
            if get_box_30d_avg_sales:
                try:
                    avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
                except Exception as e:
                    print(f"⚠️  Error getting avg sales: {e}")
                    avg_sales_30d = None
            if avg_sales_30d is not None:
                box_data["metrics"]["boxes_sold_30d_avg"] = avg_sales_30d
            
            # Get rolling volume sums for accurate rankings
            # These are ACTUAL sums of daily volumes, not extrapolations
            volume_7d = None
            volume_30d = None
            if get_rolling_volume_sum:
                try:
                    volume_7d = get_rolling_volume_sum(str(db_box.id), 7)
                    volume_30d = get_rolling_volume_sum(str(db_box.id), 30)
                    # Add to metrics if available
                    if volume_7d is not None:
                        box_data["metrics"]["volume_7d"] = float(volume_7d)
                    if volume_30d is not None:
                        box_data["metrics"]["volume_30d"] = float(volume_30d)
                except Exception as e:
                    print(f"⚠️  Error getting volume sums: {e}")
                    volume_7d = None
                    volume_30d = None
            
            # Get the most recent historical entry with calculated metrics
            historical_data = None
            if get_box_price_history:
                try:
                    historical_data = get_box_price_history(str(db_box.id), days=90)
                except Exception as e:
                    print(f"⚠️  Error getting price history: {e}")
                    historical_data = None
            if historical_data:
                latest_historical = historical_data[-1]
                
                # PRIORITY: Use historical floor_price_usd (from Apify marketPrice - more accurate)
                hist_floor = latest_historical.get("floor_price_usd")
                if hist_floor and hist_floor > 0:
                    box_data["metrics"]["floor_price_usd"] = hist_floor
                
                # Use historical 7d EMA
                hist_ema = latest_historical.get("unified_volume_7d_ema")
                if hist_ema and hist_ema > 0:
                    box_data["metrics"]["unified_volume_7d_ema"] = hist_ema
                
                # Use historical daily volume (24h) - prioritize this over calculated
                hist_daily_vol = latest_historical.get("daily_volume_usd")
                if hist_daily_vol and hist_daily_vol > 0:
                    box_data["metrics"]["daily_volume_usd"] = hist_daily_vol
                # If no historical daily volume, keep the calculated one from above
                
                # PRIORITY: Use Apify's calculated 30d volume (daily_vol * 30)
                hist_30d_vol = latest_historical.get("unified_volume_usd")
                if hist_30d_vol and hist_30d_vol > 0:
                    box_data["metrics"]["unified_volume_usd"] = hist_30d_vol
                elif hist_daily_vol and hist_daily_vol > 0:
                    # Fallback to extrapolation if not in historical
                    box_data["metrics"]["unified_volume_usd"] = hist_daily_vol * 30
                # If no historical 30d volume and no daily volume, ensure we have a value
                # If no historical 30d volume, try to calculate from available metrics
                # NOTE: Do NOT use unified_volume_7d_ema - it's an EMA, not a sum
                elif not box_data["metrics"].get("unified_volume_usd"):
                    if box_data["metrics"].get("volume_30d"):
                        box_data["metrics"]["unified_volume_usd"] = float(box_data["metrics"]["volume_30d"])
                    elif box_data["metrics"].get("volume_7d"):
                        # Estimate 30d from 7d sum
                        box_data["metrics"]["unified_volume_usd"] = float(box_data["metrics"]["volume_7d"]) * (30 / 7)
                
                # Ensure daily_volume_usd exists after historical data processing
                # NOTE: Do NOT use unified_volume_7d_ema - it's an EMA, not a sum, so dividing by 7 is incorrect
                if not box_data["metrics"].get("daily_volume_usd"):
                    if box_data["metrics"].get("unified_volume_usd"):
                        # unified_volume_usd is typically daily_volume_usd * 30
                        box_data["metrics"]["daily_volume_usd"] = float(box_data["metrics"]["unified_volume_usd"]) / 30
                
                # Ensure unified_volume_usd exists after historical data processing
                if not box_data["metrics"].get("unified_volume_usd"):
                    # Prefer volume_30d (actual rolling sum) if available
                    if box_data["metrics"].get("volume_30d"):
                        box_data["metrics"]["unified_volume_usd"] = float(box_data["metrics"]["volume_30d"])
                    elif box_data["metrics"].get("daily_volume_usd"):
                        box_data["metrics"]["unified_volume_usd"] = float(box_data["metrics"]["daily_volume_usd"]) * 30
                    elif box_data["metrics"].get("volume_7d"):
                        # Estimate 30d from 7d sum
                        box_data["metrics"]["unified_volume_usd"] = float(box_data["metrics"]["volume_7d"]) * (30 / 7)
                
                # PRIORITY: Use Apify's calculated 7d volume (daily_vol * 7)
                hist_7d_vol = latest_historical.get("volume_7d")
                if hist_7d_vol and hist_7d_vol > 0:
                    box_data["metrics"]["volume_7d"] = hist_7d_vol
                elif hist_daily_vol and hist_daily_vol > 0:
                    # Fallback to extrapolation if not in historical
                    box_data["metrics"]["volume_7d"] = hist_daily_vol * 7
                
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
    
    # Sort by the requested field (default: unified_volume_7d_ema)
    def get_sort_value(box):
        val = box.get("metrics", {}).get(sort)
        if val is None or val == 0:
            # If the sort field is missing, try to calculate from available metrics
            metrics = box.get("metrics", {})
            if sort == "daily_volume_usd":
                # Try to calculate from 30d volume (NOT from EMA - EMA is not a sum)
                if metrics.get("unified_volume_usd"):
                    return float(metrics["unified_volume_usd"]) / 30
                elif metrics.get("volume_7d"):
                    # If we have 7d sum, estimate daily from that
                    return float(metrics["volume_7d"]) / 7
            elif sort == "unified_volume_usd":
                # Try to calculate from daily volume or 7d sum
                if metrics.get("daily_volume_usd"):
                    return float(metrics["daily_volume_usd"]) * 30
                elif metrics.get("volume_7d"):
                    # Estimate 30d from 7d sum
                    return float(metrics["volume_7d"]) * (30 / 7)
                elif metrics.get("volume_30d"):
                    # Use actual 30d sum if available
                    return float(metrics["volume_30d"])
            elif sort == "unified_volume_7d_ema":
                # unified_volume_7d_ema is an EMA (smoothed average), not a sum
                # For sorting purposes, use the actual EMA value if available
                # Fallback to calculated estimates if needed
                if metrics.get("unified_volume_7d_ema"):
                    return float(metrics["unified_volume_7d_ema"])
                elif metrics.get("volume_7d"):
                    # If we have the actual 7d sum, use it (better than EMA for sorting)
                    return float(metrics["volume_7d"])
                elif metrics.get("daily_volume_usd"):
                    # Estimate: daily * 7 (but this is a sum, not an EMA)
                    return float(metrics["daily_volume_usd"]) * 7
                elif metrics.get("unified_volume_usd"):
                    return float(metrics["unified_volume_usd"]) * (7 / 30)
            elif sort == "volume_7d":
                # For volume_7d, prefer the actual rolling sum, fallback to calculated values
                # NOTE: Do NOT use unified_volume_7d_ema - it's an EMA, not a 7-day sum
                if metrics.get("volume_7d"):
                    return float(metrics["volume_7d"])
                elif metrics.get("daily_volume_usd"):
                    return float(metrics["daily_volume_usd"]) * 7
                elif metrics.get("unified_volume_usd"):
                    return float(metrics["unified_volume_usd"]) * (7 / 30)
            return 0  # Put None/zero values at the end (0 sorts last when reverse=True)
        try:
            float_val = float(val) if isinstance(val, (int, float, str)) else 0
            return float_val if float_val > 0 else 0  # Ensure positive values for sorting
        except (ValueError, TypeError):
            return 0
    
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


# Box detail endpoint - requires authentication and active subscription
@app.get("/booster-boxes/{box_id}")
async def get_box_detail(
    box_id: str,
    current_user = Depends(require_active_subscription) if require_active_subscription is not None else Depends(get_optional_user),
):
    """
    Get detailed information for a specific booster box.
    Requires authentication and active subscription (trial or paid).
    """
    """
    Box detail endpoint - fetches from database with historical data for accurate metrics
    Supports both UUID and numeric rank-based lookups
    """
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.booster_box import BoosterBox
    try:
        from app.services.historical_data import get_box_price_history, get_box_month_over_month_price_change
    except ImportError:
        get_box_price_history = None
        get_box_month_over_month_price_change = None
    
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
                hist = None
                if get_box_price_history:
                    try:
                        hist = get_box_price_history(str(b.id), days=90)
                    except Exception as e:
                        hist = None
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
        try:
            from app.services.historical_data import get_box_30d_avg_sales
        except ImportError:
            get_box_30d_avg_sales = None
        
        historical_data = None
        if get_box_price_history:
            try:
                historical_data = get_box_price_history(str(db_box.id), days=90)
            except Exception as e:
                print(f"⚠️  Error getting price history: {e}")
                historical_data = None
        
        box_metrics = {}
        if historical_data:
            latest = historical_data[-1]
            
            # Get values for calculations
            active_listings = latest.get("active_listings_count") or 0
            boxes_sold_per_day = latest.get("boxes_sold_per_day") or 0
            
            # Get 30d average sales FIRST (needed for days_to_20pct calculation)
            avg_sales_30d = latest.get("boxes_sold_30d_avg")
            if avg_sales_30d is None and get_box_30d_avg_sales:
                try:
                    avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
                except Exception as e:
                    print(f"⚠️  Error getting avg sales: {e}")
                    avg_sales_30d = None
            
            # Get avg boxes added per day (may be None if not captured yet)
            avg_boxes_added_per_day = latest.get("avg_boxes_added_per_day") or 0
            
            # Calculate days_to_20pct_increase using full formula:
            # T₊ = inventory below +20% tier (active_listings_count)
            # net_burn_rate = boxes_sold_30d_avg - avg_boxes_added_per_day
            # days_to_20pct = T₊ / net_burn_rate
            days_to_20pct = None
            if avg_sales_30d and avg_sales_30d > 0 and active_listings:
                net_burn_rate = avg_sales_30d - avg_boxes_added_per_day
                
                if net_burn_rate > 0.05:  # Meaningful burn rate
                    days_to_20pct = round(active_listings / net_burn_rate, 2)
                    # Cap at 180 days max
                    if days_to_20pct > 180:
                        days_to_20pct = 180.0
                elif net_burn_rate <= 0:
                    # More boxes being added than sold - price won't rise
                    days_to_20pct = None  # Display as N/A
                else:
                    # Too slow to be meaningful (< 0.05 net burn)
                    days_to_20pct = 180.0  # Show as max
            
            # Calculate liquidity_score: higher = more liquid
            # Based on sell rate vs listings - quick sellers get higher scores
            liquidity_score = latest.get("liquidity_score")
            if liquidity_score is None and avg_sales_30d and avg_sales_30d > 0:
                if active_listings and active_listings > 0:
                    raw_score = (avg_sales_30d / active_listings) * 100
                    liquidity_score = round(min(raw_score, 10), 1)  # Cap at 10
                else:
                    liquidity_score = 5.0  # Default mid-range if no listing data
            
            # Calculate volumes from daily if not already set
            daily_vol = latest.get("daily_volume_usd") or 0
            volume_7d = latest.get("volume_7d") or (daily_vol * 7 if daily_vol else 0)
            volume_30d = latest.get("unified_volume_usd") or (daily_vol * 30 if daily_vol else 0)
            
            box_metrics = {
                "floor_price_usd": latest.get("floor_price_usd"),
                "floor_price_1d_change_pct": latest.get("floor_price_1d_change_pct"),
                "active_listings_count": active_listings,
                "daily_volume_usd": daily_vol,
                "volume_7d": volume_7d,
                "unified_volume_usd": volume_30d,
                "unified_volume_7d_ema": latest.get("unified_volume_7d_ema"),
                "boxes_sold_per_day": boxes_sold_per_day,
                "boxes_added_today": latest.get("boxes_added_today"),
                "days_to_20pct_increase": days_to_20pct,
                "liquidity_score": liquidity_score,
                "boxes_sold_30d_avg": avg_sales_30d,
            }
        
        # Add 30d price change
        price_change_30d = None
        if get_box_month_over_month_price_change:
            try:
                price_change_30d = get_box_month_over_month_price_change(str(db_box.id))
            except Exception as e:
                print(f"⚠️  Error getting price change: {e}")
                price_change_30d = None
        if price_change_30d is not None:
            box_metrics["floor_price_30d_change_pct"] = price_change_30d
        
        # boxes_sold_30d_avg already set above, but keep fallback just in case
        if "boxes_sold_30d_avg" not in box_metrics or box_metrics["boxes_sold_30d_avg"] is None:
            if get_box_30d_avg_sales:
                try:
                    avg_sales_30d = get_box_30d_avg_sales(str(db_box.id))
                    if avg_sales_30d is not None:
                        box_metrics["boxes_sold_30d_avg"] = avg_sales_30d
                except Exception as e:
                    print(f"⚠️  Error getting avg sales: {e}")
        
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


# Historical time-series data endpoint - requires authentication and active subscription
@app.get("/booster-boxes/{box_id}/time-series")
async def get_box_time_series(
    box_id: str,
    metric: str = "floor_price",
    days: int = 30,
    one_per_month: bool = False,
    current_user = Depends(require_active_subscription) if require_active_subscription is not None else Depends(get_optional_user),
):
    """
    Get historical time-series data for a booster box.
    Requires authentication and active subscription (trial or paid).
    """
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
        price_history = None
        if get_box_price_history:
            try:
                price_history = get_box_price_history(box_id, days=days if days > 0 else None, one_per_month=one_per_month)
            except Exception as e:
                print(f"⚠️  Error getting price history: {e}")
                price_history = None
        
        if not price_history:
            return JSONResponse(
                status_code=404,
                content={"detail": "No price history data available for this box"}
            )
        
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
