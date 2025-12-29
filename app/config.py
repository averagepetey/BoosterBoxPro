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
    
    # Future: Marketplace API keys
    # tcgplayer_api_key: Optional[str] = None
    # ebay_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

