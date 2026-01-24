"""
Security Middleware
Adds security headers to all responses
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.config import settings
import uuid
import time
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses.
    
    Headers added:
    - Strict-Transport-Security (HSTS) - Forces HTTPS
    - X-Content-Type-Options - Prevents MIME sniffing
    - X-Frame-Options - Prevents clickjacking
    - X-XSS-Protection - Legacy XSS protection
    - Referrer-Policy - Controls referrer information
    - Permissions-Policy - Restricts browser features
    - Content-Security-Policy - Controls resource loading (basic)
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Only add HSTS in production (requires HTTPS)
        if settings.environment == "production":
            # HSTS: Force HTTPS for 1 year, include subdomains
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking - deny all framing
        response.headers["X-Frame-Options"] = "DENY"
        
        # Legacy XSS protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Restrict browser features we don't need
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        # Basic CSP (can be customized per route if needed)
        if settings.environment == "production":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs all incoming requests with correlation IDs.
    
    Adds:
    - X-Request-ID header to responses
    - Request logging with timing information
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate correlation ID
        request_id = str(uuid.uuid4())[:8]
        
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Get client IP
        client_ip = get_real_client_ip(request)
        
        # Log request
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"from {client_ip} - Status: {response.status_code} ({duration_ms:.1f}ms)"
        )
        
        # Add correlation ID to response
        response.headers["X-Request-ID"] = request_id
        
        return response


def get_real_client_ip(request: Request) -> str:
    """
    Get the real client IP address, respecting proxy headers.
    
    Checks headers in order of priority:
    1. CF-Connecting-IP (Cloudflare)
    2. X-Real-IP (nginx)
    3. X-Forwarded-For (standard proxy header)
    4. Direct connection IP
    """
    # Cloudflare
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()
    
    # nginx / other proxies
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Standard proxy header (take first IP)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Direct connection
    if request.client:
        return request.client.host
    
    return "unknown"
