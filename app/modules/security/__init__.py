"""
Security module for rZer0 application.

This module contains security-related middleware including CORS configuration
and security headers for the FastAPI application.
"""

from .middleware import setup_cors_middleware
from .headers import setup_security_headers

__all__ = [
    "setup_cors_middleware",
    "setup_security_headers",
]