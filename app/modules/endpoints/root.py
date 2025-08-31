"""
Root endpoint for the rZer0 API.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint returning a simple greeting."""
    return JSONResponse({
        "message": "Hello World!",
        "status": "running"
    })
