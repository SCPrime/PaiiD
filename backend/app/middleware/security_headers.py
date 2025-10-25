"""
Security Headers Middleware

Adds common security headers (CSP, HSTS, X-Frame-Options, etc.).
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Basic protections
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        # HSTS (note: only meaningful over HTTPS)
        response.headers.setdefault(
            "Strict-Transport-Security", "max-age=15552000; includeSubDomains"
        )
        # CSP (relatively relaxed, adjust as needed)
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; "
            "connect-src 'self' https: http:; "
            "font-src 'self' data:; "
            "object-src 'none'; frame-ancestors 'none'"
        )
        response.headers.setdefault("Content-Security-Policy", csp)
        return response
