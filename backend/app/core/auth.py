import logging

from fastapi import Header, HTTPException, status

from .config import settings


# Add logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def require_bearer(authorization: str = Header(None)):
    """
    Validates Bearer token authentication.
    Security: NO tokens are logged - only validation status.
    """
    logger.debug("=" * 50)
    logger.debug("AUTH MIDDLEWARE CALLED")

    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        logger.warning("Invalid authorization format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]

    # 🔒 SECURITY: Log only token prefix, never full token
    logger.debug(f"Received token: {token[:10]}...")
    logger.debug(f"Expected token: {settings.API_TOKEN[:10] if settings.API_TOKEN else 'NOT_SET'}...")

    if not settings.API_TOKEN:
        logger.error("API_TOKEN not set in environment!")
        raise HTTPException(status_code=500, detail="Server configuration error")

    if token != settings.API_TOKEN:
        logger.warning("Token mismatch")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    logger.debug("✅ Authentication successful")
    logger.debug("=" * 50)
    return token
