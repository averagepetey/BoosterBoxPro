"""
SQLAlchemy Database Models
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Import models
from .booster_box import BoosterBox
from .unified_box_metrics import UnifiedBoxMetrics
from .user import User
from .market_index import MarketIndexDaily

__all__ = ["Base", "BoosterBox", "UnifiedBoxMetrics", "User", "MarketIndexDaily"]









