"""
Monitor API Router - Provides monitoring dashboard data

Endpoints:
- GET /dashboard - Complete dashboard data
- GET /counters - Event counters
- GET /progress - Completion progress with history
- GET /alerts - Recent alerts
- POST /webhook - GitHub webhook receiver
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from app.core.config import settings
from app.services.alert_manager import AlertSeverity, get_alert_manager
from app.services.counter_manager import get_counter_manager
from app.services.github_monitor import GitHubWebhookHandler


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitor", tags=["monitoring"])


@router.get("/dashboard")
async def get_dashboard() -> dict[str, Any]:
    """
    Get complete dashboard data

    Returns all monitoring metrics for dashboard display
    """
    try:
        counter_mgr = await get_counter_manager()
        alert_mgr = get_alert_manager()

        # Get event counters
        event_counters = {
            "commits": await counter_mgr.get("commits"),
            "pushes": await counter_mgr.get("pushes"),
            "pulls_opened": await counter_mgr.get("pulls_opened"),
            "pulls_merged": await counter_mgr.get("pulls_merged"),
            "pulls_closed": await counter_mgr.get("pulls_closed"),
            "issues_opened": await counter_mgr.get("issues_opened"),
            "issues_closed": await counter_mgr.get("issues_closed"),
            "deployments": await counter_mgr.get("deployments"),
            "build_failures": await counter_mgr.get("build_failures"),
            "test_failures": await counter_mgr.get("test_failures"),
            "conflicts": await counter_mgr.get("conflicts"),
        }

        # Get issue health (from ISSUE_TRACKER.md data)
        issue_health = {
            "total_issues": await counter_mgr.get("total_issues"),
            "critical_p0": await counter_mgr.get("issues_p0"),
            "high_p1": await counter_mgr.get("issues_p1"),
            "medium_p2": await counter_mgr.get("issues_p2"),
            "assigned": await counter_mgr.get("issues_assigned"),
            "unassigned": await counter_mgr.get("issues_unassigned"),
            "blocked": await counter_mgr.get("issues_blocked"),
            "avg_resolution_time_hours": await counter_mgr.get("avg_resolution_hours")
            / 10.0,  # Stored as tenths
        }

        # Get completion tracking
        completion_tracking = await counter_mgr.get_completion_progress()

        # Get system health
        system_health = {
            "frontend_status": "healthy",  # Would check actual health
            "backend_status": "healthy",
            "database_status": "healthy",
            "redis_status": "healthy",
            "last_crash": None,  # Would track actual crashes
            "uptime_percent_7d": await counter_mgr.get("uptime_7d")
            / 10.0,  # Stored as tenths
            "api_error_rate_5m": await counter_mgr.get("error_rate_5m")
            / 10000.0,  # Stored as ten-thousandths
        }

        # Get recent alerts
        recent_alerts = await alert_mgr.get_recent_alerts(limit=5)

        return {
            "eventCounters": event_counters,
            "issueHealth": issue_health,
            "completionTracking": completion_tracking,
            "systemHealth": system_health,
            "recentAlerts": recent_alerts,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get dashboard data: {e!s}"
        )


@router.get("/counters")
async def get_counters() -> dict[str, int]:
    """Get all event counters"""
    try:
        counter_mgr = await get_counter_manager()
        return await counter_mgr.get_all()
    except Exception as e:
        logger.error(f"Error getting counters: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress")
async def get_progress(days: int = 30) -> dict[str, Any]:
    """
    Get project completion progress with historical data

    Args:
        days: Number of days of history to return

    Returns:
        Current progress and historical data points for line graph
    """
    try:
        counter_mgr = await get_counter_manager()

        # Get current progress
        current = await counter_mgr.get_completion_progress()

        # Get historical data
        history = await counter_mgr.get_progress_history(days=days)

        return {
            "current": current,
            "history": history,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting progress data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(limit: int = 10, severity: str | None = None) -> dict[str, Any]:
    """
    Get recent alerts

    Args:
        limit: Maximum number of alerts to return
        severity: Filter by severity (critical, high, medium, low)

    Returns:
        List of recent alerts
    """
    try:
        alert_mgr = get_alert_manager()

        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid severity: {severity}"
                )

        alerts = await alert_mgr.get_recent_alerts(limit=limit, severity=severity_enum)

        return {
            "alerts": alerts,
            "total": len(alerts),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(None),
    x_github_event: str | None = Header(None),
):
    """
    Receive GitHub webhook events

    This endpoint is called by GitHub when repository events occur.
    Configure in GitHub: Repository → Settings → Webhooks
    """
    try:
        # Get webhook secret from settings
        webhook_secret = getattr(settings, "GITHUB_WEBHOOK_SECRET", None)

        if not webhook_secret:
            logger.warning("GITHUB_WEBHOOK_SECRET not configured")
            return {"status": "accepted", "warning": "signature verification disabled"}

        # Get raw body for signature verification
        payload = await request.body()

        # Verify signature
        handler = GitHubWebhookHandler(webhook_secret)
        if not handler.verify_signature(payload, x_hub_signature_256 or ""):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Parse JSON
        event_data = await request.json()

        # Route to appropriate handler
        if x_github_event == "push":
            await handler.handle_push(event_data)
        elif x_github_event == "pull_request":
            await handler.handle_pull_request(event_data)
        elif x_github_event == "check_suite":
            await handler.handle_check_suite(event_data)
        elif x_github_event == "issues":
            await handler.handle_issues(event_data)
        elif x_github_event == "deployment_status":
            await handler.handle_deployment(event_data)
        else:
            logger.info(f"Unhandled webhook event: {x_github_event}")

        return {
            "status": "processed",
            "event_type": x_github_event,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/snapshot")
async def record_progress_snapshot():
    """
    Record current progress snapshot for historical tracking

    Call this daily (via cron) to track progress over time
    """
    try:
        counter_mgr = await get_counter_manager()
        await counter_mgr.record_progress_snapshot()

        return {"status": "recorded", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error recording progress snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progress/update")
async def update_phase_progress(
    phase: str, tasks_completed: int, tasks_total: int, hours_remaining: float
):
    """
    Update progress for a specific phase

    Args:
        phase: Phase identifier (phase_0, phase_1, etc.)
        tasks_completed: Number of completed tasks
        tasks_total: Total number of tasks
        hours_remaining: Estimated hours remaining
    """
    try:
        valid_phases = ["phase_0", "phase_1", "phase_2", "phase_3", "phase_4"]
        if phase not in valid_phases:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid phase. Must be one of: {', '.join(valid_phases)}",
            )

        counter_mgr = await get_counter_manager()
        await counter_mgr.update_phase_progress(
            phase=phase,
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            hours_remaining=hours_remaining,
        )

        return {
            "status": "updated",
            "phase": phase,
            "progress": tasks_completed / tasks_total if tasks_total > 0 else 0,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating phase progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/issues/sync")
async def sync_issue_counts(
    total: int, p0: int, p1: int, p2: int, assigned: int = 0, blocked: int = 0
):
    """
    Sync issue counts from ISSUE_TRACKER.md

    Call this when issue tracker is updated to reflect changes in dashboard
    """
    try:
        counter_mgr = await get_counter_manager()

        await counter_mgr.set("total_issues", total)
        await counter_mgr.set("issues_p0", p0)
        await counter_mgr.set("issues_p1", p1)
        await counter_mgr.set("issues_p2", p2)
        await counter_mgr.set("issues_assigned", assigned)
        await counter_mgr.set("issues_unassigned", total - assigned)
        await counter_mgr.set("issues_blocked", blocked)

        return {
            "status": "synced",
            "total_issues": total,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error syncing issue counts: {e}")
        raise HTTPException(status_code=500, detail=str(e))
