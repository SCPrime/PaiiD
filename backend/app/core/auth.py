import logging

from fastapi import Header, HTTPException, status

from .config import settings


# Add logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def require_bearer(authorization: str = Header(None)):
    logger.debug("=" * 50)
    logger.debug("AUTH MIDDLEWARE CALLED")
    print(f"\n{'=' * 50}", flush=True)
    print("AUTH MIDDLEWARE CALLED", flush=True)
    print(f"Authorization header: {authorization}", flush=True)

    if not authorization:
        logger.error("❌ No authorization header provided")
        print("❌ ERROR: No authorization header", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header"
        )

    if not authorization.startswith("Bearer "):
        logger.error(f"❌ Invalid authorization format: {authorization[:20]}")
        print(f"❌ ERROR: Invalid auth format: {authorization[:20]}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization format"
        )

    token = authorization.split(" ", 1)[1]
    logger.debug(f"Received token: {token[:10]}...")
    logger.debug(
        f"Expected token: {settings.API_TOKEN[:10] if settings.API_TOKEN else 'NOT_SET'}..."
    )

    print(f"[AUTH] Received: [{token}]", flush=True)
    print(f"[AUTH] Expected: [{settings.API_TOKEN}]", flush=True)
    print(f"[AUTH] Match: {token == settings.API_TOKEN}", flush=True)

    if not settings.API_TOKEN:
        logger.error("❌ API_TOKEN not set in environment!")
        print("❌ ERROR: API_TOKEN not configured", flush=True)
        raise HTTPException(status_code=500, detail="Server configuration error")

    if token != settings.API_TOKEN:
        logger.error("❌ Token mismatch!")
        print("❌ ERROR: Token mismatch", flush=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    logger.debug("✅ Authentication successful")
    print("✅ Authentication successful", flush=True)
    print(f"{'=' * 50}\n", flush=True)
    return token


def get_current_user_id(token: str = None) -> int:
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


def get_current_user_id_str(token: str = None) -> str:
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
