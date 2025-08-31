"""
Endpoints module for the rZer0 API.

This module contains all API endpoint definitions organized by functionality.
Each endpoint is in its own file for better maintainability and organization.
"""

from .root import router as root_router
from .health import router as health_router
from .docs import create_docs_router

__all__ = [
    "root_router",
    "health_router", 
    "create_docs_router"
]
