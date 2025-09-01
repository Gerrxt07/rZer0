"""
Rate limiting module for rZer0 application.

This module provides IP-based rate limiting using dragonflydb (Redis-compatible)
and fastapi-limiter with sliding window algorithm for precise rate limiting.
Supports Cloudflare proxy headers for accurate client IP detection.
"""

try:
    import zangy
    ZANGY_AVAILABLE = True
except ImportError:
    ZANGY_AVAILABLE = False
    # Fallback to redis for environments where zangy is not available
    try:
        import redis.asyncio as fallback_redis
        REDIS_FALLBACK = True
    except ImportError:
        REDIS_FALLBACK = False

from fastapi import Request, HTTPException, status
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from typing import Optional
import asyncio

from ..config import config
from ..logging import logger
from .middleware import get_real_client_ip


async def init_rate_limiter() -> None:
    """
    Initialize the rate limiter with Zangy connection (preferred) or Redis fallback.
    
    This function sets up the connection to Dragonfly (Redis-compatible)
    using Zangy connection pool if available, otherwise falls back to Redis client.
    
    Zangy uses connection pools created with create_pool() for optimal performance,
    especially in high-concurrency scenarios. It beats similar Python libraries
    by fair margins and excels in parallel operations.
    """
    try:
        if ZANGY_AVAILABLE:
            # Create Zangy connection pool optimized for rate limiting workload
            # Pool size chosen based on expected concurrent rate limit checks
            # Zangy distributes actions over the pool using round robin
            pool = await zangy.create_pool(
                config.REDIS_URL,
                10,  # Regular connections for rate limiting operations
                2    # PubSub connections (minimal for rate limiting use case)
            )
            
            # Test the connection with a ping operation
            # Zangy supports standard Redis operations like ping
            await pool.execute("PING")
            logger.info("Using Zangy connection pool for rate limiting", 
                       redis_url=config.REDIS_URL,
                       pool_size=10,
                       pubsub_size=2,
                       performance_note="Zangy excels in concurrent scenarios")
            
            # Store the pool reference for use with FastAPILimiter
            redis_client = pool
            
        elif REDIS_FALLBACK:
            # Fallback to standard Redis client
            redis_client = fallback_redis.from_url(
                config.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            # Test the connection
            await redis_client.ping()
            logger.warning("Zangy not available, using Redis fallback client", redis_url=config.REDIS_URL)
        else:
            raise ImportError("Neither Zangy nor Redis client libraries are available")
        
        logger.info("Connected to Dragonfly for rate limiting", 
                   client_type="Zangy" if ZANGY_AVAILABLE else "Redis",
                   redis_url=config.REDIS_URL)
        
        # Initialize FastAPILimiter with Redis connection/pool
        # Zangy pool is compatible with fastapi-limiter as it supports Redis operations
        await FastAPILimiter.init(redis_client)
        logger.info("Rate limiter initialized successfully")
        
    except Exception as e:
        logger.error("Failed to initialize rate limiter", error=str(e))
        raise


async def close_rate_limiter() -> None:
    """
    Close the rate limiter and Redis connections gracefully.
    """
    try:
        await FastAPILimiter.close()
        logger.info("Rate limiter closed successfully")
    except Exception as e:
        logger.warning("Error closing rate limiter", error=str(e))


def get_client_ip_for_rate_limiting(request: Request) -> str:
    """
    Get client IP for rate limiting using the existing middleware function.
    
    This reuses the get_real_client_ip function from middleware.py which already
    handles Cloudflare headers (CF-Connecting-IP) and proxy headers (X-Forwarded-For).
    
    Args:
        request: FastAPI/Starlette request object
        
    Returns:
        str: The real client IP address
    """
    return get_real_client_ip(request)


async def async_get_client_ip_for_rate_limiting(request: Request) -> str:
    """
    Async wrapper for getting client IP for rate limiting.
    
    fastapi-limiter expects an async identifier function, so this wraps
    the synchronous get_real_client_ip function.
    
    Args:
        request: FastAPI/Starlette request object
        
    Returns:
        str: The real client IP address
    """
    return get_real_client_ip(request)


def create_rate_limit_dependency():
    """
    Create a rate limit dependency that can be used as a FastAPI dependency.
    
    This creates a RateLimiter dependency using a sliding window algorithm
    that extracts the real client IP considering proxy headers.
    
    Returns:
        RateLimiter: Configured rate limiter dependency
    """
    if not config.RATE_LIMIT_ENABLED:
        # If rate limiting is disabled, return a no-op dependency
        async def no_rate_limit():
            return None
        return no_rate_limit
    
    # Create rate limiter with sliding window
    # Times format: "requests/seconds" 
    rate_limit_str = f"{config.RATE_LIMIT_REQUESTS}/{config.RATE_LIMIT_WINDOW}s"
    
    return RateLimiter(
        times=config.RATE_LIMIT_REQUESTS,
        seconds=config.RATE_LIMIT_WINDOW,
        identifier=async_get_client_ip_for_rate_limiting
    )


async def rate_limit_exceeded_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
    """
    Handle rate limit exceeded exceptions.
    
    This function is called when a rate limit is exceeded and returns
    a proper 429 Too Many Requests response.
    
    Args:
        request: FastAPI request object
        exc: HTTPException raised by rate limiter
        
    Returns:
        ORJSONResponse: 429 response with rate limit message
    """
    client_ip = get_client_ip_for_rate_limiting(request)
    
    # Log the rate limit violation
    logger.warning(
        "Rate limit exceeded", 
        client_ip=client_ip,
        path=request.url.path,
        method=request.method,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    # Return 429 Too Many Requests response
    return ORJSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Too Many Requests",
            "message": config.RATE_LIMIT_MESSAGE,
            "status_code": 429,
            "detail": "Rate limit exceeded. Please slow down your requests."
        },
        headers={
            "Retry-After": str(config.RATE_LIMIT_WINDOW),
            "X-RateLimit-Limit": str(config.RATE_LIMIT_REQUESTS),
            "X-RateLimit-Window": str(config.RATE_LIMIT_WINDOW)
        }
    )


# Create the global rate limiter dependency
rate_limiter = create_rate_limit_dependency()