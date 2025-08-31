"""
Health check endpoint for the rZer0 API.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    now = datetime.now(timezone.utc)
    
    return JSONResponse({
        "status": "healthy",
        "service": "rZer0",
        "timestamp": now.isoformat(),
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S UTC")
    })
