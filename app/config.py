"""
Application Configuration
Loads settings from environment variables

SECURITY: Critical settings must be set via environment variables in production.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Admin API Key (simple auth for manual entry endpoints)
    admin_api_key: Optional[str] = None
    
    # CORS - Production domains (comma-separated in .env)
    # Example: CORS_ORIGINS=https://boosterboxpro.com,https://www.boosterboxpro.com
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    # Rate limiting
    rate_limit_enabled: bool = True
    
    # Redis Cache (Phase 6)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    redis_url: Optional[str] = None  # Override host/port/password if provided (e.g., redis://localhost:6379/0)
    
    # Cache TTLs (in seconds)
    cache_ttl_leaderboard: int = 900  # 15 minutes
    cache_ttl_box_detail: int = 600  # 10 minutes
    cache_ttl_time_series: int = 1800  # 30 minutes
    
    # Authentication & Security (Phase 8)
    # SECURITY: In production, JWT_SECRET_KEY MUST be set to a long random string
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
    jwt_secret_key: str = "change-me-in-production-use-strong-random-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7  # Note: actual expiry is now 30 min in code
    
    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        """
        SECURITY: Warn if using default JWT secret.
        In production, this should fail instead of warn.
        """
        default_secret = "change-me-in-production-use-strong-random-key"
        if v == default_secret:
            # Check environment - in production this should be an error
            import os
            env = os.getenv('ENVIRONMENT', 'development')
            if env == 'production':
                raise ValueError(
                    "CRITICAL: JWT_SECRET_KEY must be changed in production! "
                    "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
                )
            else:
                logger.warning(
                    "⚠️  Using default JWT secret - this is INSECURE for production! "
                    "Set JWT_SECRET_KEY in your .env file."
                )
        elif len(v) < 32:
            logger.warning("⚠️  JWT secret is short - recommend at least 64 characters")
        return v
    
    # Stripe (Phase 8)
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # Apify API (TCGplayer scraping)
    apify_api_token: Optional[str] = None
    
    # Future: Marketplace API keys
    # tcgplayer_api_key: Optional[str] = None
    # ebay_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

