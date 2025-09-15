"""
Cache status endpoint for monitoring performance optimizations.
"""

from fastapi import APIRouter, HTTPException
from ..logging import logger
from ..performance.caching import get_cache_manager

router = APIRouter()


@router.get("/cache-status")
async def cache_status():
    """Get cache status and statistics."""
    logger.debug("Cache status requested")
    
    try:
        cache = await get_cache_manager()
        stats = await cache.get_stats()
        
        logger.info("Cache status retrieved", entries=stats.get("cache_entries", 0))
        return stats
        
    except Exception as e:
        logger.error("Failed to get cache status", error=str(e))
        return {
            "connected": False,
            "error": str(e),
            "cache_entries": 0,
            "cache_type": "redis"
        }


@router.post("/cache-clear")
async def cache_clear():
    """Clear all cache entries."""
    logger.debug("Cache clear requested")
    
    try:
        cache = await get_cache_manager()
        await cache.clear()
        
        logger.info("Cache cleared successfully")
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
        
    except Exception as e:
        logger.error("Failed to clear cache", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
