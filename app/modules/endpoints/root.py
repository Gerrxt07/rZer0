"""
Root endpoint for the rZer0 API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint returning a simple greeting."""
    return {
        "message": "Hello World!",
        "status": "running"
    }
