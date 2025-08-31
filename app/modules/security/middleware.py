"""
CORS Middleware configuration for rZer0 application.

This module provides CORS (Cross-Origin Resource Sharing) middleware setup
for the FastAPI application, configured for production use with Cloudflare proxy.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional


def setup_cors_middleware(
    app: FastAPI,
    allowed_origins: Optional[List[str]] = None,
    allowed_methods: Optional[List[str]] = None,
    allowed_headers: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allow_origin_regex: Optional[str] = None
) -> None:
    """
    Set up CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins. Defaults to ["*"] for development
        allowed_methods: List of allowed HTTP methods
        allowed_headers: List of allowed headers
        allow_credentials: Whether to allow credentials in CORS requests
        allow_origin_regex: Regex pattern for allowed origins
    """
    
    # Default configuration suitable for development and Cloudflare proxy
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            # Add production domains here as needed
        ]
    
    if allowed_methods is None:
        allowed_methods = [
            "GET",
            "POST", 
            "PUT",
            "DELETE",
            "OPTIONS",
            "HEAD",
            "PATCH"
        ]
    
    if allowed_headers is None:
        allowed_headers = [
            "*",  # Allow all headers for flexibility
            "Authorization",
            "Content-Type",
            "Accept",
            "Origin",
            "User-Agent",
            "DNT",
            "Cache-Control",
            "X-Mx-ReqToken",
            "Keep-Alive",
            "X-Requested-With",
            "If-Modified-Since",
            # Cloudflare headers
            "CF-Connecting-IP",
            "CF-RAY",
            "CF-Visitor"
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        allow_origin_regex=allow_origin_regex,
    )


def get_real_client_ip(request) -> str:
    """
    Extract the real client IP address considering Cloudflare proxy.
    
    This function checks various headers to determine the real client IP,
    prioritizing Cloudflare headers when available.
    
    Args:
        request: FastAPI/Starlette request object
        
    Returns:
        str: The real client IP address
    """
    # Priority order for IP detection with Cloudflare
    headers_to_check = [
        "CF-Connecting-IP",  # Cloudflare's real client IP
        "X-Forwarded-For",   # Standard proxy header
        "X-Real-IP",         # Nginx proxy header
        "X-Forwarded",       # Alternative forwarded header
        "Forwarded-For",     # Another alternative
        "Forwarded"          # RFC 7239 standard
    ]
    
    for header in headers_to_check:
        value = request.headers.get(header)
        if value:
            # X-Forwarded-For can contain multiple IPs, take the first one
            if header == "X-Forwarded-For":
                return value.split(",")[0].strip()
            return value.strip()
    
    # Fallback to the direct client address
    return request.client.host if request.client else "unknown"