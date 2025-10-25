from ..core.jwt import (
from ..db.session import get_db
from ..models.database import ActivityLog, User, UserSession
from datetime import UTC, datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session
import logging

"""
Authentication API Routes

Handles user registration, login, logout, token refresh, and profile management.
Supports owner and beta tester registration with invite codes.
"""



    create_token_pair,
    decode_token,
    get_current_user,
    hash_password,
    verify_password,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

# Invite codes for beta testing (store these securely in production, e.g., environment variables or database)
BETA_INVITE_CODES = {"PAIID_BETA_2025", "TRADING_BETA_ACCESS"}  # Example invite code

class UserRegister(BaseModel):
    """User registration request"""

    email: EmailStr
    password: str = Field(
        ..., min_length=8, description="Password must be at least 8 characters"
    )
    full_name: str | None = None
    invite_code: str | None = Field(
        None, description="Required for beta tester registration"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password has minimum security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token response for login/refresh"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""

    refresh_token: str

class UserProfile(BaseModel):
    """User profile response"""

    id: int
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    preferences: dict

    class Config:
        from_attributes = True

@router.post(
    "/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister, request: Request, db: Session = Depends(get_db)
):
    """
    Register a new user

    **Beta Testing:**
    - Requires valid invite code for beta tester registration
    - Owner accounts must be created manually via database

    **Returns:**
    - Access token (15min expiry)
    - Refresh token (7 days expiry)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Validate invite code for beta testers
    if user_data.invite_code:
        if user_data.invite_code not in BETA_INVITE_CODES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid invite code"
            )
        role = "beta_tester"
    else:
        # Default to personal_only if no invite code
        role = "personal_only"

    # Hash password
    password_hash = hash_password(user_data.password)

    # Create user
    new_user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name or user_data.email,
        role=role,
        is_active=True,
        preferences={"risk_tolerance": 50},  # Default moderate risk
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"✅ New user registered: {new_user.email} (role: {role})")

    # Log activity
    activity = ActivityLog(
        user_id=new_user.id,
        action_type="user_register",
        resource_type="user",
        resource_id=new_user.id,
        details={"email": new_user.email, "role": role},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(activity)
    db.commit()

    # Generate tokens
    tokens = create_token_pair(
        new_user,
        db,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return tokens

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin, request: Request, db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens

    **Returns:**
    - Access token (15min expiry)
    - Refresh token (7 days expiry)

    **Errors:**
    - 401: Invalid email or password
    - 403: Account disabled
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        # Log failed attempt
        logger.warning(f"⚠️ Failed login attempt for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    logger.info(f"✅ User logged in: {user.email} (role: {user.role})")

    # Log activity
    activity = ActivityLog(
        user_id=user.id,
        action_type="user_login",
        resource_type="session",
        resource_id=user.id,
        details={"email": user.email},
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(activity)
    db.commit()

    # Generate tokens
    tokens = create_token_pair(
        user,
        db,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return tokens

@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Logout user and invalidate all sessions

    Deletes all active sessions for the current user, effectively
    invalidating all access and refresh tokens.
    """
    # Delete all user sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()

    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action_type="user_logout",
        resource_type="session",
        resource_id=current_user.id,
        details={"email": current_user.email},
        timestamp=datetime.now(UTC),
    )
    db.add(activity)
    db.commit()

    logger.info(f"✅ User logged out: {current_user.email}")

    return None  # 204 No Content

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Exchange refresh token for new access + refresh token pair

    **Process:**
    1. Validate refresh token
    2. Check session exists in database
    3. Invalidate old session
    4. Generate new token pair
    5. Store new session

    **Returns:**
    - New access token (15min expiry)
    - New refresh token (7 days expiry)
    """
    # Decode refresh token
    try:
        payload = decode_token(refresh_request.refresh_token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type (expected refresh token)",
        )

    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled"
        )

    # Verify session exists
    refresh_jti = payload.get("jti")
    session = (
        db.query(UserSession)
        .filter(
            UserSession.user_id == user_id,
            UserSession.refresh_token_jti == refresh_jti,
            UserSession.expires_at > datetime.now(UTC),
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )

    # Delete old session
    db.delete(session)
    db.commit()

    logger.info(f"✅ Token refreshed for user: {user.email}")

    # Generate new token pair
    tokens = create_token_pair(
        user,
        db,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return tokens

@router.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile

    **Requires:**
    - Valid JWT access token in Authorization header

    **Returns:**
    - User profile with email, role, preferences, etc.
    """
    return current_user
