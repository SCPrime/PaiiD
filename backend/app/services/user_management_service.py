"""
User Management Service - Business logic for user preferences and settings

This service handles user preference management, risk tolerance calculations,
and user-specific trading limits.
"""

from typing import Any

from sqlalchemy.orm import Session

from ..core.logging_utils import format_user_for_logging, get_secure_logger
from ..models.database import User


logger = get_secure_logger(__name__)


class UserPreferences:
    """User preferences data class"""

    def __init__(
        self,
        risk_tolerance: int = 50,
        default_position_size: float | None = None,
        watchlist: list | None = None,
        notifications_enabled: bool = True,
        preferences: dict[str, Any] | None = None,
    ):
        self.risk_tolerance = risk_tolerance
        self.default_position_size = default_position_size
        self.watchlist = watchlist or []
        self.notifications_enabled = notifications_enabled
        self.preferences = preferences or {}

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "risk_tolerance": self.risk_tolerance,
            "default_position_size": self.default_position_size,
            "watchlist": self.watchlist,
            "notifications_enabled": self.notifications_enabled,
            "preferences": self.preferences,
        }


class RiskLimits:
    """Risk-based trading limits data class"""

    def __init__(
        self,
        risk_category: str,
        max_position_size_percent: float,
        max_positions: int,
        description: str,
    ):
        self.risk_category = risk_category
        self.max_position_size_percent = max_position_size_percent
        self.max_positions = max_positions
        self.description = description

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "risk_category": self.risk_category,
            "max_position_size_percent": self.max_position_size_percent,
            "max_positions": self.max_positions,
            "description": self.description,
        }


class UserManagementService:
    """Service for managing user preferences and settings"""

    def __init__(self, db: Session):
        """
        Initialize user management service

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_user_preferences(self, user_id: int) -> UserPreferences:
        """
        Get user preferences including risk tolerance

        Args:
            user_id: User ID from authenticated session

        Returns:
            UserPreferences object with current settings

        Raises:
            ValueError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.error("User not found in database", user_id=user_id)
            raise ValueError("User not found")

        preferences = user.preferences or {}

        logger.debug("Retrieved user preferences", user=format_user_for_logging(user))

        return UserPreferences(
            risk_tolerance=preferences.get("risk_tolerance", 50),
            default_position_size=preferences.get("default_position_size"),
            watchlist=preferences.get("watchlist", []),
            notifications_enabled=preferences.get("notifications_enabled", True),
            preferences=preferences,
        )

    def update_user_preferences(
        self, user_id: int, updates: dict[str, Any]
    ) -> UserPreferences:
        """
        Update user preferences

        Args:
            user_id: User ID from authenticated session
            updates: Dictionary of fields to update

        Returns:
            Updated UserPreferences object

        Raises:
            ValueError: If user not found or invalid data provided
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.error("User not found in database", user_id=user_id)
            raise ValueError("User not found")

        # Get current preferences
        preferences = user.preferences or {}

        # Validate and apply risk_tolerance if provided
        if "risk_tolerance" in updates:
            risk_value = updates["risk_tolerance"]

            # Safeguard: Ensure value is in valid range
            if risk_value < 0 or risk_value > 100:
                raise ValueError("risk_tolerance must be between 0 and 100")

            # Safeguard: Warn if ultra-aggressive (>90)
            if risk_value > 90:
                logger.warning(
                    "User setting very high risk tolerance",
                    user=format_user_for_logging(user),
                    risk_tolerance=risk_value,
                )

            preferences["risk_tolerance"] = risk_value

        # Update other preferences
        for key, value in updates.items():
            if key != "risk_tolerance":
                preferences[key] = value

        # Save to database
        user.preferences = preferences
        self.db.commit()
        self.db.refresh(user)

        logger.info(
            "Updated user preferences",
            user=format_user_for_logging(user),
            updated_fields=list(updates.keys()),
        )

        return UserPreferences(
            risk_tolerance=preferences.get("risk_tolerance", 50),
            default_position_size=preferences.get("default_position_size"),
            watchlist=preferences.get("watchlist", []),
            notifications_enabled=preferences.get("notifications_enabled", True),
            preferences=preferences,
        )

    def calculate_risk_limits(self, risk_tolerance: int) -> RiskLimits:
        """
        Calculate risk-based trading limits

        Args:
            risk_tolerance: User's risk tolerance (0-100)

        Returns:
            RiskLimits object with calculated limits
        """
        if risk_tolerance <= 33:
            # Conservative
            return RiskLimits(
                risk_category="Conservative",
                max_position_size_percent=5.0,  # Max 5% per trade
                max_positions=3,  # Max 3 concurrent positions
                description="Lower risk, smaller position sizes",
            )
        elif risk_tolerance <= 66:
            # Moderate
            return RiskLimits(
                risk_category="Moderate",
                max_position_size_percent=10.0,  # Max 10% per trade
                max_positions=5,  # Max 5 concurrent positions
                description="Balanced risk and reward",
            )
        else:
            # Aggressive
            return RiskLimits(
                risk_category="Aggressive",
                max_position_size_percent=20.0,  # Max 20% per trade
                max_positions=10,  # Max 10 concurrent positions
                description="Higher risk, larger position sizes",
            )

    def get_user_risk_limits(self, user_id: int) -> dict:
        """
        Get calculated risk limits based on user's risk tolerance

        Args:
            user_id: User ID from authenticated session

        Returns:
            Dictionary with risk tolerance and calculated limits

        Raises:
            ValueError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            logger.error("User not found in database", user_id=user_id)
            raise ValueError("User not found")

        preferences = user.preferences or {}
        risk_tolerance = preferences.get("risk_tolerance", 50)

        limits = self.calculate_risk_limits(risk_tolerance)

        logger.debug(
            "Calculated risk limits",
            user=format_user_for_logging(user),
            risk_tolerance=risk_tolerance,
            risk_category=limits.risk_category,
        )

        return {"risk_tolerance": risk_tolerance, **limits.to_dict()}


def get_user_management_service(db: Session) -> UserManagementService:
    """
    Factory function to create UserManagementService

    Args:
        db: SQLAlchemy database session

    Returns:
        UserManagementService instance
    """
    return UserManagementService(db)
