"""
Application Configuration
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Admin API Key (simple auth for manual entry endpoints)
    admin_api_key: Optional[str] = None
    
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
    jwt_secret_key: str = "change-me-in-production-use-strong-random-key"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7
    
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

