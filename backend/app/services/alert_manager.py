            from app.models.monitor import MonitorAlert
            from app.models.monitor import MonitorAlert
from app.core.config import settings
from app.core.database import SessionLocal
from datetime import UTC, datetime
from enum import Enum
from typing import Any
import asyncio
import httpx
import logging

"""
Alert Manager Service - Handles alerting for monitoring events

Sends alerts via:
- Slack webhooks
- Discord webhooks
- Email (SMTP)
- Database logging for dashboard display
"""




logger = logging.getLogger(__name__)

class AlertSeverity(str, Enum):
    """Alert severity levels"""

    CRITICAL = "critical"  # Immediate action required (crashes, deployment failures)
    HIGH = "high"  # Attention needed soon (build failures, merge conflicts)
    MEDIUM = "medium"  # Notable event (stale PRs, increased error rates)
    LOW = "low"  # Informational (successful deployments, milestones)

class AlertManager:
    """Manages alerts across multiple channels"""

    def __init__(self):
        self.slack_webhook = getattr(settings, "SLACK_WEBHOOK_URL", None)
        self.discord_webhook = getattr(settings, "DISCORD_WEBHOOK_URL", None)
        self.alert_threshold = AlertSeverity.MEDIUM

    async def send_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ):
        """
        Send alert to configured channels

        Args:
            severity: Alert severity level
            title: Short alert title
            message: Detailed message
            context: Additional context data
            tags: List of tags for categorization
        """

        # Check severity threshold
        severity_order = {
            AlertSeverity.LOW: 0,
            AlertSeverity.MEDIUM: 1,
            AlertSeverity.HIGH: 2,
            AlertSeverity.CRITICAL: 3,
        }

        if severity_order[severity] < severity_order[self.alert_threshold]:
            logger.debug(
                f"Alert filtered by threshold: {severity} < {self.alert_threshold}"
            )
            return

        alert = {
            "severity": severity.value,
            "title": title,
            "message": message,
            "context": context or {},
            "tags": tags or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Store alert in database for dashboard
        await self.store_alert(alert)

        # Send to channels based on severity
        tasks = []

        # Critical and High alerts go to Slack
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            if self.slack_webhook:
                tasks.append(self.send_slack(alert))

        # Critical alerts also go to Discord
        if severity == AlertSeverity.CRITICAL and self.discord_webhook:
            tasks.append(self.send_discord(alert))

        # Execute all sends in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Failed to send alert: {result}")

    async def send_slack(self, alert: dict[str, Any]):
        """Send alert to Slack via webhook"""
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

        color = {
            "critical": "#FF0000",
            "high": "#FF8C00",
            "medium": "#FFD700",
            "low": "#00FF00",
        }

        payload = {
            "text": f"{emoji[alert['severity']]} *{alert['title']}*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{alert['title']}*\n{alert['message']}",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Severity: {alert['severity'].upper()} | Time: {alert['timestamp']}",
                        }
                    ],
                },
            ],
            "attachments": [
                {
                    "color": color[alert["severity"]],
                    "fields": [
                        {"title": key, "value": str(value), "short": True}
                        for key, value in alert["context"].items()
                    ]
                    if alert["context"]
                    else [],
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.slack_webhook, json=payload)
                response.raise_for_status()
                logger.info(f"Sent Slack alert: {alert['title']}")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            raise

    async def send_discord(self, alert: dict[str, Any]):
        """Send alert to Discord via webhook"""
        color_map = {
            "critical": 0xFF0000,  # Red
            "high": 0xFF8C00,  # Orange
            "medium": 0xFFD700,  # Gold
            "low": 0x00FF00,  # Green
        }

        embed = {
            "title": alert["title"],
            "description": alert["message"],
            "color": color_map[alert["severity"]],
            "timestamp": alert["timestamp"],
            "fields": [
                {"name": "Severity", "value": alert["severity"].upper(), "inline": True}
            ],
        }

        # Add context fields
        if alert["context"]:
            for key, value in alert["context"].items():
                embed["fields"].append(
                    {"name": key, "value": str(value), "inline": True}
                )

        payload = {"embeds": [embed]}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.discord_webhook, json=payload)
                response.raise_for_status()
                logger.info(f"Sent Discord alert: {alert['title']}")
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            raise

    async def store_alert(self, alert: dict[str, Any]):
        """Store alert in database for dashboard display"""
        try:
            # Import here to avoid circular dependency

            db = SessionLocal()
            try:
                db_alert = MonitorAlert(
                    severity=alert["severity"],
                    title=alert["title"],
                    message=alert["message"],
                    context=alert["context"],
                    tags=alert.get("tags", []),
                    created_at=datetime.fromisoformat(alert["timestamp"]),
                )
                db.add(db_alert)
                db.commit()
                logger.debug(f"Stored alert in database: {alert['title']}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to store alert in database: {e}")

    async def get_recent_alerts(
        self, limit: int = 10, severity: AlertSeverity | None = None
    ) -> list[dict[str, Any]]:
        """
        Get recent alerts from database

        Args:
            limit: Maximum number of alerts to return
            severity: Filter by severity (optional)

        Returns:
            List of recent alerts
        """
        try:

            db = SessionLocal()
            try:
                query = db.query(MonitorAlert).order_by(MonitorAlert.created_at.desc())

                if severity:
                    query = query.filter(MonitorAlert.severity == severity.value)

                alerts = query.limit(limit).all()

                return [
                    {
                        "id": alert.id,
                        "severity": alert.severity,
                        "title": alert.title,
                        "message": alert.message,
                        "context": alert.context,
                        "tags": alert.tags,
                        "timestamp": alert.created_at.isoformat(),
                    }
                    for alert in alerts
                ]
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []

# Singleton instance
_alert_manager = None

def get_alert_manager() -> AlertManager:
    """Get or create AlertManager singleton"""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager
