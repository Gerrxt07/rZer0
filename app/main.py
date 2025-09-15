"""
A FastAPI application running with rloop and granian.
"""

import asyncio
import os
import sys
import rloop
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import ORJSONResponse

# Import configuration
from .modules.config import config

# Import logging
from .modules.logging import logger, stop_async_logging

# Import endpoint routers
from .modules.endpoints.root import router as root_router
from .modules.endpoints.health import router as health_router
from .modules.endpoints.cache import router as cache_router
from .modules.endpoints.docs import create_docs_router

# Import security middleware
from .modules.security import (
    setup_cors_middleware, 
    setup_security_headers
)

# Import performance optimizations
from .modules.performance import (
    setup_compression_middleware,
    setup_performance_monitoring
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events for multiprocessing optimization.
    """
    # Startup
    logger.info("Starting rZer0 application", version=config.APP_VERSION)
    logger.debug("Setting rloop as event loop policy for better performance")
    
    # Set rloop as the event loop policy for better performance
    asyncio.set_event_loop_policy(rloop.EventLoopPolicy())
    
    # Initialize Redis cache connection
    logger.debug("Initializing Redis cache connection")
    try:
        from .modules.performance.caching import get_cache_manager
        cache = await get_cache_manager()
        logger.info("Redis cache connection established")
    except Exception as e:
        logger.warning("Failed to connect to Redis cache, continuing without caching", error=str(e))
    
    # Additional multiprocessing optimizations can be added here
    # such as database connection pools, cache connections, etc.
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down rZer0 application")
    
    # Cleanup Redis connection
    logger.debug("Closing Redis cache connection")
    try:
        from .modules.performance.caching import cache_manager
        if cache_manager:
            await cache_manager.disconnect()
        logger.info("Redis cache connection closed")
    except Exception as e:
        logger.warning("Error closing Redis cache connection", error=str(e))
    
    # Stop async logging gracefully
    try:
        stop_async_logging(timeout=config.LOG_ASYNC_SHUTDOWN_TIMEOUT)
        logger.info("Async logging stopped gracefully")
    except Exception as e:
        # Use print as fallback since logging might be stopped
        print(f"Warning: Error stopping async logging: {e}", file=sys.stderr)
    
    logger.info("Application shutdown completed")

logger.info("Initializing FastAPI application", name=config.APP_NAME, description=config.APP_DESCRIPTION)

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

logger.debug("Setting up security middleware")

# Set up performance optimizations first (middleware order matters)
logger.debug("Setting up performance optimizations")
setup_performance_monitoring(app)
setup_compression_middleware(app, minimum_size=500)  # Compress responses > 500 bytes

# Set up security middleware
# Note: Middleware is applied in reverse order, so security headers should be added first
setup_security_headers(
    app,
    hsts_max_age=config.SECURITY_HSTS_MAX_AGE,
    hsts_include_subdomains=config.SECURITY_HSTS_INCLUDE_SUBDOMAINS,
    hsts_preload=config.SECURITY_HSTS_PRELOAD,
    frame_options=config.SECURITY_FRAME_OPTIONS,
    csp_policy=config.SECURITY_CSP_POLICY
)

setup_cors_middleware(
    app,
    allowed_origins=config.get_cors_origins() if config.get_cors_origins() else None,
    allowed_methods=config.get_cors_methods(),
    allowed_headers=config.get_cors_headers(),
    allow_credentials=config.CORS_ALLOW_CREDENTIALS
)

logger.debug("Including endpoint routers")

# Include endpoint routers
app.include_router(root_router)
app.include_router(health_router)
app.include_router(cache_router)

# Create and include docs router with app configuration
docs_router = create_docs_router(
    app_title=config.APP_NAME,
    openapi_url=config.OPENAPI_URL
)
app.include_router(docs_router)

logger.success("FastAPI application initialized successfully")