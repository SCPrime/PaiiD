"""
Production alert system
"""
import logging
import os
from typing import Optional

import requests

from app.core.time_utils import utc_now_isoformat

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        self.email_enabled = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() == "true"
        
    def send_alert(
        self,
        severity: str,  # "critical", "warning", "info"
        title: str,
        message: str,
        details: Optional[dict] = None
    ):
        """Send alert via configured channels"""
        
        alert_data = {
            "severity": severity,
            "title": title,
            "message": message,
            "timestamp": utc_now_isoformat(),
            "details": details or {}
        }
        
        # Send to Slack
        if self.slack_webhook:
            self._send_slack(alert_data)
        
        # Log alert
        if severity == "critical":
            logger.critical(f"ALERT: {title} - {message}")
        elif severity == "warning":
            logger.warning(f"ALERT: {title} - {message}")
        else:
            logger.info(f"ALERT: {title} - {message}")
    
    def _send_slack(self, alert_data: dict):
        """Send alert to Slack"""
        color = {
            "critical": "#ff0000",
            "warning": "#ffaa00",
            "info": "#00ff00"
        }.get(alert_data["severity"], "#cccccc")
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"🚨 {alert_data['title']}",
                "text": alert_data['message'],
                "fields": [
                    {"title": "Severity", "value": alert_data['severity'].upper(), "short": True},
                    {"title": "Time", "value": alert_data['timestamp'], "short": True}
                ],
                "footer": "PaiiD Production Monitor"
            }]
        }
        
        try:
            requests.post(self.slack_webhook, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")


# Global instance
alert_service = AlertService()


# Usage examples:
def check_error_rate():
    """Example: Alert on high error rate"""
    from app.services.health_monitor import health_monitor
    
    health = health_monitor.get_system_health()
    error_rate = health["application"]["error_rate_percent"]
    
    if error_rate > 5:
        alert_service.send_alert(
            severity="critical" if error_rate > 10 else "warning",
            title="High Error Rate Detected",
            message=f"Error rate is {error_rate:.2f}%",
            details=health["application"]
        )
