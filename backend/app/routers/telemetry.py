"""
Telemetry Router - Tracks user interactions and system events
"""

import json
from datetime import datetime
import json
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])

# In-memory storage (replace with database in production)
telemetry_events: list[dict[str, Any]] = []


class TelemetryEvent(BaseModel):
    userId: str
    sessionId: str
    component: str
    action: str
    timestamp: str
    metadata: dict[str, Any]
    userRole: str


class TelemetryBatch(BaseModel):
    events: list[TelemetryEvent]


@router.post("", status_code=status.HTTP_201_CREATED)
async def log_telemetry(batch: TelemetryBatch):
    """
    Receive and store telemetry events
    """
    try:
        # Store events
        for event in batch.events:
            event_dict = event.dict()
            telemetry_events.append(event_dict)

        # Optional: Write to file for persistence
        log_file = "telemetry_events.jsonl"
        with open(log_file, "a", encoding="utf-8") as file_handle:
            for event in batch.events:
                file_handle.write(json.dumps(event.dict()) + "\n")

        logger.info("Logged %d telemetry events", len(batch.events))

        return {
            "success": True,
            "received": len(batch.events),
            "message": f"Logged {len(batch.events)} telemetry events",
        }
    except Exception as exc:
        logger.error("Failed to persist telemetry events: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record telemetry events",
        )


@router.get("/events")
async def get_telemetry_events(
    limit: int = 100,
    user_id: Optional[str] = None,
    component: Optional[str] = None,
    action: Optional[str] = None,
    user_role: Optional[str] = None,
):
    """
    Retrieve telemetry events with optional filters
    """
    try:
        filtered_events = telemetry_events

        # Apply filters
        if user_id:
            filtered_events = [
                event for event in filtered_events if event.get("userId") == user_id
            ]
        if component:
            filtered_events = [
                event for event in filtered_events if event.get("component") == component
            ]
        if action:
            filtered_events = [
                event for event in filtered_events if event.get("action") == action
            ]
        if user_role:
            filtered_events = [
                event for event in filtered_events if event.get("userRole") == user_role
            ]

        # Sort by timestamp (newest first)
        filtered_events = sorted(
            filtered_events, key=lambda event: event.get("timestamp", ""), reverse=True
        )

        return {"total": len(filtered_events), "events": filtered_events[:limit]}
    except Exception as exc:
        logger.error("Failed to filter telemetry events: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load telemetry events",
        )


@router.get("/stats")
async def get_telemetry_stats():
    """
    Get aggregate statistics from telemetry data
    """
    try:
        if not telemetry_events:
            return {
                "total_events": 0,
                "unique_users": 0,
                "unique_sessions": 0,
                "top_components": [],
                "top_actions": [],
                "users_by_role": {},
            }

        unique_users = set(event.get("userId") for event in telemetry_events)
        unique_sessions = set(event.get("sessionId") for event in telemetry_events)

        # Count by component
        component_counts: dict[str, int] = {}
        for event in telemetry_events:
            comp = event.get("component", "Unknown")
            component_counts[comp] = component_counts.get(comp, 0) + 1

        # Count by action
        action_counts: dict[str, int] = {}
        for event in telemetry_events:
            action_value = event.get("action", "Unknown")
            action_counts[action_value] = action_counts.get(action_value, 0) + 1

        # Count by role
        role_counts: dict[str, int] = {}
        for event in telemetry_events:
            role_value = event.get("userRole", "unknown")
            role_counts[role_value] = role_counts.get(role_value, 0) + 1

        # Sort and get top 10
        top_components = sorted(
            component_counts.items(), key=lambda item: item[1], reverse=True
        )[:10]
        top_actions = sorted(
            action_counts.items(), key=lambda item: item[1], reverse=True
        )[:10]

        return {
            "total_events": len(telemetry_events),
            "unique_users": len(unique_users),
            "unique_sessions": len(unique_sessions),
            "top_components": [
                {"component": component, "count": count}
                for component, count in top_components
            ],
            "top_actions": [
                {"action": action_label, "count": count}
                for action_label, count in top_actions
            ],
            "users_by_role": role_counts,
        }
    except Exception as exc:
        logger.error("Failed to compute telemetry stats: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to compute telemetry stats",
        )


@router.delete("/events")
async def clear_telemetry_events():
    """
    Clear all telemetry events (admin only)
    """
    try:
        global telemetry_events
        count = len(telemetry_events)
        telemetry_events = []
        logger.info("Cleared %d telemetry events", count)
        return {"success": True, "message": f"Cleared {count} telemetry events"}
    except Exception as exc:
        logger.error("Failed to clear telemetry events: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear telemetry events",
        )


@router.get("/export")
async def export_telemetry():
    """
    Export all telemetry events as JSON
    """
    try:
        return {
            "events": telemetry_events,
            "exported_at": datetime.now().isoformat(),
            "total": len(telemetry_events),
        }
    except Exception as exc:
        logger.error("Failed to export telemetry events: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export telemetry events",
        )
