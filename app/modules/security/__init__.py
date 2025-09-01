"""
Security module for rZer0 application.

This module contains security-related middleware including CORS configuration,
security headers, and rate limiting for the FastAPI application.
"""

from .middleware import setup_cors_middleware
from .headers import setup_security_headers
from .ratelimit import (
    init_rate_limiter,
    close_rate_limiter,
    rate_limiter,
    rate_limit_exceeded_handler
)

__all__ = [
    "setup_cors_middleware",
    "setup_security_headers",
    "init_rate_limiter",
    "close_rate_limiter", 
    "rate_limiter",
    "rate_limit_exceeded_handler"
]