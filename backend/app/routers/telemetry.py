"""
Telemetry Router - Tracks user interactions and system events

SECURITY: User IDs logged but no sensitive PII
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.logging_utils import get_secure_logger
from ..services.telemetry_service import TelemetryEvent, get_telemetry_service


router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])
logger = get_secure_logger(__name__)


class TelemetryBatch(BaseModel):
    events: list[TelemetryEvent]


@router.post("")
async def log_telemetry(batch: TelemetryBatch):
    """
    Receive and store telemetry events
    """
    try:
        telemetry_service = get_telemetry_service()
        count = telemetry_service.log_events(batch.events)

        return {
            "success": True,
            "received": count,
            "message": f"Logged {count} telemetry events",
        }
    except Exception as e:
        logger.error(
            "Failed to log telemetry events",
            error_type=type(e).__name__,
            error_msg=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/events")
async def get_telemetry_events(
    limit: int = 100,
    user_id: str | None = None,
    component: str | None = None,
    action: str | None = None,
    user_role: str | None = None,
):
    """
    Retrieve telemetry events with optional filters
    """
    try:
        telemetry_service = get_telemetry_service()
        filtered_events = telemetry_service.get_events(
            limit=limit,
            user_id=user_id,
            component=component,
            action=action,
            user_role=user_role,
        )

        return {"total": len(filtered_events), "events": filtered_events}

    except Exception as e:
        logger.error(
            "Failed to get telemetry events",
            error_type=type(e).__name__,
            error_msg=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to get telemetry events") from e


@router.get("/stats")
async def get_telemetry_stats():
    """
    Get aggregate statistics from telemetry data
    """
    try:
        telemetry_service = get_telemetry_service()
        stats = telemetry_service.get_statistics()
        return stats.to_dict()

    except Exception as e:
        logger.error(
            "Failed to get telemetry stats",
            error_type=type(e).__name__,
            error_msg=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to get telemetry stats") from e


@router.delete("/events")
async def clear_telemetry_events():
    """
    Clear all telemetry events (admin only)
    """
    try:
        telemetry_service = get_telemetry_service()
        count = telemetry_service.clear_events()
        return {"success": True, "message": f"Cleared {count} telemetry events"}

    except Exception as e:
        logger.error(
            "Failed to clear telemetry events",
            error_type=type(e).__name__,
            error_msg=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to clear telemetry events") from e


@router.get("/export")
async def export_telemetry():
    """
    Export all telemetry events as JSON
    """
    try:
        telemetry_service = get_telemetry_service()
        return telemetry_service.export_events()

    except Exception as e:
        logger.error(
            "Failed to export telemetry",
            error_type=type(e).__name__,
            error_msg=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to export telemetry") from e
