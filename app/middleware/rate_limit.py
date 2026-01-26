"""
Rate Limiting Configuration
Uses slowapi for request rate limiting
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.middleware.security import get_real_client_ip


def get_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    Uses real client IP (respecting proxies) + optional user ID.
    """
    client_ip = get_real_client_ip(request)
    
    # If user is authenticated, also include their user ID
    # This prevents one user from consuming another's rate limit
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        # Hash the token to create a user identifier without exposing the token
        import hashlib
        token_hash = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
        return f"{client_ip}:{token_hash}"
    
    return client_ip


# Create limiter instance with proxy-aware IP detection
limiter = Limiter(key_func=get_identifier)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded errors.
    Returns a 429 response with retry-after header.
    """
    import logging
    
    client_ip = get_real_client_ip(request)
    logging.warning(
        f"Rate limit exceeded: {request.method} {request.url.path} from {client_ip}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down.",
            "error": "rate_limit_exceeded",
            "retry_after": exc.detail.split()[-1] if exc.detail else "60",
        },
        headers={
            "Retry-After": exc.detail.split()[-1] if exc.detail else "60",
            "X-RateLimit-Limit": str(getattr(exc, 'limit', 'unknown')),
        }
    )


# Rate limit constants - adjust based on your needs
class RateLimits:
    """
    Rate limit definitions.
    Format: "requests/period" where period is second, minute, hour, day
    """
    
    # Authentication endpoints (strict to prevent brute force)
    LOGIN = "5/minute"          # 5 login attempts per minute
    REGISTER = "3/minute"       # 3 registration attempts per minute
    PASSWORD_RESET = "3/hour"   # 3 password reset requests per hour
    
    # API endpoints (more lenient)
    LEADERBOARD = "60/minute"   # 60 requests per minute
    BOX_DETAIL = "120/minute"   # 120 requests per minute
    TIME_SERIES = "30/minute"   # 30 requests per minute (expensive query)
    
    # Admin endpoints
    ADMIN = "30/minute"         # 30 requests per minute
    
    # General API (fallback)
    DEFAULT = "100/minute"      # 100 requests per minute


# Decorator shortcuts for common limits
def limit_auth(func):
    """Rate limit for authentication endpoints"""
    return limiter.limit(RateLimits.LOGIN)(func)


def limit_register(func):
    """Rate limit for registration endpoint"""
    return limiter.limit(RateLimits.REGISTER)(func)


def limit_api(func):
    """Rate limit for general API endpoints"""
    return limiter.limit(RateLimits.DEFAULT)(func)


def limit_expensive(func):
    """Rate limit for expensive/heavy endpoints"""
    return limiter.limit(RateLimits.TIME_SERIES)(func)
