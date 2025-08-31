"""
Health check endpoint for the rZer0 API.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    # Get current time in Frankfurt, Germany timezone
    berlin_tz = ZoneInfo('Europe/Berlin')
    now = datetime.now(berlin_tz)
    
    # Format date as DD:MM:YYYY
    date_formatted = now.strftime('%d:%m:%Y')
    
    # Format time as HH:MM:SS
    time_formatted = now.strftime('%H:%M:%S')
    
    return {
        "status": "online",
        "date": date_formatted,
        "time": time_formatted
    }
