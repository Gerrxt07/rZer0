"""
Security Headers Middleware for rZer0 application.

This module provides security headers middleware for the FastAPI application,
implementing common security headers to protect against various web vulnerabilities.
"""

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    This middleware adds common security headers that help protect against
    various web vulnerabilities like XSS, clickjacking, MIME type sniffing, etc.
    """

    def __init__(
        self,
        app,
        hsts_max_age: int = 31536000,  # 1 year in seconds
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = True,
        csp_policy: str = None,
        frame_options: str = "DENY",
        content_type_options: str = "nosniff",
        xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: str = None
    ):
        """
        Initialize the security headers middleware.
        
        Args:
            app: The ASGI application
            hsts_max_age: Max age for HSTS header in seconds
            hsts_include_subdomains: Include subdomains in HSTS
            hsts_preload: Enable HSTS preload
            csp_policy: Content Security Policy string
            frame_options: X-Frame-Options value  
            content_type_options: X-Content-Type-Options value
            xss_protection: X-XSS-Protection value
            referrer_policy: Referrer-Policy value
            permissions_policy: Permissions-Policy value
        """
        super().__init__(app)
        self.hsts_max_age = hsts_max_age
        self.hsts_include_subdomains = hsts_include_subdomains
        self.hsts_preload = hsts_preload
        self.csp_policy = csp_policy or self._default_csp_policy()
        self.frame_options = frame_options
        self.content_type_options = content_type_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy or self._default_permissions_policy()

    def _default_csp_policy(self) -> str:
        """Generate a default Content Security Policy."""
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )

    def _default_permissions_policy(self) -> str:
        """Generate a default Permissions Policy."""
        return (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "keyboard-map=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "navigation-override=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add security headers to the response.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint
            
        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)
        
        return response

    def _add_security_headers(self, response: Response) -> None:
        """Add all configured security headers to the response."""
        
        # HTTP Strict Transport Security (HSTS)
        hsts_value = f"max-age={self.hsts_max_age}"
        if self.hsts_include_subdomains:
            hsts_value += "; includeSubDomains"
        if self.hsts_preload:
            hsts_value += "; preload"
        response.headers["Strict-Transport-Security"] = hsts_value

        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy

        # X-Frame-Options (clickjacking protection)
        response.headers["X-Frame-Options"] = self.frame_options

        # X-Content-Type-Options (MIME type sniffing protection)
        response.headers["X-Content-Type-Options"] = self.content_type_options

        # X-XSS-Protection (XSS protection for older browsers)
        response.headers["X-XSS-Protection"] = self.xss_protection

        # Referrer Policy
        response.headers["Referrer-Policy"] = self.referrer_policy

        # Permissions Policy (feature policy)
        response.headers["Permissions-Policy"] = self.permissions_policy

        # Server header (remove or customize server identification)
        response.headers["Server"] = "rZer0"

        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"


def setup_security_headers(
    app: FastAPI,
    hsts_max_age: int = 31536000,
    hsts_include_subdomains: bool = True,
    hsts_preload: bool = True,
    csp_policy: str = None,
    frame_options: str = "DENY",
    content_type_options: str = "nosniff",
    xss_protection: str = "1; mode=block",
    referrer_policy: str = "strict-origin-when-cross-origin",
    permissions_policy: str = None
) -> None:
    """
    Set up security headers middleware for the FastAPI application.
    
    This function adds the SecurityHeadersMiddleware to the FastAPI app
    with the specified configuration.
    
    Args:
        app: FastAPI application instance
        hsts_max_age: Max age for HSTS header in seconds (default: 1 year)
        hsts_include_subdomains: Include subdomains in HSTS (default: True)
        hsts_preload: Enable HSTS preload (default: True)
        csp_policy: Content Security Policy string (uses default if None)
        frame_options: X-Frame-Options value (default: "DENY")
        content_type_options: X-Content-Type-Options value (default: "nosniff")
        xss_protection: X-XSS-Protection value (default: "1; mode=block")
        referrer_policy: Referrer-Policy value (default: "strict-origin-when-cross-origin")
        permissions_policy: Permissions-Policy value (uses default if None)
    """
    
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_max_age=hsts_max_age,
        hsts_include_subdomains=hsts_include_subdomains,
        hsts_preload=hsts_preload,
        csp_policy=csp_policy,
        frame_options=frame_options,
        content_type_options=content_type_options,
        xss_protection=xss_protection,
        referrer_policy=referrer_policy,
        permissions_policy=permissions_policy
    )