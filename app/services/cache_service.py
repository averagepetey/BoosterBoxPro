"""
Cache Service
Redis-based caching for leaderboard and box detail queries
"""

import json
from typing import Any, Optional, Dict, List
from datetime import date, timedelta
from uuid import UUID

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from app.config import settings


class CacheService:
    """Service for caching leaderboard and box detail queries"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = False
        
        if REDIS_AVAILABLE:
            try:
                # Get Redis config from settings (with defaults)
                redis_host = getattr(settings, 'redis_host', 'localhost')
                redis_port = getattr(settings, 'redis_port', 6379)
                redis_password = getattr(settings, 'redis_password', None)
                redis_db = getattr(settings, 'redis_db', 0)
                
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    db=redis_db,
                    decode_responses=True  # Auto-decode to strings
                )
                
                # Test connection
                self.redis_client.ping()
                self.enabled = True
            except Exception as e:
                # Redis not available - continue without cache
                print(f"Redis not available: {e}. Continuing without cache.")
                self.enabled = False
                self.redis_client = None
    
    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string"""
        return json.dumps(value, default=str)
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize JSON string to Python object"""
        return json.loads(value)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return self._deserialize(value)
        except Exception as e:
            # Log error but don't fail - continue without cache
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 300 = 5 minutes)
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            serialized = self._serialize(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            # Log error but don't fail - continue without cache
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    # Convenience methods for common cache keys
    
    def get_leaderboard_cache_key(self, metric_date: date, limit: int = 10) -> str:
        """Generate cache key for leaderboard"""
        return f"leaderboard:top{limit}:{metric_date.isoformat()}"
    
    def get_box_detail_cache_key(self, box_id: UUID, metric_date: date) -> str:
        """Generate cache key for box detail"""
        return f"box:detail:{box_id}:{metric_date.isoformat()}"
    
    def get_time_series_cache_key(self, box_id: UUID, start_date: date, end_date: date) -> str:
        """Generate cache key for time series data"""
        return f"box:timeseries:{box_id}:{start_date.isoformat()}:{end_date.isoformat()}"
    
    def cache_leaderboard(self, metric_date: date, data: List[Dict], limit: int = 10, ttl: int = 900) -> bool:
        """
        Cache leaderboard data
        
        Args:
            metric_date: Date for the leaderboard
            data: Leaderboard data (list of box metrics)
            limit: Number of boxes (10, 50, etc.)
            ttl: Time to live in seconds (default: 900 = 15 minutes)
        
        Returns:
            True if cached successfully
        """
        key = self.get_leaderboard_cache_key(metric_date, limit)
        return self.set(key, data, ttl)
    
    def get_cached_leaderboard(self, metric_date: date, limit: int = 10) -> Optional[List[Dict]]:
        """Get cached leaderboard data"""
        key = self.get_leaderboard_cache_key(metric_date, limit)
        return self.get(key)
    
    def cache_box_detail(self, box_id: UUID, metric_date: date, data: Dict, ttl: int = 600) -> bool:
        """
        Cache box detail data
        
        Args:
            box_id: Box UUID
            metric_date: Date for the metrics
            data: Box detail data
            ttl: Time to live in seconds (default: 600 = 10 minutes)
        
        Returns:
            True if cached successfully
        """
        key = self.get_box_detail_cache_key(box_id, metric_date)
        return self.set(key, data, ttl)
    
    def get_cached_box_detail(self, box_id: UUID, metric_date: date) -> Optional[Dict]:
        """Get cached box detail data"""
        key = self.get_box_detail_cache_key(box_id, metric_date)
        return self.get(key)
    
    def invalidate_leaderboard(self, metric_date: date) -> None:
        """Invalidate all leaderboard caches for a date"""
        if not self.enabled:
            return
        
        # Delete common leaderboard cache keys
        for limit in [10, 50, 100]:
            key = self.get_leaderboard_cache_key(metric_date, limit)
            self.delete(key)
    
    def invalidate_box_detail(self, box_id: UUID, metric_date: date) -> None:
        """Invalidate box detail cache for a date"""
        key = self.get_box_detail_cache_key(box_id, metric_date)
        self.delete(key)

    def invalidate_all_data_caches(self) -> int:
        """
        Invalidate all leaderboard, box detail, and time-series caches (e.g. after daily refresh).
        Uses Redis KEYS; returns number of keys deleted.
        """
        if not self.enabled or not self.redis_client:
            return 0
        deleted = 0
        try:
            for pattern in ("leaderboard:*", "box:detail:*", "box:timeseries:*", "market:*"):
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    deleted += len(keys)
        except Exception as e:
            print(f"Cache invalidate_all_data_caches error: {e}")
        return deleted


# Global instance
cache_service = CacheService()

