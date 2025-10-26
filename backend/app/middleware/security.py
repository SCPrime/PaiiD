"""
CSRF Protection and XSS Security Middleware

Implements comprehensive CSRF token validation and XSS protection for state-changing operations.
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware

    Validates CSRF tokens for state-changing HTTP methods (POST, PUT, DELETE, PATCH).
    Skips validation for safe methods (GET, HEAD, OPTIONS) and health check endpoints.

    Token validation:
    - Expects X-CSRF-Token header on state-changing requests
    - Tokens are generated per-session and stored in-memory
    - Tokens expire after 1 hour
    """

    def __init__(self, app, exempt_paths: list[str] | None = None, testing_mode: bool = False):
        super().__init__(app)
        # Testing mode disables CSRF validation (TestClient doesn't maintain state)
        self.testing_mode = testing_mode

        # Paths that should be exempt from CSRF validation
        self.exempt_paths = exempt_paths or [
            "/api/health",
            "/api/monitor/health",
            "/api/monitor/ping",
            "/api/monitor/version",
            "/api/auth/login",  # Login doesn't have a token yet
            "/api/auth/register",  # Registration doesn't have a token yet
            "/api/auth/refresh",  # Token refresh needs special handling
            "/api/proposals",  # Options trade proposals (idempotent with requestId)
            "/docs",  # Swagger documentation
            "/openapi.json",  # OpenAPI spec
            "/redoc",  # ReDoc documentation
        ]

        # In-memory token store (would use Redis in production)
        # Format: {token: (created_at, user_id)}
        self._tokens: dict[str, tuple[datetime, str | None]] = {}

        # Token expiration time (1 hour)
        self.token_ttl = timedelta(hours=1)

    def _is_safe_method(self, method: str) -> bool:
        """Check if HTTP method is safe (doesn't modify state)"""
        return method in ["GET", "HEAD", "OPTIONS"]

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from CSRF validation"""
        for exempt_path in self.exempt_paths:
            if path.startswith(exempt_path):
                return True
        return False

    def generate_csrf_token(self, user_id: str | None = None) -> str:
        """
        Generate a new CSRF token

        Args:
            user_id: Optional user identifier to bind token to

        Returns:
            URL-safe CSRF token string
        """
        token = secrets.token_urlsafe(32)
        self._tokens[token] = (datetime.now(UTC), user_id)

        # Clean up expired tokens (basic cleanup)
        self._cleanup_expired_tokens()

        logger.info(f"[CSRF] Generated new token for user: {user_id or 'anonymous'}")
        return token

    def validate_csrf_token(self, token: str, user_id: str | None = None) -> bool:
        """
        Validate a CSRF token

        Args:
            token: CSRF token to validate
            user_id: Optional user identifier to verify token binding

        Returns:
            True if token is valid, False otherwise
        """
        if not token:
            logger.warning("[CSRF] Validation failed: No token provided")
            return False

        token_data = self._tokens.get(token)
        if not token_data:
            logger.warning(f"[CSRF] Validation failed: Token not found")
            return False

        created_at, bound_user_id = token_data

        # Check if token has expired
        if datetime.now(UTC) - created_at > self.token_ttl:
            logger.warning(f"[CSRF] Validation failed: Token expired")
            del self._tokens[token]  # Remove expired token
            return False

        # Check if token is bound to a specific user
        if bound_user_id and user_id and bound_user_id != user_id:
            logger.warning(f"[CSRF] Validation failed: User mismatch")
            return False

        logger.info(f"[CSRF] Token validated successfully for user: {user_id or 'anonymous'}")
        return True

    def _cleanup_expired_tokens(self):
        """Remove expired tokens from the store"""
        now = datetime.now(UTC)
        expired_tokens = [
            token for token, (created_at, _) in self._tokens.items()
            if now - created_at > self.token_ttl
        ]

        for token in expired_tokens:
            del self._tokens[token]

        if expired_tokens:
            logger.info(f"[CSRF] Cleaned up {len(expired_tokens)} expired tokens")

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and validate CSRF token for state-changing operations
        """
        # Skip CSRF validation in testing mode (TestClient doesn't maintain state)
        if self.testing_mode:
            response = await call_next(request)
            self._add_security_headers(response)
            return response

        # Skip CSRF validation for safe methods
        if self._is_safe_method(request.method):
            return await call_next(request)

        # Skip CSRF validation for exempt paths
        if self._is_exempt_path(request.url.path):
            logger.debug(f"[CSRF] Skipping validation for exempt path: {request.url.path}")
            return await call_next(request)

        # Extract CSRF token from headers
        csrf_token = request.headers.get("X-CSRF-Token")

        if not csrf_token:
            logger.warning(
                f"[CSRF] Blocked request to {request.url.path}: Missing X-CSRF-Token header"
            )
            return Response(
                content='{"detail": "CSRF token missing. Include X-CSRF-Token header."}',
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json",
            )

        # Extract user ID from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)

        # Validate token
        if not self.validate_csrf_token(csrf_token, user_id):
            logger.warning(
                f"[CSRF] Blocked request to {request.url.path}: Invalid or expired token"
            )
            return Response(
                content='{"detail": "Invalid or expired CSRF token."}',
                status_code=status.HTTP_403_FORBIDDEN,
                media_type="application/json",
            )

        # Token is valid - proceed with request
        logger.debug(f"[CSRF] Token validated for {request.method} {request.url.path}")
        response = await call_next(request)

        # Add security headers to response
        self._add_security_headers(response)

        return response

    def _add_security_headers(self, response: Response):
        """
        Add comprehensive security headers to response

        These headers provide defense-in-depth against various attacks:
        - XSS attacks
        - Clickjacking
        - MIME sniffing
        - Information leakage
        """
        # Prevent MIME type sniffing
        response.headers.setdefault("X-Content-Type-Options", "nosniff")

        # Prevent clickjacking attacks
        response.headers.setdefault("X-Frame-Options", "DENY")

        # Legacy XSS protection (modern browsers use CSP instead)
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")

        # Enforce HTTPS connections (only meaningful over HTTPS)
        # max-age=31536000 = 1 year
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains; preload"
        )

        # Control referrer information leakage
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

        # Permissions Policy (formerly Feature Policy)
        # Disable dangerous features like camera, microphone, geolocation
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # Content Security Policy (CSP) - Primary XSS defense
        # This is a strict policy suitable for API endpoints
        csp_directives = [
            "default-src 'self'",  # Only load resources from same origin
            "script-src 'self'",  # Only execute scripts from same origin
            "style-src 'self' 'unsafe-inline'",  # Allow inline styles (needed for Swagger)
            "img-src 'self' data: https:",  # Allow images from self, data URIs, and HTTPS
            "font-src 'self' data:",  # Allow fonts from self and data URIs
            "connect-src 'self' https:",  # Allow connections to self and HTTPS endpoints
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


# Global middleware instance for token generation
_csrf_middleware_instance: CSRFProtectionMiddleware | None = None


def get_csrf_middleware() -> CSRFProtectionMiddleware:
    """Get the global CSRF middleware instance"""
    global _csrf_middleware_instance
    if not _csrf_middleware_instance:
        raise RuntimeError("CSRF middleware not initialized")
    return _csrf_middleware_instance


def set_csrf_middleware(middleware: CSRFProtectionMiddleware):
    """Set the global CSRF middleware instance"""
    global _csrf_middleware_instance
    _csrf_middleware_instance = middleware


def generate_csrf_token_endpoint(user_id: str | None = None) -> str:
    """
    Generate a CSRF token (for use in endpoints)

    This function can be called from endpoints to generate tokens
    that clients can use for subsequent state-changing requests.
    """
    middleware = get_csrf_middleware()
    return middleware.generate_csrf_token(user_id)
