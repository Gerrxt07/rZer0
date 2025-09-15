"""
Compression middleware for better response times and bandwidth usage.
"""

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware


def setup_compression_middleware(app: FastAPI, minimum_size: int = 1000) -> None:
    """
    Set up GZip compression middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        minimum_size: Minimum response size in bytes to compress (default: 1000)
    """
    app.add_middleware(
        GZipMiddleware,
        minimum_size=minimum_size
    )
