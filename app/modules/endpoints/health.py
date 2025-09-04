"""
Health check endpoint for the rZer0 API.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends
from ..logging import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    
    # Get current time in Frankfurt, Germany timezone
    berlin_tz = ZoneInfo('Europe/Berlin')
    now = datetime.now(berlin_tz)
    
    # Format date as DD:MM:YYYY
    date_formatted = now.strftime('%d:%m:%Y')
    
    # Format time as HH:MM:SS
    time_formatted = now.strftime('%H:%M:%S')
    
    response = {
        "status": "online",
        "date": date_formatted,
        "time": time_formatted
    }
    
    logger.info("Health check completed", status="online", timestamp=f"{date_formatted} {time_formatted}")
    
    return response
