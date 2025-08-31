"""
A FastAPI application running with rloop and granian.
"""

import asyncio
import rloop
from fastapi import FastAPI

# Import configuration
from .modules.config import config

# Import endpoint routers
from .modules.endpoints.root import router as root_router
from .modules.endpoints.health import router as health_router
from .modules.endpoints.docs import create_docs_router

# Set rloop as the event loop policy for better performance
asyncio.set_event_loop_policy(rloop.EventLoopPolicy())

# Initialize FastAPI application with configuration
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    openapi_url=config.OPENAPI_URL,
)

# Include endpoint routers
app.include_router(root_router)
app.include_router(health_router)

# Create and include docs router with app configuration
docs_router = create_docs_router(
    app_title=config.APP_NAME,
    openapi_url=config.OPENAPI_URL
)
app.include_router(docs_router)