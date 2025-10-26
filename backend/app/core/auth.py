import logging

from fastapi import Header, HTTPException, status

from .config import settings
from .logging_utils import get_secure_logger, redact_auth_header


# Use secure logger with automatic redaction
logger = get_secure_logger(__name__)


def require_bearer(authorization: str = Header(None)):
    """
    DEPRECATED: Use unified_auth.get_current_user_unified() instead

    This function is kept for backwards compatibility only.
    Validates simple API token authentication.
    """
    if not authorization:
        logger.error("Authentication failed: Missing authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        logger.error(
            "Authentication failed: Invalid format",
            auth_header=redact_auth_header(authorization)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    if not settings.API_TOKEN:
        logger.error("Server misconfiguration: API_TOKEN not set")
        raise HTTPException(status_code=500, detail="Server configuration error")

    if token != settings.API_TOKEN:
        logger.error(
            "Authentication failed: Invalid token",
            token_length=len(token)
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    logger.debug("API token authentication successful")
    return token


def get_current_user_id(token: str | None = None) -> int:
    """
    Get the current user ID from the authenticated token.

    SINGLE-USER MVP: Currently returns user_id=1 for all authenticated requests.

    FUTURE (Multi-user support):
        - Decode JWT token to extract user_id claim
        - Validate user exists in database
        - Return actual user_id from token payload

    Args:
        token: Bearer token (currently unused, reserved for JWT decoding)

    Returns:
        int: User ID (always 1 in current MVP implementation)
    """
    # MVP: Single user system - all authenticated requests map to user_id=1
    # This will be replaced with JWT decoding when multi-user support is added
    return 1


def get_current_user_id_str(token: str | None = None) -> str:
    """
    Get the current user ID as a string (for file-based storage keys).

    SINGLE-USER MVP: Currently returns "default" for all authenticated requests.

    See get_current_user_id() for future multi-user implementation plan.

    Args:
        token: Bearer token (currently unused, reserved for JWT decoding)

    Returns:
        str: User ID string (always "default" in current MVP implementation)
    """
    # MVP: Single user system - use "default" as user identifier
    return "default"
