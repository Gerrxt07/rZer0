"""
A FastAPI application running with rloop and granian.
"""

import asyncio
import rloop
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

# Import configuration
from .modules.config import config

# Import endpoint routers
from .modules.endpoints.root import router as root_router
from .modules.endpoints.health import router as health_router
from .modules.endpoints.docs import create_docs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events for multiprocessing optimization.
    """
    # Startup
    # Set rloop as the event loop policy for better performance
    asyncio.set_event_loop_policy(rloop.EventLoopPolicy())
    
    # Additional multiprocessing optimizations can be added here
    # such as database connection pools, cache connections, etc.
    
    yield
    
    # Shutdown
    # Cleanup resources if needed

# Initialize FastAPI application with configuration
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    docs_url=config.DOCS_URL,
    redoc_url=config.REDOC_URL,
    openapi_url=config.OPENAPI_URL,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
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