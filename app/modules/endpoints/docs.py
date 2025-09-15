"""
API documentation endpoint for the rZer0 API.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from scalar_fastapi import get_scalar_api_reference
from ..performance.caching import cache_response

router = APIRouter()


def create_docs_router(app_title: str, openapi_url: str):
    """
    Create the docs router with app configuration.
    """
    @router.get("/docs", include_in_schema=False, response_class=HTMLResponse)
    @cache_response(ttl=300, key_prefix="docs_")  # Cache for 5 minutes
    async def scalar_html():
        """
        Serve the Scalar API Reference documentation.
        """
        return get_scalar_api_reference(
            openapi_url=openapi_url,
            title=app_title,
        )
    return router
