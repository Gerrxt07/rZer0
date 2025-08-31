"""
A FastAPI application running with rloop and granian.
"""

import asyncio
import rloop
from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

# Import endpoint routers
from .modules.endpoints.root import router as root_router
from .modules.endpoints.health import router as health_router
from .modules.endpoints.docs import create_docs_router

# Set rloop as the event loop policy for better performance
asyncio.set_event_loop_policy(rloop.EventLoopPolicy())

# Initialize FastAPI application
app = FastAPI(
    title="rZer0",
    description="A simple FastAPI application running with rloop and granian.",
    version="1.0.0",
    docs_url=None,  # Disable Swagger UI docs
    redoc_url=None,  # Disable Redoc docs
)

# Include endpoint routers
app.include_router(root_router)
app.include_router(health_router)

# Create and include docs router with app configuration
docs_router = create_docs_router(
    app_title=app.title,
    openapi_url=app.openapi_url or "/openapi.json"
)
app.include_router(docs_router)