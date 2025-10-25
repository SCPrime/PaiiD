"""
GitHub Repository Monitor API Router
Provides endpoints for monitoring dashboard and counters
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..core.jwt import get_current_user
from ..core.config import settings
from ..models.user import User
from ..services.counter_manager import get_counter_manager
from ..services.github_monitor import get_github_handler


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/monitor", tags=["Repository Monitor"])
settings = get_settings()


# Response Models
class CountersResponse(BaseModel):
    """Current counter values"""

    commits: int = 0
    pushes: int = 0
    pulls_opened: int = 0
    pulls_merged: int = 0
    pulls_closed: int = 0
    issues_opened: int = 0
    issues_closed: int = 0
    deployments: int = 0
    build_failures: int = 0
    test_failures: int = 0
    conflicts: int = 0
    hotfixes: int = 0


class DashboardResponse(BaseModel):
    """Complete dashboard data"""

    event_counters: CountersResponse
    timestamp: datetime
    status: str


class TrendPoint(BaseModel):
    """Single point in trend data"""

    timestamp: float
    value: int


class TrendResponse(BaseModel):
    """Trend data for a counter"""

    counter_name: str
    hours: int
    data: list[TrendPoint]


# Endpoints
@router.get("/counters", response_model=CountersResponse)
async def get_counters(current_user: User = Depends(get_current_user)):
    """
    Get all current counter values

    Returns current week's activity counters.
    """
    try:
        counter_manager = get_counter_manager()
        all_counters = await counter_manager.get_all()

        return CountersResponse(
            commits=all_counters.get("commits", 0),
            pushes=all_counters.get("pushes", 0),
            pulls_opened=all_counters.get("pulls_opened", 0),
            pulls_merged=all_counters.get("pulls_merged", 0),
            pulls_closed=all_counters.get("pulls_closed", 0),
            issues_opened=all_counters.get("issues_opened", 0),
            issues_closed=all_counters.get("issues_closed", 0),
            deployments=all_counters.get("deployments", 0),
            build_failures=all_counters.get("build_failures", 0),
            test_failures=all_counters.get("test_failures", 0),
            conflicts=all_counters.get("conflicts", 0),
            hotfixes=all_counters.get("hotfixes", 0),
        )

    except Exception as e:
        logger.error(f"Error getting counters: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get counters: {e!s}"
        ) from e


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(current_user: User = Depends(get_current_user)):
    """
    Get complete dashboard data

    Returns all monitoring data for the dashboard UI.
    """
    try:
        counter_manager = get_counter_manager()
        all_counters = await counter_manager.get_all()

        counters = CountersResponse(
            commits=all_counters.get("commits", 0),
            pushes=all_counters.get("pushes", 0),
            pulls_opened=all_counters.get("pulls_opened", 0),
            pulls_merged=all_counters.get("pulls_merged", 0),
            pulls_closed=all_counters.get("pulls_closed", 0),
            issues_opened=all_counters.get("issues_opened", 0),
            issues_closed=all_counters.get("issues_closed", 0),
            deployments=all_counters.get("deployments", 0),
            build_failures=all_counters.get("build_failures", 0),
            test_failures=all_counters.get("test_failures", 0),
            conflicts=all_counters.get("conflicts", 0),
            hotfixes=all_counters.get("hotfixes", 0),
        )

        return DashboardResponse(
            event_counters=counters,
            timestamp=datetime.now(UTC),
            status="healthy",
        )

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get dashboard data: {e!s}"
        ) from e


@router.get("/trend/{counter_name}", response_model=TrendResponse)
async def get_counter_trend(
    counter_name: str,
    hours: int = 24,
    current_user: User = Depends(get_current_user),
):
    """
    Get trend data for a specific counter

    Args:
        counter_name: Name of the counter
        hours: Number of hours to look back (default: 24)

    Returns:
        Trend data with timestamps and values
    """
    try:
        counter_manager = get_counter_manager()
        trend_data = await counter_manager.get_trend(counter_name, hours)

        return TrendResponse(
            counter_name=counter_name,
            hours=hours,
            data=[
                TrendPoint(timestamp=point["timestamp"], value=point["value"])
                for point in trend_data
            ],
        )

    except Exception as e:
        logger.error(f"Error getting trend for {counter_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get trend data: {e!s}"
        ) from e


@router.post("/webhook")
async def github_webhook(request: Request):
    """
    Receive GitHub webhook events

    This endpoint receives webhooks from GitHub and processes events.
    Requires webhook secret verification.
    """
    try:
        # Get signature and event type from headers
        signature = request.headers.get("X-Hub-Signature-256", "")
        event_type = request.headers.get("X-GitHub-Event", "unknown")

        # Get raw payload for signature verification
        payload = await request.body()

        # Get handler
        handler = get_github_handler()

        # Verify signature
        if not handler.verify_signature(payload, signature):
            logger.warning(f"Invalid webhook signature for {event_type} event")
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Parse JSON payload
        event_data = await request.json()

        # Route to appropriate handler
        result = {"event_type": event_type, "processed": False}

        if event_type == "push":
            result = await handler.handle_push(event_data)
        elif event_type == "pull_request":
            result = await handler.handle_pull_request(event_data)
        elif event_type == "issues":
            result = await handler.handle_issues(event_data)
        elif event_type == "check_suite":
            result = await handler.handle_check_suite(event_data)
        elif event_type == "deployment":
            result = await handler.handle_deployment(event_data)
        elif event_type == "deployment_status":
            result = await handler.handle_deployment_status(event_data)
        elif event_type == "release":
            result = await handler.handle_release(event_data)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            result = {"event_type": event_type, "status": "unhandled"}

        result["processed"] = True
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {e!s}"
        ) from e


@router.post("/reset-weekly")
async def reset_weekly_counters(current_user: User = Depends(get_current_user)):
    """
    Reset weekly counters

    Resets all weekly counters to zero.
    Typically called by a scheduler on Monday at midnight.
    """
    try:
        counter_manager = get_counter_manager()
        reset_count = await counter_manager.reset_weekly_counters()

        return {
            "status": "success",
            "reset_count": reset_count,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error(f"Error resetting weekly counters: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reset counters: {e!s}"
        ) from e


@router.get("/health")
async def monitor_health_check():
    """Check monitor service health"""
    try:
        counter_manager = get_counter_manager()

        # Try to get a counter to verify Redis connection
        await counter_manager.get("commits")

        return {
            "status": "healthy",
            "services": {
                "counter_manager": "ready",
                "webhook_handler": "ready",
                "redis": "connected",
            },
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        logger.error(f"Monitor health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }

