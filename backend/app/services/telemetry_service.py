"""
Telemetry Service - Business logic for event tracking and analytics

This service handles storage, retrieval, and analysis of user interaction events.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ..core.logging_utils import get_secure_logger


logger = get_secure_logger(__name__)


class TelemetryEvent(BaseModel):
    """Telemetry event model"""

    userId: str  # noqa: N815 - API contract requires mixedCase
    sessionId: str  # noqa: N815 - API contract requires mixedCase
    component: str
    action: str
    timestamp: str
    metadata: dict[str, Any]
    userRole: str  # noqa: N815 - API contract requires mixedCase


class TelemetryStats:
    """Telemetry statistics data class"""

    def __init__(
        self,
        total_events: int,
        unique_users: int,
        unique_sessions: int,
        top_components: list[dict],
        top_actions: list[dict],
        users_by_role: dict[str, int],
    ):
        self.total_events = total_events
        self.unique_users = unique_users
        self.unique_sessions = unique_sessions
        self.top_components = top_components
        self.top_actions = top_actions
        self.users_by_role = users_by_role

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "total_events": self.total_events,
            "unique_users": self.unique_users,
            "unique_sessions": self.unique_sessions,
            "top_components": self.top_components,
            "top_actions": self.top_actions,
            "users_by_role": self.users_by_role,
        }


class TelemetryService:
    """Service for tracking and analyzing user interaction events"""

    def __init__(self, log_file: str = "telemetry_events.jsonl"):
        """
        Initialize telemetry service

        Args:
            log_file: Path to JSONL file for event persistence
        """
        self.log_file = Path(log_file)
        self.events: list[dict[str, Any]] = []

    def log_events(self, events: list[TelemetryEvent]) -> int:
        """
        Store telemetry events in memory and persist to file

        Args:
            events: List of telemetry events to log

        Returns:
            Number of events successfully logged
        """
        count = 0
        for event in events:
            event_dict = event.model_dump()
            self.events.append(event_dict)
            count += 1

        # Persist to file for durability
        try:
            with open(self.log_file, "a") as f:
                for event in events:
                    f.write(json.dumps(event.model_dump()) + "\n")
        except OSError as e:
            logger.error(
                "Failed to persist telemetry events to file",
                error_type=type(e).__name__,
                error_msg=str(e),
            )

        return count

    def get_events(
        self,
        limit: int = 100,
        user_id: str | None = None,
        component: str | None = None,
        action: str | None = None,
        user_role: str | None = None,
    ) -> list[dict]:
        """
        Retrieve telemetry events with optional filters

        Args:
            limit: Maximum number of events to return
            user_id: Filter by user ID
            component: Filter by component name
            action: Filter by action name
            user_role: Filter by user role

        Returns:
            List of filtered events, sorted by timestamp (newest first)
        """
        filtered_events = self.events

        # Apply filters
        if user_id:
            filtered_events = [e for e in filtered_events if e.get("userId") == user_id]
        if component:
            filtered_events = [
                e for e in filtered_events if e.get("component") == component
            ]
        if action:
            filtered_events = [e for e in filtered_events if e.get("action") == action]
        if user_role:
            filtered_events = [
                e for e in filtered_events if e.get("userRole") == user_role
            ]

        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return filtered_events[:limit]

    def get_statistics(self) -> TelemetryStats:
        """
        Calculate aggregate statistics from telemetry data

        Returns:
            TelemetryStats object with aggregated metrics
        """
        if not self.events:
            return TelemetryStats(
                total_events=0,
                unique_users=0,
                unique_sessions=0,
                top_components=[],
                top_actions=[],
                users_by_role={},
            )

        # Calculate unique counts
        unique_users = {e.get("userId") for e in self.events}
        unique_sessions = {e.get("sessionId") for e in self.events}

        # Count by component
        component_counts: dict[str, int] = {}
        for event in self.events:
            comp = event.get("component", "Unknown")
            component_counts[comp] = component_counts.get(comp, 0) + 1

        # Count by action
        action_counts: dict[str, int] = {}
        for event in self.events:
            action = event.get("action", "Unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        # Count by role
        role_counts: dict[str, int] = {}
        for event in self.events:
            role = event.get("userRole", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        # Get top 10 for each category
        top_components = sorted(
            component_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        top_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        return TelemetryStats(
            total_events=len(self.events),
            unique_users=len(unique_users),
            unique_sessions=len(unique_sessions),
            top_components=[{"component": c, "count": n} for c, n in top_components],
            top_actions=[{"action": a, "count": n} for a, n in top_actions],
            users_by_role=role_counts,
        )

    def clear_events(self) -> int:
        """
        Clear all telemetry events from memory

        Returns:
            Number of events cleared

        Note:
            This does NOT delete the persisted file, only the in-memory cache
        """
        count = len(self.events)
        self.events = []
        logger.info("Cleared telemetry events", count=count)
        return count

    def export_events(self) -> dict:
        """
        Export all telemetry events as a dictionary

        Returns:
            Dictionary with events, export timestamp, and total count
        """
        return {
            "events": self.events,
            "exported_at": datetime.now().isoformat(),
            "total": len(self.events),
        }


# Singleton instance
_telemetry_service: TelemetryService | None = None


def get_telemetry_service() -> TelemetryService:
    """Get or create the singleton telemetry service instance"""
    global _telemetry_service
    if _telemetry_service is None:
        _telemetry_service = TelemetryService()
    return _telemetry_service
