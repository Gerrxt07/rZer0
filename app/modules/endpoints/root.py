"""
Root endpoint for the rZer0 API.
"""

from fastapi import APIRouter, Depends
from ..logging import logger

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint returning a simple greeting."""
    logger.debug("Root endpoint accessed")
    
    response = {
        "message": "Hello World!",
        "status": "running"
    }
    
    logger.info("Root endpoint response sent", response_message=response["message"], status=response["status"])
    
    return response
