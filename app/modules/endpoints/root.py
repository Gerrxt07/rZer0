"""
Root endpoint for the rZer0 API.
"""

from fastapi import APIRouter, Depends
from ..logging import logger
from ..performance.caching import cache_response

router = APIRouter()


@router.get("/")
@cache_response(ttl=60, key_prefix="root_")  # Cache for 1 minute
async def root():
    """Root endpoint returning a simple greeting."""
    logger.debug("Root endpoint accessed")
    
    response = {
        "message": "Hello World!",
        "status": "running"
    }
    
    logger.info("Root endpoint response sent")
    
    return response
