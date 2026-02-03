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
import time

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
# In production, restrict to specific domains + allow *.vercel.app
if settings.environment == "development":
    cors_origins = ["*"]
    cors_credentials = False
    cors_origin_regex = None
    logger.info("🔓 CORS: Development mode - allowing all origins")
else:
    cors_origins = settings.cors_origins_list
    cors_credentials = True
    # Allow any https *.vercel.app so Vercel production + preview URLs work without listing each one
    cors_origin_regex = r"https://.*\.vercel\.app"
    logger.info(f"🔒 CORS: Production - origins: {cors_origins}, regex: *.vercel.app")
    if not cors_origins:
        logger.warning("⚠️  CORS_ORIGINS is empty - *.vercel.app still allowed via regex. Add CORS_ORIGINS for custom domains.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
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


@app.get("/health/cron")
async def cron_health():
    """
    Cron job health check endpoint.
    Returns status of last daily refresh run.
    Can be monitored by UptimeRobot or similar services.
    """
    from pathlib import Path
    import json
    from datetime import datetime, timedelta
    
    status_file = Path(__file__).parent / "logs" / "daily_refresh_status.json"
    
    if not status_file.exists():
        return {
            "status": "unknown",
            "message": "No status file found - cron may not have run yet",
            "last_check": None
        }
    
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        last_end_time = status.get("end_time")
        if last_end_time:
            try:
                last_end = datetime.fromisoformat(last_end_time.replace('Z', '+00:00'))
                hours_ago = (datetime.now(last_end.tzinfo) - last_end).total_seconds() / 3600
            except:
                hours_ago = None
        else:
            hours_ago = None
        
        # Consider unhealthy if:
        # - Last run was more than 25 hours ago (should run daily ~1pm EST)
        # - Last run failed (overall_success = false)
        is_healthy = True
        message = "Cron is healthy"
        
        if status.get("status") == "running":
            is_healthy = True
            message = "Cron is currently running"
        elif not status.get("overall_success", False):
            is_healthy = False
            message = f"Cron last run failed: {status.get('apify', {}).get('error') or status.get('scraper', {}).get('error') or 'Unknown error'}"
        elif hours_ago and hours_ago > 25:
            is_healthy = False
            message = f"Cron hasn't run in {hours_ago:.1f} hours (expected daily)"
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "message": message,
            "last_run": {
                "end_time": last_end_time,
                "hours_ago": round(hours_ago, 1) if hours_ago else None,
                "overall_success": status.get("overall_success", False),
                "apify_success": status.get("apify", {}).get("success_count", 0),
                "apify_errors": status.get("apify", {}).get("error_count", 0),
                "scraper_success": status.get("scraper", {}).get("success_count", 0),
                "scraper_errors": status.get("scraper", {}).get("error_count", 0),
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to read status file: {str(e)}",
            "last_check": None
        }


@app.post("/admin/invalidate-cache")
async def admin_invalidate_cache(request: Request):
    """
    Invalidate all API caches so leaderboard and box detail serve fresh data.
    Called by the daily refresh job when it completes. Requires INVALIDATE_CACHE_SECRET.
    """
    secret = request.headers.get("X-Invalidate-Secret") or request.query_params.get("secret")
    if not settings.invalidate_cache_secret or secret != settings.invalidate_cache_secret:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    # Clear in-memory leaderboard cache (defined below in this module)
    _leaderboard_cache.clear()
    # Clear historical entries JSON cache so next request reads fresh from file/DB
    try:
        from app.services.historical_data import invalidate_historical_entries_cache
        invalidate_historical_entries_cache()
    except Exception as e:
        logger.warning(f"invalidate_historical_entries_cache: {e}")
    # Clear Redis caches (leaderboard, box detail, time-series)
    redis_deleted = 0
    try:
        from app.services.cache_service import cache_service
        redis_deleted = cache_service.invalidate_all_data_caches()
    except Exception as e:
        logger.warning(f"cache_service.invalidate_all_data_caches: {e}")
    logger.info("Cache invalidated (leaderboard in-memory + historical entries + Redis)")
    return {"ok": True, "message": "Caches invalidated", "redis_keys_deleted": redis_deleted}


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

from app.services.box_detail_service import (
    build_box_detail_data,
    get_box_image_url,
    get_manual_liquidity_reprint,
    get_manual_community_sentiment,
    get_top_10_value_usd,
    set_code_from_product_name,
)

# In-memory response cache for leaderboard (repeat requests return instantly)
_leaderboard_cache: dict = {}


# Leaderboard endpoint - requires authentication and active subscription
@app.get("/booster-boxes")
async def get_booster_boxes(
    sort: str = "unified_volume_usd",  # Primary ranking metric: 30-day raw volume
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(require_active_subscription) if require_active_subscription is not None else Depends(get_optional_user),
):
    """
    Get leaderboard of booster boxes.
    Requires authentication and active subscription (trial or paid).
    Default sort: unified_volume_usd (30-day raw volume sum)
    """
    """
    Leaderboard endpoint - combines static box info with live database metrics
    """
    cache_key = (sort, limit, offset)
    now_ts = time.time()
    if cache_key in _leaderboard_cache:
        cached_response, expiry = _leaderboard_cache[cache_key]
        if now_ts < expiry:
            return cached_response
    import json
    from pathlib import Path
    from datetime import date
    from sqlalchemy import select, desc, func, and_
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
    
    # Query database for all boxes and their latest metrics (batch: 2 queries + 1 historical call)
    async with AsyncSessionLocal() as db:
        # 1) All booster boxes
        stmt = select(BoosterBox)
        result = await db.execute(stmt)
        db_boxes = result.scalars().all()
        
        # 2) Latest UnifiedBoxMetrics per box in one query
        subq = (
            select(UnifiedBoxMetrics.booster_box_id, func.max(UnifiedBoxMetrics.metric_date).label("md"))
            .group_by(UnifiedBoxMetrics.booster_box_id)
        ).subquery()
        mstmt = select(UnifiedBoxMetrics).join(
            subq,
            and_(
                UnifiedBoxMetrics.booster_box_id == subq.c.booster_box_id,
                UnifiedBoxMetrics.metric_date == subq.c.md,
            ),
        )
        mres = await db.execute(mstmt)
        metrics_list = mres.scalars().all()
        metrics_by_box = {str(m.booster_box_id): m for m in metrics_list}
        
        # 3) Batch historical snapshot for all boxes (one DB hit)
        try:
            from app.services.historical_data import get_all_boxes_latest_for_leaderboard
            box_ids = [str(b.id) for b in db_boxes]
            hist_by_box = get_all_boxes_latest_for_leaderboard(box_ids)
        except Exception:
            hist_by_box = {}
        
        result_boxes = []
        seen_product_names = set()
        
        for db_box in db_boxes:
            if "(Test)" in db_box.product_name or "Test Box" in db_box.product_name:
                continue
            # Exclude legacy generic OP-01 Romance Dawn (we track Blue and White separately)
            if db_box.product_name == "One Piece - OP-01 Romance Dawn Booster Box":
                continue
            if db_box.product_name in seen_product_names:
                continue
            seen_product_names.add(db_box.product_name)
            
            latest_metrics = metrics_by_box.get(str(db_box.id))
            hist = hist_by_box.get(str(db_box.id), {})
            
            # Start with JSON data if available (exact product_name), else match by set code (OP-07, PRB-01, etc.)
            json_box = json_boxes_by_name.get(db_box.product_name, {})
            if not json_box and boxes:
                set_code = set_code_from_product_name(db_box.product_name)
                if set_code:
                    for b in boxes:
                        if b.get("product_name") and set_code in b.get("product_name", "").upper():
                            json_box = b
                            break
            
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
                continue
            
            # Overlay batch historical snapshot (floor_price, volumes, 30d change, etc.)
            if hist:
                if hist.get("floor_price_1d_change_pct") is not None:
                    box_data["metrics"]["floor_price_1d_change_pct"] = float(hist["floor_price_1d_change_pct"])
                if hist.get("floor_price_30d_change_pct") is not None:
                    box_data["metrics"]["floor_price_30d_change_pct"] = hist["floor_price_30d_change_pct"]
                if hist.get("volume_1d_change_pct") is not None:
                    box_data["metrics"]["volume_1d_change_pct"] = float(hist["volume_1d_change_pct"])
                if hist.get("volume_7d_change_pct") is not None:
                    box_data["metrics"]["volume_7d_change_pct"] = float(hist["volume_7d_change_pct"])
                if hist.get("volume_30d_change_pct") is not None:
                    box_data["metrics"]["volume_30d_change_pct"] = float(hist["volume_30d_change_pct"])
                if hist.get("boxes_sold_30d_avg") is not None:
                    box_data["metrics"]["boxes_sold_30d_avg"] = hist["boxes_sold_30d_avg"]
                if hist.get("volume_7d") is not None:
                    box_data["metrics"]["volume_7d"] = float(hist["volume_7d"])
                if hist.get("volume_30d") is not None:
                    box_data["metrics"]["volume_30d"] = float(hist["volume_30d"])
                # Prefer historical floor/volume when present (Apify/market data)
                if hist.get("floor_price_usd") and hist["floor_price_usd"] > 0:
                    box_data["metrics"]["floor_price_usd"] = hist["floor_price_usd"]
                if hist.get("unified_volume_7d_ema") and hist["unified_volume_7d_ema"] > 0:
                    box_data["metrics"]["unified_volume_7d_ema"] = hist["unified_volume_7d_ema"]
                if hist.get("daily_volume_usd") and hist["daily_volume_usd"] > 0:
                    box_data["metrics"]["daily_volume_usd"] = hist["daily_volume_usd"]
                if hist.get("unified_volume_usd") and hist["unified_volume_usd"] > 0:
                    box_data["metrics"]["unified_volume_usd"] = hist["unified_volume_usd"]
                if hist.get("boxes_sold_per_day") is not None:
                    box_data["metrics"]["boxes_sold_per_day"] = hist["boxes_sold_per_day"]
                if hist.get("boxes_added_today") is not None:
                    box_data["metrics"]["boxes_added_today"] = hist["boxes_added_today"]
                if hist.get("active_listings_count") is not None:
                    box_data["metrics"]["active_listings_count"] = hist["active_listings_count"]
            
            # volume_30d from hist is the rolling total (sum of daily floor×sold over last 30d); use as-is.
            # Ramp formula was for sparse data; with daily refreshes we use rolling totals only.
            
            # OP-13 manual overrides: reprint risk High, liquidity High (90)
            if "OP-13" in (box_data.get("product_name") or ""):
                box_data["reprint_risk"] = "HIGH"
                box_data["metrics"]["liquidity_score"] = 90
            
            # Manual liquidity and reprint risk by set (overrides DB/calculated values)
            manual_liq, manual_reprint = get_manual_liquidity_reprint(db_box.product_name)
            if manual_liq is not None:
                box_data["metrics"]["liquidity_score"] = manual_liq
            if manual_reprint is not None:
                box_data["reprint_risk"] = manual_reprint
            # Manual community sentiment by set
            manual_sentiment = get_manual_community_sentiment(db_box.product_name)
            if manual_sentiment is not None:
                box_data["metrics"]["community_sentiment"] = manual_sentiment

            # Top 10 cards value (manual data from spreadsheet; match by product_name or set code)
            top_10 = get_top_10_value_usd(db_box.product_name)
            if top_10 is not None:
                box_data["metrics"]["top_10_value_usd"] = top_10
            # If still missing and we have json_box metrics, use JSON top_10
            if top_10 is None and json_box.get("metrics", {}).get("top_10_value_usd") is not None:
                box_data["metrics"]["top_10_value_usd"] = float(json_box["metrics"]["top_10_value_usd"])
            # If still missing, ensure days_to_20pct from JSON is used when DB didn't provide it
            if json_box.get("metrics", {}).get("days_to_20pct_increase") is not None and box_data["metrics"].get("days_to_20pct_increase") is None:
                box_data["metrics"]["days_to_20pct_increase"] = float(json_box["metrics"]["days_to_20pct_increase"])
            
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
    
    response = {
        "data": paginated_boxes,
        "meta": {
            "total": total,
            "sort": sort,
            "sort_direction": "desc",
            "limit": limit,
            "offset": offset,
        }
    }
    ttl = settings.cache_ttl_leaderboard
    _leaderboard_cache[cache_key] = (response, now_ts + ttl)
    return response


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
        
        # If not found and box_id is numeric, find by rank from leaderboard (single batch to avoid N×get_box_price_history)
        if not db_box and box_id.isdigit():
            all_boxes_stmt = select(BoosterBox)
            all_result = await db.execute(all_boxes_stmt)
            all_boxes = all_result.scalars().all()
            valid = [b for b in all_boxes if "(Test)" not in (b.product_name or "") and "Test Box" not in (b.product_name or "")]
            if not valid:
                db_box = None
            else:
                try:
                    from app.services.historical_data import get_all_boxes_latest_for_leaderboard
                    box_ids = [str(b.id) for b in valid]
                    hist_by_box = get_all_boxes_latest_for_leaderboard(box_ids)
                    # Sort by volume (7d EMA or 30d), then pick by rank
                    def vol_key(b):
                        h = hist_by_box.get(str(b.id), {})
                        return float(h.get("unified_volume_7d_ema") or h.get("volume_30d") or h.get("unified_volume_usd") or 0)
                    valid.sort(key=vol_key, reverse=True)
                    rank = int(box_id)
                    if 1 <= rank <= len(valid):
                        db_box = valid[rank - 1]
                    else:
                        db_box = None
                except Exception:
                    # Fallback: no historical batch, use first box (avoid N calls)
                    db_box = valid[0] if int(box_id) == 1 else None
        
        if not db_box:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Box with ID {box_id} not found"}
            )
        
        data = await build_box_detail_data(db, db_box)
        return {"data": data}


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
