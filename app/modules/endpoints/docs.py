"""
API documentation endpoint for the rZer0 API.
"""

from fastapi import APIRouter
from scalar_fastapi import get_scalar_api_reference

router = APIRouter()


def create_docs_router(app_title: str, openapi_url: str):
    """
    Create the docs router with app configuration.
    """
    @router.get("/docs", include_in_schema=False)
    async def scalar_html():
        """
        Serve the Scalar API Reference documentation.
        """
        return get_scalar_api_reference(
            openapi_url=openapi_url,
            title=app_title,
        )
    return router
