"""
JWT Token Utilities

Provides secure JWT token creation, validation, and refresh functionality
for multi-user authentication system.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.database import User, UserSession
from .config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Bcrypt password hash
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hash to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Payload data to encode (should include user_id, role)
        expires_delta: Custom expiration time (default: 15 minutes)

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard JWT claims
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),  # Unique token ID for tracking
            "type": "access",
        }
    )

    # Encode token
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict[str, Any]) -> str:
    """
    Create a JWT refresh token (longer expiration)

    Args:
        data: Payload data to encode (should include user_id)

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()

    # Set expiration
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # Add standard JWT claims
    to_encode.update(
        {"exp": expire, "iat": datetime.utcnow(), "jti": str(uuid.uuid4()), "type": "refresh"}
    )

    # Encode token
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e!s}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency to get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token from request
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: If token invalid or user not found/inactive
    """
    token = credentials.credentials

    # Decode token
    payload = decode_token(token)

    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type (expected access token)",
        )

    # Get user_id from payload
    user_id_claim = payload.get("sub")
    if user_id_claim is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing user identifier"
        )

    try:
        user_id = int(user_id_claim)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing valid user identifier",
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled"
        )

    # Verify session still exists (optional: check token JTI in user_sessions)
    jti = payload.get("jti")
    if jti:
        session = (
            db.query(UserSession)
            .filter(
                UserSession.user_id == user_id,
                UserSession.access_token_jti == jti,
                UserSession.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid"
            )

        # Update last activity
        session.last_activity_at = datetime.utcnow()
        db.commit()

    return user


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require owner role

    Args:
        current_user: Current authenticated user

    Returns:
        User object if owner role

    Raises:
        HTTPException: If user is not owner
    """
    if current_user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner access required")
    return current_user


def create_token_pair(
    user: User, db: Session, ip_address: str | None = None, user_agent: str | None = None
) -> dict[str, str]:
    """
    Create access + refresh token pair and store session

    Args:
        user: User to create tokens for
        db: Database session
        ip_address: Client IP address (for audit)
        user_agent: Client user agent (for audit)

    Returns:
        Dictionary with access_token, refresh_token, token_type
    """
    # Create token payloads
    access_payload = {"sub": str(user.id), "role": user.role, "email": user.email}
    refresh_payload = {"sub": str(user.id)}

    # Generate tokens
    access_token = create_access_token(access_payload)
    refresh_token = create_refresh_token(refresh_payload)

    # Decode to get JTIs
    access_decoded = decode_token(access_token)
    refresh_decoded = decode_token(refresh_token)

    # Store session in database
    session = UserSession(
        user_id=user.id,
        access_token_jti=access_decoded["jti"],
        refresh_token_jti=refresh_decoded["jti"],
        expires_at=datetime.fromtimestamp(refresh_decoded["exp"]),
        last_activity_at=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)

    # Update user's last login
    user.last_login_at = datetime.utcnow()

    db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
