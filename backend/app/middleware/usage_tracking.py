"""
Usage Tracking Middleware

Automatically tracks feature usage for subscription metering.

Phase 2: Monetization Engine - Usage Metering
"""

import logging
from datetime import datetime
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


# Feature tracking configuration
TRACKED_ENDPOINTS = {
    "/api/ml/market-regime": "ml_prediction",
    "/api/ml/recommend-strategy": "ml_prediction",
    "/api/ml/detect-patterns": "ml_prediction",
    "/api/ml/optimize-portfolio": "ml_prediction",
    "/api/ml/backtest-patterns": "backtest",
    "/api/ml/train-regime-detector": "ml_training",
    "/api/ml/train-strategy-selector": "ml_training",
    "/api/sentiment/analyze": "ml_prediction",
    "/api/news": "news_fetch",
}


class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track feature usage for subscription metering

    Tracks:
    - ML predictions
    - Backtests
    - Model training
    - News fetches
    - Strategy operations
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track usage if applicable

        Args:
            request: FastAPI request
            call_next: Next middleware in chain

        Returns:
            Response
        """
        # Get response first
        response = await call_next(request)

        # Only track successful requests (2xx status codes)
        if 200 <= response.status_code < 300:
            await self.track_usage(request, response)

        return response

    async def track_usage(self, request: Request, response: Response) -> None:
        """
        Track usage for metered features

        Args:
            request: FastAPI request
            response: FastAPI response
        """
        try:
            # Check if endpoint should be tracked
            endpoint = request.url.path
            feature = TRACKED_ENDPOINTS.get(endpoint)

            if not feature:
                return  # Not a tracked endpoint

            # Get user ID (TODO: Extract from JWT token)
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                user_id = 1  # Default for development

            # Get current billing period
            now = datetime.utcnow()
            billing_period_start = datetime(now.year, now.month, 1)

            # Calculate period end (first day of next month)
            if now.month == 12:
                billing_period_end = datetime(now.year + 1, 1, 1)
            else:
                billing_period_end = datetime(now.year, now.month + 1, 1)

            # TODO: Record usage in database
            usage_record = {
                "user_id": user_id,
                "feature": feature,
                "quantity": 1,
                "timestamp": now,
                "billing_period_start": billing_period_start,
                "billing_period_end": billing_period_end,
                "endpoint": endpoint,
                "method": request.method,
            }

            logger.info(f"📊 Usage tracked: {feature} for user {user_id}")

            # TODO: Check if user has exceeded limits
            # If exceeded, return 429 Too Many Requests in future requests

        except Exception as e:
            # Don't fail request if usage tracking fails
            logger.warning(f"Failed to track usage: {e}")


async def check_usage_limit(
    user_id: int,
    feature: str,
    tier: str,
) -> tuple[bool, int, int]:
    """
    Check if user has exceeded usage limit for a feature

    Args:
        user_id: User ID
        feature: Feature name (ml_prediction, backtest, etc.)
        tier: Subscription tier (free, pro, premium)

    Returns:
        (within_limit, current_usage, limit)
    """
    try:
        from ..models.subscription import check_feature_limit
        from datetime import datetime

        # Get current billing period start
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        # TODO: Get subscription_id from user
        subscription_id = 1  # Placeholder

        # Check limit
        within_limit, usage, limit = check_feature_limit(
            subscription_id=subscription_id,
            feature=feature,
            month_start=month_start,
            tier=tier,
        )

        return within_limit, usage, limit

    except Exception as e:
        logger.error(f"Failed to check usage limit: {e}")
        # On error, allow request to proceed
        return True, 0, -1


def require_feature_access(feature: str):
    """
    Decorator to require feature access based on subscription tier

    Usage:
        @router.get("/api/ml/advanced-feature")
        @require_feature_access("advanced_ml")
        async def advanced_feature():
            ...
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            from fastapi import HTTPException

            # TODO: Get user subscription tier
            tier = "free"  # Placeholder

            # Check if feature is available for tier
            from ..services.stripe_service import get_stripe_service

            stripe_service = get_stripe_service()
            limits = stripe_service.get_tier_limits(tier)

            # Check boolean features
            if feature in limits:
                if not limits[feature]:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Feature '{feature}' not available in {tier} tier. Please upgrade.",
                    )

            # Execute function
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def increment_usage(user_id: int, feature: str, quantity: int = 1) -> None:
    """
    Manually increment usage for a feature

    Args:
        user_id: User ID
        feature: Feature name
        quantity: Usage quantity (default: 1)
    """
    try:
        from datetime import datetime

        now = datetime.utcnow()
        billing_period_start = datetime(now.year, now.month, 1)

        if now.month == 12:
            billing_period_end = datetime(now.year + 1, 1, 1)
        else:
            billing_period_end = datetime(now.year, now.month + 1, 1)

        # TODO: Record in database
        logger.info(f"📊 Manual usage increment: {feature} +{quantity} for user {user_id}")

    except Exception as e:
        logger.warning(f"Failed to increment usage: {e}")


def get_usage_summary(user_id: int, tier: str) -> dict:
    """
    Get usage summary for all features

    Args:
        user_id: User ID
        tier: Subscription tier

    Returns:
        Dictionary with usage for each feature
    """
    try:
        from ..services.stripe_service import get_stripe_service
        from datetime import datetime

        stripe_service = get_stripe_service()
        limits = stripe_service.get_tier_limits(tier)

        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)

        # TODO: Get actual usage from database
        # For now, return placeholder data
        summary = {
            "tier": tier,
            "billing_period_start": month_start.isoformat(),
            "usage": {
                "ml_predictions": {
                    "used": 0,  # TODO: Get from DB
                    "limit": limits.get("ml_predictions_per_month", 0),
                    "percentage": 0.0,
                },
                "backtests": {
                    "used": 0,  # TODO: Get from DB
                    "limit": limits.get("backtests_per_month", 0),
                    "percentage": 0.0,
                },
                "strategies": {
                    "used": 0,  # TODO: Get from DB
                    "limit": limits.get("strategies", 0),
                    "percentage": 0.0,
                },
            },
        }

        return summary

    except Exception as e:
        logger.error(f"Failed to get usage summary: {e}")
        return {}


# Export middleware and utilities
__all__ = [
    "UsageTrackingMiddleware",
    "check_usage_limit",
    "require_feature_access",
    "increment_usage",
    "get_usage_summary",
]
