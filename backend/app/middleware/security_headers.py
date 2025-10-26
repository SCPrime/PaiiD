"""
Security Headers Middleware

Adds comprehensive security headers (CSP, HSTS, X-Frame-Options, etc.) to all responses.
This middleware provides defense-in-depth against XSS, clickjacking, and other attacks.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security Headers Middleware

    Adds essential security headers to all HTTP responses:
    - Content Security Policy (CSP) - Primary XSS defense
    - Strict Transport Security (HSTS) - Enforce HTTPS
    - X-Frame-Options - Prevent clickjacking
    - X-Content-Type-Options - Prevent MIME sniffing
    - X-XSS-Protection - Legacy XSS protection
    - Referrer-Policy - Control referrer information
    - Permissions-Policy - Disable dangerous browser features
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Prevent clickjacking attacks
        response.headers.setdefault("X-Frame-Options", "DENY")

        # Control referrer information leakage
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

        # Legacy XSS protection (modern browsers use CSP instead)
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")

        # Enforce HTTPS connections (only meaningful over HTTPS)
        # max-age=31536000 = 1 year (increased from 180 days for better security)
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload"
        )

        # Permissions Policy (formerly Feature Policy)
        # Disable dangerous features like camera, microphone, geolocation, payment
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Content Security Policy (CSP) - Primary XSS defense
        # Balanced policy: strict but compatible with Swagger/ReDoc documentation
        csp_directives = [
            "default-src 'self'",  # Only load resources from same origin
            "script-src 'self' 'unsafe-inline'",  # Allow inline scripts (needed for Swagger)
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles (needed for Swagger)
            "img-src 'self' data: https:",  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from self and data URIs
            "connect-src 'self' https: http:",  # Allow API calls to self and external HTTPS/HTTP
            "frame-ancestors 'none'",  # Prevent embedding in iframes (defense-in-depth)
            "base-uri 'self'",  # Restrict base tag to same origin
            "form-action 'self'",  # Restrict form submissions to same origin
            "object-src 'none'",  # Block plugins (Flash, Java, etc.)
            "upgrade-insecure-requests",  # Upgrade HTTP to HTTPS automatically
        ]
        response.headers.setdefault(
            "Content-Security-Policy",
            "; ".join(csp_directives)
        )

        return response
