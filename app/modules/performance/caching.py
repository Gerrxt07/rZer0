"""
Response caching utilities for improved performance using redis-py with async support.
"""

import asyncio
import pickle
from typing import Any, Dict, Optional
from functools import wraps
import redis.asyncio as redis
from redis.asyncio import Redis


class CacheManager:
    """Redis-based cache manager for responses using aioredis."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 300):
        """
        Initialize cache manager with Redis connection.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live for cache entries in seconds
        """
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._redis: Optional[Redis] = None
        
    async def connect(self) -> None:
        """Establish Redis connection."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    self.redis_url,
                    decode_responses=False,  # We'll handle encoding manually
                    socket_connect_timeout=2,
                    socket_timeout=2,
                    retry_on_timeout=True
                )
                # Test connection
                await self._redis.ping()
            except Exception as e:
                # Fallback to in-memory cache if Redis is unavailable
                self._redis = None
                raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if self._redis is None:
            await self.connect()
            
        try:
            data = await self._redis.get(f"cache:{key}")
            if data is None:
                return None
            return pickle.loads(data)
        except Exception:
            # Return None if cache lookup fails
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in Redis cache with expiration."""
        if self._redis is None:
            await self.connect()
            
        if ttl is None:
            ttl = self.default_ttl
            
        try:
            serialized_value = pickle.dumps(value)
            await self._redis.setex(f"cache:{key}", ttl, serialized_value)
        except Exception:
            # Silently fail if cache set fails
            pass
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        if self._redis is None:
            await self.connect()
            
        try:
            # Delete all keys matching cache:* pattern
            keys = await self._redis.keys("cache:*")
            if keys:
                await self._redis.delete(*keys)
        except Exception:
            # Silently fail if cache clear fails
            pass
    
    async def size(self) -> int:
        """Get number of cached entries."""
        if self._redis is None:
            await self.connect()
            
        try:
            keys = await self._redis.keys("cache:*")
            return len(keys)
        except Exception:
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        if self._redis is None:
            await self.connect()
            
        try:
            info = await self._redis.info("memory")
            stats = {
                "connected": True,
                "memory_used": info.get("used_memory_human", "N/A"),
                "memory_peak": info.get("used_memory_peak_human", "N/A"),
                "cache_entries": await self.size(),
                "cache_type": "redis"
            }
            return stats
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "cache_entries": 0,
                "cache_type": "redis"
            }


# Global cache instance - will be initialized in the FastAPI lifespan
cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or initialize the global cache manager."""
    global cache_manager
    if cache_manager is None:
        # Import config here to avoid circular imports
        from ..config import config
        cache_manager = CacheManager(
            redis_url=config.REDIS_URL,
            default_ttl=300
        )
        await cache_manager.connect()
    return cache_manager


def cache_response(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache endpoint responses using Redis.
    
    Args:
        ttl: Time-to-live for cache in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            try:
                # Get cache manager
                cache = await get_cache_manager()
                
                # Try to get from cache
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Cache the result
                await cache.set(cache_key, result, ttl)
                return result
                
            except Exception:
                # If caching fails, execute function without caching
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
        return wrapper
    return decorator
