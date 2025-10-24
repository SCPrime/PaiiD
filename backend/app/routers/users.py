"""
User Preferences API Routes
Endpoints for managing user preferences including risk tolerance
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from ..core.dependencies import require_user
from ..db.session import get_db
from ..models.database import User


logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(require_user)])


class UserPreferencesResponse(BaseModel):
    """Response model for user preferences"""

    risk_tolerance: int | None = Field(None, ge=0, le=100, description="Risk tolerance (0-100)")
    default_position_size: float | None = None
    watchlist: list | None = None
    notifications_enabled: bool | None = None
    preferences: dict[str, Any]  # Full preferences object


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences"""

    risk_tolerance: int | None = Field(None, ge=0, le=100, description="Risk tolerance (0-100)")
    default_position_size: float | None = Field(
        None, gt=0, description="Default position size in dollars"
    )
    watchlist: list | None = None
    notifications_enabled: bool | None = None

    @validator("risk_tolerance")
    def validate_risk_tolerance(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("risk_tolerance must be between 0 and 100")
        return v


@router.get("/users/preferences")
def get_user_preferences(
    db: Session = Depends(get_db)
) -> UserPreferencesResponse:
    """
    Get user preferences including risk tolerance

    Returns current user preferences or default values if not set.
    """
    try:
        # For now, use a default user (user_id=1) until auth is fully implemented
        # TODO: Replace placeholder with current_user.id once frontend wiring is complete
        user = db.query(User).filter(User.id == 1).first()

        if not user:
            # Create default user if doesn't exist
            user = User(
                id=1,
                email="default@paiid.com",
                alpaca_account_id=None,
                preferences={"risk_tolerance": 50},  # Default to moderate risk
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info("✅ Created default user with preferences")

        preferences = user.preferences or {}

        return UserPreferencesResponse(
            risk_tolerance=preferences.get("risk_tolerance", 50),
            default_position_size=preferences.get("default_position_size"),
            watchlist=preferences.get("watchlist", []),
            notifications_enabled=preferences.get("notifications_enabled", True),
            preferences=preferences,
        )

    except Exception as e:
        logger.error(f"❌ Failed to fetch user preferences: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user preferences: {e!s}")


@router.patch("/users/preferences")
def update_user_preferences(
    updates: UserPreferencesUpdate, db: Session = Depends(get_db)
) -> UserPreferencesResponse:
    """
    Update user preferences

    Updates only the fields provided in the request body.
    Validates risk_tolerance is between 0-100.
    """
    try:
        # Get or create default user
        user = db.query(User).filter(User.id == 1).first()

        if not user:
            user = User(id=1, email="default@paiid.com", alpaca_account_id=None, preferences={})
            db.add(user)
            db.commit()
            db.refresh(user)

        # Get current preferences
        preferences = user.preferences or {}

        # Update only provided fields
        update_data = updates.dict(exclude_unset=True)

        # Apply backend safeguards for risk_tolerance
        if "risk_tolerance" in update_data:
            risk_value = update_data["risk_tolerance"]

            # Safeguard: Warn if ultra-aggressive (>90)
            if risk_value > 90:
                logger.warning(f"⚠️ User setting very high risk tolerance: {risk_value}")

            # Safeguard: Ensure value is in valid range
            if risk_value < 0 or risk_value > 100:
                raise HTTPException(
                    status_code=400, detail="risk_tolerance must be between 0 and 100"
                )

            preferences["risk_tolerance"] = risk_value

        # Update other preferences
        for key, value in update_data.items():
            if key != "risk_tolerance":
                preferences[key] = value

        # Save to database
        user.preferences = preferences
        db.commit()
        db.refresh(user)

        logger.info(f"✅ Updated user preferences: {update_data}")

        return UserPreferencesResponse(
            risk_tolerance=preferences.get("risk_tolerance", 50),
            default_position_size=preferences.get("default_position_size"),
            watchlist=preferences.get("watchlist", []),
            notifications_enabled=preferences.get("notifications_enabled", True),
            preferences=preferences,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update user preferences: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to update user preferences: {e!s}")


def get_risk_limits(risk_tolerance: int) -> dict[str, Any]:
    """
    Calculate risk-based trading limits

    Args:
        risk_tolerance: User's risk tolerance (0-100)

    Returns:
        Dictionary with max_position_size_percent, max_positions, and risk_category
    """
    if risk_tolerance <= 33:
        # Conservative
        return {
            "risk_category": "Conservative",
            "max_position_size_percent": 5.0,  # Max 5% per trade
            "max_positions": 3,  # Max 3 concurrent positions
            "description": "Lower risk, smaller position sizes",
        }
    elif risk_tolerance <= 66:
        # Moderate
        return {
            "risk_category": "Moderate",
            "max_position_size_percent": 10.0,  # Max 10% per trade
            "max_positions": 5,  # Max 5 concurrent positions
            "description": "Balanced risk and reward",
        }
    else:
        # Aggressive
        return {
            "risk_category": "Aggressive",
            "max_position_size_percent": 20.0,  # Max 20% per trade
            "max_positions": 10,  # Max 10 concurrent positions
            "description": "Higher risk, larger position sizes",
        }


@router.get("/users/risk-limits")
def get_user_risk_limits(db: Session = Depends(get_db)):
    """
    Get calculated risk limits based on user's risk tolerance

    Returns position sizing limits and maximum concurrent positions.
    """
    try:
        user = db.query(User).filter(User.id == 1).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        preferences = user.preferences or {}
        risk_tolerance = preferences.get("risk_tolerance", 50)

        limits = get_risk_limits(risk_tolerance)

        return {"risk_tolerance": risk_tolerance, **limits}

    except Exception as e:
        logger.error(f"❌ Failed to calculate risk limits: {e!s}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate risk limits: {e!s}")
