"""
Unified Authentication System for PaiiD
=======================================

This module provides a clean, unified authentication system that supports:
1. Simple API token auth (for service-to-service)
2. JWT-based user authentication (for multi-user)
3. Automatic fallback for single-user MVP mode

STABILITY: Gibraltar-level - bulletproof error handling and clear auth flow
SECURITY: All tokens are redacted in logs
"""

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.database import User
from .config import settings
from .jwt import decode_token
from .logging_utils import get_secure_logger, redact_auth_header, format_user_for_logging


logger = get_secure_logger(__name__)
security = HTTPBearer()


class AuthMode:
    """Authentication mode selector"""

    API_TOKEN = "api_token"  # Simple token for service-to-service
    JWT = "jwt"  # Full JWT for user sessions
    MVP_FALLBACK = "mvp_fallback"  # Single-user MVP mode


def verify_api_token(authorization: str) -> bool:
    """
    Verify simple API token from Authorization header

    Args:
        authorization: Full Authorization header value

    Returns:
        True if token is valid, False otherwise
    """
    if not authorization or not authorization.startswith("Bearer "):
        return False

    token = authorization.split(" ", 1)[1]
    return token == settings.API_TOKEN


def get_auth_mode(authorization: str | None) -> str:
    """
    Determine which authentication mode to use

    Args:
        authorization: Authorization header value

    Returns:
        AuthMode constant indicating auth type
    """
    if not authorization:
        logger.debug("Auth mode: MVP fallback (no header)")
        return AuthMode.MVP_FALLBACK

    if not authorization.startswith("Bearer "):
        logger.debug("Auth mode: MVP fallback (invalid format)")
        return AuthMode.MVP_FALLBACK

    token = authorization.split(" ", 1)[1]

    # Check if it's the simple API token
    if token == settings.API_TOKEN:
        logger.debug("Auth mode: API_TOKEN")
        return AuthMode.API_TOKEN

    # Otherwise assume it's a JWT
    logger.debug("Auth mode: JWT")
    return AuthMode.JWT


def get_current_user_unified(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None, alias="Authorization", convert_underscores=False),
) -> User:
    """
    Unified authentication that handles both API token and JWT

    This is the MAIN authentication dependency to use in your endpoints.

    Args:
        authorization: Authorization header
        db: Database session

    Returns:
        User object (either from JWT or MVP fallback user)

    Raises:
        HTTPException: 401 if authentication fails
    """
    auth_mode = get_auth_mode(authorization)
    logger.debug(
        "Authentication attempt",
        mode=auth_mode,
        auth_header=redact_auth_header(authorization)
    )

    # CASE 1: Simple API Token (service-to-service or frontend proxy)
    if auth_mode == AuthMode.API_TOKEN:
        # Get or create MVP user (user_id=1)
        user = db.query(User).filter(User.id == 1).first()

        if not user:
            # Create MVP user if doesn't exist
            user = User(
                id=1,
                email="mvp@paiid.local",
                password_hash="",  # No password for MVP user (uses API token only)
                full_name="MVP User",
                role="owner",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("Created MVP user", user_id=1)

        # CRITICAL: Detach user from session to prevent connection leak
        # This is essential for SSE streams that hold user objects for extended periods
        db.expunge(user)

        logger.debug(
            "API token auth successful",
            user=format_user_for_logging(user)
        )
        return user

    # CASE 2: JWT Authentication (multi-user mode)
    if auth_mode == AuthMode.JWT:
        if not authorization:
            logger.error("JWT auth failed: Missing authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
            )

        # Extract token (already validated to start with "Bearer " in get_auth_mode)
        token = authorization.split(" ", 1)[1]

        try:
            # Decode and validate JWT
            payload = decode_token(token)

            # Verify token type
            if payload.get("type") != "access":
                logger.error(
                    "JWT auth failed: Invalid token type",
                    token_type=payload.get("type")
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type (expected access token)",
                )

            # Get user_id from payload
            user_id: int = payload.get("sub")
            if user_id is None:
                logger.error("JWT auth failed: Token missing user identifier")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing user identifier",
                )

            # Fetch user from database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error("JWT auth failed: User not found", user_id=user_id)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
                )

            # Check if user is active
            if not user.is_active:
                logger.warning(
                    "JWT auth failed: Inactive user",
                    user=format_user_for_logging(user)
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is disabled",
                )

            # CRITICAL: Detach user from session to prevent connection leak
            # This is essential for SSE streams that hold user objects for extended periods
            db.expunge(user)

            logger.debug(
                "JWT auth successful",
                user=format_user_for_logging(user)
            )
            return user

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "JWT validation error",
                error_type=type(e).__name__,
                error_msg=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

    # CASE 3: MVP Fallback (no auth header or unrecognized)
    if auth_mode == AuthMode.MVP_FALLBACK:
        # Get or create MVP user (user_id=1)
        user = db.query(User).filter(User.id == 1).first()

        if not user:
            # Create MVP user if doesn't exist
            user = User(
                id=1,
                email="mvp@paiid.local",
                password_hash="",  # No password for MVP user (uses API token only)
                full_name="MVP User",
                role="owner",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("Created MVP user for fallback auth", user_id=1)

        # CRITICAL: Detach user from session to prevent connection leak
        # This is essential for SSE streams that hold user objects for extended periods
        db.expunge(user)

        logger.debug(
            "MVP fallback auth successful",
            user=format_user_for_logging(user)
        )
        return user

    # Should never reach here
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Authentication system error",
    )


def require_api_token(authorization: str | None = Header(None, alias="Authorization", convert_underscores=False)) -> str:
    """
    Require simple API token authentication (for service endpoints)

    Use this for endpoints that should ONLY accept the simple API token,
    not JWT tokens.

    Args:
        authorization: Authorization header

    Returns:
        Valid API token string

    Raises:
        HTTPException: 401 if token invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format",
        )

    token = authorization.split(" ", 1)[1]

    if not settings.API_TOKEN:
        logger.error("API_TOKEN not configured!")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server authentication not configured",
        )

    if token != settings.API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token"
        )

    return token
