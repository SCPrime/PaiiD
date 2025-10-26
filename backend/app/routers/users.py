"""
User Preferences API Routes
Endpoints for managing user preferences including risk tolerance

SECURITY: Never logs full user objects or sensitive data
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from ..core.logging_utils import get_secure_logger
from ..core.unified_auth import get_current_user_unified
from ..db.session import get_db
from ..models.database import User
from ..services.user_management_service import get_user_management_service


logger = get_secure_logger(__name__)

router = APIRouter()


class UserPreferencesResponse(BaseModel):
    """Response model for user preferences"""

    risk_tolerance: int | None = Field(
        None, ge=0, le=100, description="Risk tolerance (0-100)"
    )
    default_position_size: float | None = None
    watchlist: list | None = None
    notifications_enabled: bool | None = None
    preferences: dict[str, Any]  # Full preferences object


class UserPreferencesUpdate(BaseModel):
    """Request model for updating user preferences"""

    risk_tolerance: int | None = Field(
        None, ge=0, le=100, description="Risk tolerance (0-100)"
    )
    default_position_size: float | None = Field(
        None, gt=0, description="Default position size in dollars"
    )
    watchlist: list | None = None
    notifications_enabled: bool | None = None

    @field_validator("risk_tolerance")
    @classmethod
    def validate_risk_tolerance(cls, v: int | None) -> int | None:
        if v is not None and (v < 0 or v > 100):
            raise ValueError("risk_tolerance must be between 0 and 100")
        return v


@router.get("/users/preferences")
def get_user_preferences(
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db),
) -> UserPreferencesResponse:
    """
    Get user preferences including risk tolerance

    Returns current user preferences or default values if not set.
    """
    try:
        user_service = get_user_management_service(db)
        prefs = user_service.get_user_preferences(current_user.id)

        return UserPreferencesResponse(
            risk_tolerance=prefs.risk_tolerance,
            default_position_size=prefs.default_position_size,
            watchlist=prefs.watchlist,
            notifications_enabled=prefs.notifications_enabled,
            preferences=prefs.preferences,
        )

    except ValueError as e:
        logger.error("User not found", user_id=current_user.id, error_msg=str(e))
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to fetch user preferences",
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch user preferences: {e!s}"
        ) from e


@router.patch("/users/preferences")
def update_user_preferences(
    updates: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db),
) -> UserPreferencesResponse:
    """
    Update user preferences

    Updates only the fields provided in the request body.
    Validates risk_tolerance is between 0-100.
    """
    try:
        user_service = get_user_management_service(db)
        update_data = updates.model_dump(exclude_unset=True)

        prefs = user_service.update_user_preferences(current_user.id, update_data)

        return UserPreferencesResponse(
            risk_tolerance=prefs.risk_tolerance,
            default_position_size=prefs.default_position_size,
            watchlist=prefs.watchlist,
            notifications_enabled=prefs.notifications_enabled,
            preferences=prefs.preferences,
        )

    except ValueError as e:
        logger.error("Invalid update request", user_id=current_user.id, error_msg=str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to update user preferences",
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to update user preferences: {e!s}"
        ) from e


@router.get("/users/risk-limits")
def get_user_risk_limits(
    current_user: User = Depends(get_current_user_unified),
    db: Session = Depends(get_db),
):
    """
    Get calculated risk limits based on user's risk tolerance

    Returns position sizing limits and maximum concurrent positions.
    """
    try:
        user_service = get_user_management_service(db)
        limits = user_service.get_user_risk_limits(current_user.id)
        return limits

    except ValueError as e:
        logger.error("User not found", user_id=current_user.id, error_msg=str(e))
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to calculate risk limits",
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate risk limits: {e!s}"
        ) from e
