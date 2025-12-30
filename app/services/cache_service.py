"""
Redis Cache Service
Handles caching for leaderboard, box details, and time-series data
"""

import json
import logging
from typing import Optional, Any
from datetime import date
from uuid import UUID

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available. Caching will be disabled.")

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for Redis caching operations"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False
        
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not installed. Caching disabled.")
            return
        
        try:
            # Use redis_url if provided, otherwise construct from components
            if settings.redis_url:
                redis_url = settings.redis_url
            else:
                # Construct URL from components
                if settings.redis_password:
                    redis_url = f"redis://:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
                else:
                    redis_url = f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"
            
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Don't mark as connected yet - will verify on first use with ping
            self._connected = False
            logger.info(f"Redis cache client created: {settings.redis_host}:{settings.redis_port} (will verify on first use)")
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}. Caching disabled.")
            self._connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/error
        """
        if not REDIS_AVAILABLE or not self.redis_client:
            return None
        
        try:
            # Test connection on first use
            if not self._connected:
                try:
                    await self.redis_client.ping()
                    self._connected = True
                except Exception as e:
                    logger.warning(f"Redis ping failed: {e}")
                    self._connected = False
                    return None
            
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            self._connected = False  # Mark as disconnected on error
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 5 minutes)
            
        Returns:
            True if successful, False otherwise
        """
        if not REDIS_AVAILABLE or not self.redis_client:
            return False
        
        try:
            # Test connection on first use
            if not self._connected:
                try:
                    await self.redis_client.ping()
                    self._connected = True
                except Exception as e:
                    logger.warning(f"Redis ping failed: {e}")
                    self._connected = False
                    return False
            
            serialized = json.dumps(value, default=str)  # default=str handles dates, UUIDs, etc.
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            self._connected = False  # Mark as disconnected on error
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self._connected or not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key to check
            
        Returns:
            True if exists, False otherwise
        """
        if not self._connected or not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
    
    # Convenience methods for specific cache keys
    
    def _leaderboard_key(self, date: date, limit: int) -> str:
        """Generate cache key for leaderboard"""
        return f"leaderboard:top{limit}:{date.isoformat()}"
    
    def _box_detail_key(self, box_id: UUID, date: date) -> str:
        """Generate cache key for box detail"""
        return f"box:detail:{box_id}:{date.isoformat()}"
    
    def _time_series_key(self, box_id: UUID, start_date: date, end_date: date) -> str:
        """Generate cache key for time-series data"""
        return f"box:timeseries:{box_id}:{start_date.isoformat()}:{end_date.isoformat()}"
    
    async def get_cached_leaderboard(
        self,
        target_date: date,
        limit: int
    ) -> Optional[list]:
        """Get cached leaderboard data"""
        key = self._leaderboard_key(target_date, limit)
        return await self.get(key)
    
    async def cache_leaderboard(
        self,
        target_date: date,
        limit: int,
        data: list
    ) -> bool:
        """Cache leaderboard data"""
        key = self._leaderboard_key(target_date, limit)
        return await self.set(key, data, ttl=settings.cache_ttl_leaderboard)
    
    async def get_cached_box_detail_json(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[str]:
        """Get cached box detail data as raw JSON string (bypasses get() deserialization)"""
        if not REDIS_AVAILABLE or not self.redis_client:
            return None
        
        try:
            if not self._connected:
                try:
                    await self.redis_client.ping()
                    self._connected = True
                except Exception as e:
                    logger.warning(f"Redis ping failed: {e}")
                    self._connected = False
                    return None
            
            key = self._box_detail_key(box_id, target_date)
            # Get raw string directly (not deserialized)
            value = await self.redis_client.get(key)
            return value  # Returns None if not found, or JSON string if found
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            self._connected = False
            return None
    
    async def get_cached_box_detail(
        self,
        box_id: UUID,
        target_date: date
    ) -> Optional[str]:
        """Get cached box detail data (returns JSON string for direct response)"""
        return await self.get_cached_box_detail_json(box_id, target_date)
    
    async def cache_box_detail(
        self,
        box_id: UUID,
        target_date: date,
        data: dict
    ) -> bool:
        """Cache box detail data as JSON string"""
        if not REDIS_AVAILABLE or not self.redis_client:
            return False
        
        try:
            if not self._connected:
                try:
                    await self.redis_client.ping()
                    self._connected = True
                except Exception as e:
                    logger.warning(f"Redis ping failed: {e}")
                    self._connected = False
                    return False
            
            key = self._box_detail_key(box_id, target_date)
            # Serialize to JSON string and store directly
            import json
            json_str = json.dumps(data, default=str)
            await self.redis_client.setex(key, settings.cache_ttl_box_detail, json_str)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            self._connected = False
            return False
    
    async def get_cached_time_series(
        self,
        box_id: UUID,
        start_date: date,
        end_date: date
    ) -> Optional[list]:
        """Get cached time-series data"""
        key = self._time_series_key(box_id, start_date, end_date)
        return await self.get(key)
    
    async def cache_time_series(
        self,
        box_id: UUID,
        start_date: date,
        end_date: date,
        data: list
    ) -> bool:
        """Cache time-series data"""
        key = self._time_series_key(box_id, start_date, end_date)
        return await self.set(key, data, ttl=settings.cache_ttl_time_series)


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get or create global cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

