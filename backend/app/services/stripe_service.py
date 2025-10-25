"""
Stripe Service for Subscription Management

Handles subscription lifecycle, usage metering, and payment processing.

Phase 2: Monetization Engine
"""

import logging
import os
from datetime import datetime
from typing import Any

import stripe


logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


# Subscription Tiers Configuration
SUBSCRIPTION_TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "stripe_price_id": None,
        "limits": {
            "ml_predictions_per_month": 50,
            "backtests_per_month": 5,
            "strategies": 2,
            "watchlist_size": 10,
            "news_articles_per_day": 20,
            "portfolio_optimization": False,
            "advanced_ml": False,
            "priority_support": False,
        },
    },
    "pro": {
        "name": "Pro",
        "price": 29.99,
        "stripe_price_id": os.getenv("STRIPE_PRO_PRICE_ID"),
        "limits": {
            "ml_predictions_per_month": 500,
            "backtests_per_month": 50,
            "strategies": 10,
            "watchlist_size": 50,
            "news_articles_per_day": 200,
            "portfolio_optimization": True,
            "advanced_ml": True,
            "priority_support": False,
        },
    },
    "premium": {
        "name": "Premium",
        "price": 99.99,
        "stripe_price_id": os.getenv("STRIPE_PREMIUM_PRICE_ID"),
        "limits": {
            "ml_predictions_per_month": -1,  # Unlimited
            "backtests_per_month": -1,  # Unlimited
            "strategies": -1,  # Unlimited
            "watchlist_size": -1,  # Unlimited
            "news_articles_per_day": -1,  # Unlimited
            "portfolio_optimization": True,
            "advanced_ml": True,
            "priority_support": True,
        },
    },
}


class StripeService:
    """Stripe integration for subscription management"""

    def __init__(self):
        self.api_key = stripe.api_key
        if not self.api_key:
            logger.warning("⚠️ Stripe API key not configured. Subscription features disabled.")

    def is_configured(self) -> bool:
        """Check if Stripe is properly configured"""
        return bool(self.api_key)

    async def create_customer(
        self,
        email: str,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe customer

        Args:
            email: Customer email
            name: Customer name
            metadata: Additional metadata (user_id, etc.)

        Returns:
            Stripe customer object
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {},
            )
            logger.info(f"✅ Stripe customer created: {customer.id}")
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    async def create_subscription(
        self,
        customer_id: str,
        tier: str = "pro",
        trial_days: int | None = None,
    ) -> dict[str, Any]:
        """
        Create a subscription for a customer

        Args:
            customer_id: Stripe customer ID
            tier: Subscription tier (free, pro, premium)
            trial_days: Number of trial days (optional)

        Returns:
            Stripe subscription object
        """
        try:
            tier_config = SUBSCRIPTION_TIERS.get(tier)
            if not tier_config:
                raise ValueError(f"Invalid tier: {tier}")

            if tier == "free":
                # Free tier doesn't need Stripe subscription
                return {
                    "id": None,
                    "status": "active",
                    "tier": "free",
                    "current_period_end": None,
                }

            price_id = tier_config["stripe_price_id"]
            if not price_id:
                raise ValueError(f"Stripe price ID not configured for tier: {tier}")

            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                metadata={"tier": tier},
            )

            logger.info(f"✅ Subscription created: {subscription.id} (tier: {tier})")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription: {e}")
            raise

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediate: bool = False,
    ) -> dict[str, Any]:
        """
        Cancel a subscription

        Args:
            subscription_id: Stripe subscription ID
            immediate: Cancel immediately vs at period end

        Returns:
            Updated subscription object
        """
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )

            logger.info(f"✅ Subscription cancelled: {subscription_id}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    async def update_subscription(
        self,
        subscription_id: str,
        new_tier: str,
    ) -> dict[str, Any]:
        """
        Upgrade or downgrade a subscription

        Args:
            subscription_id: Stripe subscription ID
            new_tier: New tier (pro, premium)

        Returns:
            Updated subscription object
        """
        try:
            tier_config = SUBSCRIPTION_TIERS.get(new_tier)
            if not tier_config or new_tier == "free":
                raise ValueError(f"Invalid tier for upgrade: {new_tier}")

            price_id = tier_config["stripe_price_id"]
            if not price_id:
                raise ValueError(f"Stripe price ID not configured for tier: {new_tier}")

            # Get current subscription
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Update subscription item
            stripe.Subscription.modify(
                subscription_id,
                items=[
                    {
                        "id": subscription["items"]["data"][0].id,
                        "price": price_id,
                    }
                ],
                metadata={"tier": new_tier},
                proration_behavior="create_prorations",  # Charge/credit immediately
            )

            logger.info(f"✅ Subscription updated: {subscription_id} -> {new_tier}")
            return subscription

        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription: {e}")
            raise

    async def create_checkout_session(
        self,
        customer_id: str,
        tier: str,
        success_url: str,
        cancel_url: str,
        trial_days: int | None = None,
    ) -> dict[str, Any]:
        """
        Create a Stripe Checkout session for subscription

        Args:
            customer_id: Stripe customer ID
            tier: Subscription tier
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            trial_days: Number of trial days

        Returns:
            Checkout session object with URL
        """
        try:
            tier_config = SUBSCRIPTION_TIERS.get(tier)
            if not tier_config or tier == "free":
                raise ValueError(f"Invalid tier for checkout: {tier}")

            price_id = tier_config["stripe_price_id"]
            if not price_id:
                raise ValueError(f"Stripe price ID not configured for tier: {tier}")

            session_params = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {"tier": tier},
            }

            if trial_days:
                session_params["subscription_data"] = {
                    "trial_period_days": trial_days,
                }

            session = stripe.checkout.Session.create(**session_params)

            logger.info(f"✅ Checkout session created: {session.id}")
            return session

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> dict[str, Any]:
        """
        Create a billing portal session for customer to manage subscription

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after managing subscription

        Returns:
            Billing portal session with URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )

            logger.info(f"✅ Billing portal session created for: {customer_id}")
            return session

        except stripe.error.StripeError as e:
            logger.error(f"Failed to create billing portal session: {e}")
            raise

    async def record_usage(
        self,
        subscription_id: str,
        quantity: int,
        timestamp: int | None = None,
    ) -> dict[str, Any]:
        """
        Record usage for metered billing (future feature)

        Args:
            subscription_id: Stripe subscription ID
            quantity: Usage quantity
            timestamp: Unix timestamp (default: now)

        Returns:
            Usage record object
        """
        try:
            # Get subscription item
            subscription = stripe.Subscription.retrieve(subscription_id)
            subscription_item_id = subscription["items"]["data"][0].id

            # Record usage
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now().timestamp()),
                action="increment",  # or "set"
            )

            logger.info(f"✅ Usage recorded: {quantity} for {subscription_id}")
            return usage_record

        except stripe.error.StripeError as e:
            logger.error(f"Failed to record usage: {e}")
            raise

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str,
    ) -> dict[str, Any]:
        """
        Verify Stripe webhook signature

        Args:
            payload: Raw request body
            signature: Stripe-Signature header

        Returns:
            Verified event object
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                STRIPE_WEBHOOK_SECRET,
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            raise

    def get_tier_limits(self, tier: str) -> dict[str, Any]:
        """
        Get limits for a subscription tier

        Args:
            tier: Subscription tier

        Returns:
            Dictionary of limits
        """
        tier_config = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["free"])
        return tier_config["limits"]

    def check_limit(
        self,
        tier: str,
        limit_key: str,
        current_usage: int,
    ) -> bool:
        """
        Check if usage is within tier limits

        Args:
            tier: Subscription tier
            limit_key: Limit to check (e.g., "ml_predictions_per_month")
            current_usage: Current usage count

        Returns:
            True if within limits, False if exceeded
        """
        limits = self.get_tier_limits(tier)
        limit = limits.get(limit_key, 0)

        # -1 means unlimited
        if limit == -1:
            return True

        return current_usage < limit


# Singleton instance
_stripe_service = None


def get_stripe_service() -> StripeService:
    """Get or create Stripe service instance"""
    global _stripe_service
    if _stripe_service is None:
        _stripe_service = StripeService()
    return _stripe_service
