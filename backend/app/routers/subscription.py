"""
Subscription API Endpoints

Handles subscription management, billing, and usage tracking.

Phase 2: Monetization Engine
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from ..models.subscription import Subscription, SubscriptionEvent, UsageRecord
from ..services.stripe_service import SUBSCRIPTION_TIERS, get_stripe_service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/subscription", tags=["Subscription"])


# Pydantic models for request/response

class SubscriptionResponse(BaseModel):
    """Subscription details response"""

    tier: str
    status: str
    price: float
    is_active: bool
    is_trial: bool
    current_period_start: datetime | None
    current_period_end: datetime | None
    days_until_renewal: int | None
    cancel_at_period_end: bool
    stripe_customer_id: str | None
    limits: dict[str, Any]

    class Config:
        from_attributes = True


class CreateCheckoutSessionRequest(BaseModel):
    """Request to create a checkout session"""

    tier: str
    trial_days: int | None = None


class UpdateSubscriptionRequest(BaseModel):
    """Request to update subscription tier"""

    new_tier: str


class UsageResponse(BaseModel):
    """Usage tracking response"""

    feature: str
    current_usage: int
    limit: int
    percentage_used: float
    within_limit: bool


# Dependency to get current user (placeholder - implement with JWT auth)
async def get_current_user_id(request: Request) -> int:
    """
    Get current user ID from authentication

    TODO: Replace with actual JWT authentication
    For now, using hardcoded user_id from header or default to 1
    """
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return int(user_id)
    return 1  # Default user for development


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    user_id: int = Depends(get_current_user_id),
) -> SubscriptionResponse:
    """
    Get current user's subscription details

    Returns:
        Subscription details including tier, limits, and billing info
    """
    try:
        # TODO: Query from database
        # For now, return free tier default
        stripe_service = get_stripe_service()

        subscription_data = {
            "tier": "free",
            "status": "active",
            "price": 0,
            "is_active": True,
            "is_trial": False,
            "current_period_start": None,
            "current_period_end": None,
            "days_until_renewal": None,
            "cancel_at_period_end": False,
            "stripe_customer_id": None,
            "limits": stripe_service.get_tier_limits("free"),
        }

        return SubscriptionResponse(**subscription_data)

    except Exception as e:
        logger.error(f"Failed to get subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get subscription: {e!s}") from e


@router.get("/tiers")
async def get_subscription_tiers() -> dict[str, Any]:
    """
    Get all available subscription tiers and their features

    Returns:
        Dictionary of tiers with pricing and limits
    """
    try:
        return {
            "tiers": SUBSCRIPTION_TIERS,
            "currency": "USD",
        }
    except Exception as e:
        logger.error(f"Failed to get tiers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tiers: {e!s}") from e


@router.post("/checkout-session")
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Create a Stripe checkout session for subscription

    Args:
        request: Checkout session request with tier and trial info

    Returns:
        Checkout session URL
    """
    try:
        stripe_service = get_stripe_service()

        if not stripe_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Payment processing is not configured",
            )

        # TODO: Get or create Stripe customer for user
        # For now, create a new customer
        customer = await stripe_service.create_customer(
            email=f"user{user_id}@example.com",  # TODO: Get from user model
            name=f"User {user_id}",
            metadata={"user_id": str(user_id)},
        )

        # Create checkout session
        session = await stripe_service.create_checkout_session(
            customer_id=customer.id,
            tier=request.tier,
            success_url=f"{request.success_url}?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=request.cancel_url,
            trial_days=request.trial_days,
        )

        return {
            "session_id": session.id,
            "url": session.url,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create checkout session: {e!s}",
        ) from e


@router.post("/billing-portal")
async def create_billing_portal_session(
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Create a Stripe billing portal session for subscription management

    Returns:
        Billing portal URL
    """
    try:
        stripe_service = get_stripe_service()

        if not stripe_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Payment processing is not configured",
            )

        # TODO: Get Stripe customer ID from database
        stripe_customer_id = "cus_placeholder"  # Placeholder

        # Create billing portal session
        session = await stripe_service.create_billing_portal_session(
            customer_id=stripe_customer_id,
            return_url="https://paiid-frontend.onrender.com/settings",
        )

        return {
            "url": session.url,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing portal session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create billing portal session: {e!s}",
        ) from e


@router.post("/upgrade")
async def upgrade_subscription(
    request: UpdateSubscriptionRequest,
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Upgrade or downgrade subscription tier

    Args:
        request: Update request with new tier

    Returns:
        Updated subscription details
    """
    try:
        stripe_service = get_stripe_service()

        if not stripe_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Payment processing is not configured",
            )

        # TODO: Get subscription from database
        stripe_subscription_id = "sub_placeholder"  # Placeholder

        # Update subscription
        subscription = await stripe_service.update_subscription(
            subscription_id=stripe_subscription_id,
            new_tier=request.new_tier,
        )

        # TODO: Update database with new tier

        return {
            "success": True,
            "new_tier": request.new_tier,
            "message": f"Successfully upgraded to {request.new_tier}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade subscription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upgrade subscription: {e!s}",
        ) from e


@router.post("/cancel")
async def cancel_subscription(
    immediate: bool = Query(False, description="Cancel immediately vs at period end"),
    user_id: int = Depends(get_current_user_id),
) -> dict[str, Any]:
    """
    Cancel subscription

    Args:
        immediate: Cancel immediately (True) or at end of billing period (False)

    Returns:
        Cancellation confirmation
    """
    try:
        stripe_service = get_stripe_service()

        if not stripe_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Payment processing is not configured",
            )

        # TODO: Get subscription from database
        stripe_subscription_id = "sub_placeholder"  # Placeholder

        # Cancel subscription
        subscription = await stripe_service.cancel_subscription(
            subscription_id=stripe_subscription_id,
            immediate=immediate,
        )

        # TODO: Update database

        return {
            "success": True,
            "immediate": immediate,
            "message": "Subscription cancelled"
            if immediate
            else "Subscription will cancel at end of billing period",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel subscription: {e!s}",
        ) from e


@router.get("/usage/{feature}")
async def get_usage(
    feature: str,
    user_id: int = Depends(get_current_user_id),
) -> UsageResponse:
    """
    Get current usage for a specific feature

    Args:
        feature: Feature name (ml_prediction, backtest, etc.)

    Returns:
        Usage statistics and limit information
    """
    try:
        stripe_service = get_stripe_service()

        # TODO: Get subscription tier from database
        tier = "free"  # Placeholder

        # TODO: Get actual usage from database
        current_usage = 0  # Placeholder

        limits = stripe_service.get_tier_limits(tier)

        # Map feature to limit key
        feature_limit_map = {
            "ml_prediction": "ml_predictions_per_month",
            "backtest": "backtests_per_month",
            "strategy": "strategies",
            "news": "news_articles_per_day",
        }

        limit_key = feature_limit_map.get(feature)
        if not limit_key:
            raise HTTPException(status_code=404, detail=f"Unknown feature: {feature}")

        limit = limits.get(limit_key, 0)

        # Calculate percentage used
        if limit == -1:
            percentage_used = 0.0  # Unlimited
            within_limit = True
        else:
            percentage_used = (current_usage / limit * 100) if limit > 0 else 0.0
            within_limit = current_usage < limit

        return UsageResponse(
            feature=feature,
            current_usage=current_usage,
            limit=limit,
            percentage_used=percentage_used,
            within_limit=within_limit,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get usage: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get usage: {e!s}") from e


@router.post("/webhook")
async def handle_stripe_webhook(request: Request) -> dict[str, Any]:
    """
    Handle Stripe webhook events (subscriptions, payments, etc.)

    This endpoint receives and processes Stripe webhooks for:
    - Subscription created/updated/cancelled
    - Payment succeeded/failed
    - Customer created/updated

    Note: Must be registered in Stripe dashboard
    """
    try:
        stripe_service = get_stripe_service()

        # Get raw body and signature
        payload = await request.body()
        signature = request.headers.get("Stripe-Signature")

        if not signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")

        # Verify webhook signature
        event = stripe_service.verify_webhook_signature(payload, signature)

        logger.info(f"📨 Stripe webhook received: {event['type']}")

        # Handle different event types
        event_type = event["type"]
        event_data = event["data"]["object"]

        if event_type == "customer.subscription.created":
            # TODO: Create subscription in database
            logger.info(f"New subscription created: {event_data['id']}")

        elif event_type == "customer.subscription.updated":
            # TODO: Update subscription in database
            logger.info(f"Subscription updated: {event_data['id']}")

        elif event_type == "customer.subscription.deleted":
            # TODO: Mark subscription as cancelled in database
            logger.info(f"Subscription cancelled: {event_data['id']}")

        elif event_type == "invoice.payment_succeeded":
            # TODO: Record successful payment in database
            logger.info(f"Payment succeeded: {event_data['id']}")

        elif event_type == "invoice.payment_failed":
            # TODO: Handle failed payment (notify user, update status)
            logger.warning(f"Payment failed: {event_data['id']}")

        else:
            logger.info(f"Unhandled webhook event: {event_type}")

        return {"success": True, "event_type": event_type}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {e!s}",
        ) from e
