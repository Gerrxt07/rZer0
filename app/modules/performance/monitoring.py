"""
Performance monitoring middleware and utilities.
"""

import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to add performance monitoring headers."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add performance monitoring to requests."""
        start_time = time.perf_counter()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.perf_counter() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))  # milliseconds
        response.headers["X-Timestamp"] = str(int(time.time()))
        
        return response


def setup_performance_monitoring(app: FastAPI) -> None:
    """
    Set up performance monitoring middleware.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(PerformanceMonitoringMiddleware)
