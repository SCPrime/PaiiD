"""
Notification Service

Handles all user notifications including:
- Order fill notifications
- Price alerts
- Portfolio alerts (threshold breaches)
- Trade execution confirmations
- System notifications

This service centralizes notification logic that was previously scattered
across multiple routers.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""

    ORDER_FILL = "order_fill"
    PRICE_ALERT = "price_alert"
    PORTFOLIO_ALERT = "portfolio_alert"
    TRADE_CONFIRMATION = "trade_confirmation"
    SYSTEM_NOTIFICATION = "system_notification"
    RISK_ALERT = "risk_alert"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Notification model"""

    notification_id: str
    user_id: str
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    data: dict[str, Any] = {}
    read: bool = False
    timestamp: str


class NotificationPreferences(BaseModel):
    """User notification preferences"""

    email_enabled: bool = True
    in_app_enabled: bool = True
    order_fill_notifications: bool = True
    price_alert_notifications: bool = True
    portfolio_alert_notifications: bool = True
    daily_summary: bool = False


class NotificationService:
    """
    Notification service for managing user notifications.

    Framework-agnostic service that handles notification delivery
    across multiple channels (email, in-app, etc.).
    """

    def __init__(self, db_session: Any | None = None):
        """
        Initialize notification service.

        Args:
            db_session: Optional database session for storing notifications
        """
        self.db = db_session
        # In-memory storage for demo (would use database in production)
        self._notifications: dict[str, list[Notification]] = {}
        self._preferences: dict[str, NotificationPreferences] = {}

    async def send_order_fill_notification(
        self,
        user_id: str,
        order: dict[str, Any],
    ) -> Notification | None:
        """
        Send notification when order is filled.

        Args:
            user_id: User ID
            order: Order data dictionary

        Returns:
            Notification object if sent, None if user preferences disabled

        Example:
            >>> service = NotificationService()
            >>> notification = await service.send_order_fill_notification(
            ...     "user123",
            ...     {"symbol": "AAPL", "qty": 10, "price": 180.50, "side": "buy"}
            ... )
        """
        # Check user preferences
        prefs = self._get_preferences(user_id)
        if not prefs.order_fill_notifications:
            logger.info(f"Order fill notifications disabled for user {user_id}")
            return None

        symbol = order.get("symbol", "Unknown")
        qty = order.get("qty", 0)
        price = order.get("price", 0)
        side = order.get("side", "").upper()

        notification = Notification(
            notification_id=self._generate_id(),
            user_id=user_id,
            type=NotificationType.ORDER_FILL,
            priority=NotificationPriority.HIGH,
            title=f"Order Filled: {symbol}",
            message=f"{side} {qty} shares of {symbol} at ${price:.2f}",
            data=order,
            timestamp=datetime.now().isoformat(),
        )

        self._store_notification(notification)

        # Send via enabled channels
        if prefs.email_enabled:
            await self._send_email(notification)

        if prefs.in_app_enabled:
            await self._send_in_app(notification)

        logger.info(f"Order fill notification sent to user {user_id}: {symbol}")
        return notification

    async def send_price_alert(
        self,
        user_id: str,
        symbol: str,
        current_price: float,
        target_price: float,
        condition: str,
    ) -> Notification | None:
        """
        Send price alert notification.

        Args:
            user_id: User ID
            symbol: Stock symbol
            current_price: Current market price
            target_price: Target price that was hit
            condition: Alert condition ("above" or "below")

        Returns:
            Notification object if sent, None if disabled

        Example:
            >>> notification = await service.send_price_alert(
            ...     "user123", "TSLA", 245.30, 250.00, "below"
            ... )
        """
        prefs = self._get_preferences(user_id)
        if not prefs.price_alert_notifications:
            logger.info(f"Price alert notifications disabled for user {user_id}")
            return None

        notification = Notification(
            notification_id=self._generate_id(),
            user_id=user_id,
            type=NotificationType.PRICE_ALERT,
            priority=NotificationPriority.MEDIUM,
            title=f"Price Alert: {symbol}",
            message=f"{symbol} is now ${current_price:.2f} ({condition} ${target_price:.2f})",
            data={
                "symbol": symbol,
                "current_price": current_price,
                "target_price": target_price,
                "condition": condition,
            },
            timestamp=datetime.now().isoformat(),
        )

        self._store_notification(notification)

        if prefs.in_app_enabled:
            await self._send_in_app(notification)

        logger.info(f"Price alert sent to user {user_id}: {symbol} @ ${current_price:.2f}")
        return notification

    async def send_portfolio_alert(
        self,
        user_id: str,
        alert_type: str,
        message: str,
        data: dict[str, Any],
    ) -> Notification | None:
        """
        Send portfolio alert (e.g., loss threshold, concentration risk).

        Args:
            user_id: User ID
            alert_type: Type of portfolio alert
            message: Alert message
            data: Additional alert data

        Returns:
            Notification object if sent, None if disabled
        """
        prefs = self._get_preferences(user_id)
        if not prefs.portfolio_alert_notifications:
            logger.info(f"Portfolio alert notifications disabled for user {user_id}")
            return None

        # Determine priority based on alert type
        priority = NotificationPriority.HIGH
        if "risk" in alert_type.lower() or "loss" in alert_type.lower():
            priority = NotificationPriority.URGENT

        notification = Notification(
            notification_id=self._generate_id(),
            user_id=user_id,
            type=NotificationType.PORTFOLIO_ALERT,
            priority=priority,
            title=f"Portfolio Alert: {alert_type}",
            message=message,
            data=data,
            timestamp=datetime.now().isoformat(),
        )

        self._store_notification(notification)

        # Always send urgent alerts
        if priority == NotificationPriority.URGENT:
            if prefs.email_enabled:
                await self._send_email(notification)
            await self._send_in_app(notification)
        elif prefs.in_app_enabled:
            await self._send_in_app(notification)

        logger.info(f"Portfolio alert sent to user {user_id}: {alert_type}")
        return notification

    async def send_trade_confirmation(
        self,
        user_id: str,
        trade: dict[str, Any],
    ) -> Notification | None:
        """
        Send trade execution confirmation.

        Args:
            user_id: User ID
            trade: Trade execution data

        Returns:
            Notification object if sent
        """
        symbol = trade.get("symbol", "Unknown")
        side = trade.get("side", "").upper()
        qty = trade.get("qty", 0)

        notification = Notification(
            notification_id=self._generate_id(),
            user_id=user_id,
            type=NotificationType.TRADE_CONFIRMATION,
            priority=NotificationPriority.MEDIUM,
            title=f"Trade Executed: {symbol}",
            message=f"{side} {qty} shares of {symbol}",
            data=trade,
            timestamp=datetime.now().isoformat(),
        )

        self._store_notification(notification)

        prefs = self._get_preferences(user_id)
        if prefs.in_app_enabled:
            await self._send_in_app(notification)

        logger.info(f"Trade confirmation sent to user {user_id}: {symbol}")
        return notification

    async def send_system_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.LOW,
    ) -> Notification:
        """
        Send generic system notification.

        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            priority: Notification priority

        Returns:
            Notification object
        """
        notification = Notification(
            notification_id=self._generate_id(),
            user_id=user_id,
            type=NotificationType.SYSTEM_NOTIFICATION,
            priority=priority,
            title=title,
            message=message,
            data={},
            timestamp=datetime.now().isoformat(),
        )

        self._store_notification(notification)

        prefs = self._get_preferences(user_id)
        if prefs.in_app_enabled:
            await self._send_in_app(notification)

        logger.info(f"System notification sent to user {user_id}: {title}")
        return notification

    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        """
        Get user's notifications.

        Args:
            user_id: User ID
            unread_only: Return only unread notifications
            limit: Maximum number of notifications to return

        Returns:
            List of notifications
        """
        user_notifications = self._notifications.get(user_id, [])

        if unread_only:
            user_notifications = [n for n in user_notifications if not n.read]

        # Sort by timestamp descending (newest first)
        user_notifications.sort(
            key=lambda n: n.timestamp,
            reverse=True,
        )

        return user_notifications[:limit]

    async def mark_as_read(
        self,
        user_id: str,
        notification_id: str,
    ) -> bool:
        """
        Mark notification as read.

        Args:
            user_id: User ID
            notification_id: Notification ID

        Returns:
            True if marked, False if not found
        """
        user_notifications = self._notifications.get(user_id, [])

        for notification in user_notifications:
            if notification.notification_id == notification_id:
                notification.read = True
                logger.info(f"Marked notification {notification_id} as read for user {user_id}")
                return True

        return False

    async def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for user.

        Args:
            user_id: User ID

        Returns:
            Number of notifications marked as read
        """
        user_notifications = self._notifications.get(user_id, [])
        count = 0

        for notification in user_notifications:
            if not notification.read:
                notification.read = True
                count += 1

        logger.info(f"Marked {count} notifications as read for user {user_id}")
        return count

    async def get_user_notification_preferences(
        self,
        user_id: str,
    ) -> NotificationPreferences:
        """
        Get user's notification preferences.

        Args:
            user_id: User ID

        Returns:
            NotificationPreferences object
        """
        return self._get_preferences(user_id)

    async def update_user_notification_preferences(
        self,
        user_id: str,
        preferences: NotificationPreferences,
    ) -> NotificationPreferences:
        """
        Update user's notification preferences.

        Args:
            user_id: User ID
            preferences: New preferences

        Returns:
            Updated preferences
        """
        self._preferences[user_id] = preferences
        logger.info(f"Updated notification preferences for user {user_id}")
        return preferences

    def _get_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user preferences with defaults"""
        if user_id not in self._preferences:
            self._preferences[user_id] = NotificationPreferences()
        return self._preferences[user_id]

    def _store_notification(self, notification: Notification) -> None:
        """Store notification in memory (would use database in production)"""
        if notification.user_id not in self._notifications:
            self._notifications[notification.user_id] = []

        self._notifications[notification.user_id].append(notification)

        # Keep only last 100 notifications per user
        if len(self._notifications[notification.user_id]) > 100:
            self._notifications[notification.user_id] = self._notifications[
                notification.user_id
            ][-100:]

    def _generate_id(self) -> str:
        """Generate notification ID"""
        import uuid

        return f"notif_{uuid.uuid4().hex[:12]}"

    async def _send_email(self, notification: Notification) -> None:
        """
        Send email notification (placeholder for production implementation).

        In production, this would integrate with SendGrid, AWS SES, or similar.
        """
        logger.info(
            f"[EMAIL] To: {notification.user_id} | "
            f"Subject: {notification.title} | "
            f"Message: {notification.message}"
        )
        # Production: Integrate with email service
        # await email_client.send(...)

    async def _send_in_app(self, notification: Notification) -> None:
        """
        Send in-app notification (placeholder for WebSocket implementation).

        In production, this would push via WebSocket to connected clients.
        """
        logger.info(
            f"[IN-APP] To: {notification.user_id} | "
            f"Type: {notification.type.value} | "
            f"Priority: {notification.priority.value}"
        )
        # Production: Push via WebSocket
        # await websocket_manager.send_to_user(notification.user_id, notification)


# Singleton instance
_notification_service: NotificationService | None = None


def get_notification_service(db_session: Any | None = None) -> NotificationService:
    """
    Get or create notification service instance.

    Args:
        db_session: Optional database session

    Returns:
        NotificationService instance

    Usage in routers:
        from ..services.notification_service import get_notification_service

        @router.post("/orders")
        async def create_order(order_data: dict):
            # ... create order ...
            notification_service = get_notification_service()
            await notification_service.send_order_fill_notification(
                user_id="user123",
                order=order_data
            )
    """
    global _notification_service

    if _notification_service is None:
        _notification_service = NotificationService(db_session=db_session)

    return _notification_service
