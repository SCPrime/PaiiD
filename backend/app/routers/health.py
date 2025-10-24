"""Enhanced health check endpoints with metrics and diagnostics."""

from datetime import datetime
import logging

import sentry_sdk
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.core.config import settings
from app.services.health_monitor import health_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check - public"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health():
    """Detailed health metrics - requires auth"""
    return health_monitor.get_system_health()


@router.get("/readiness")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    health = health_monitor.get_system_health()
    
    if health["status"] == "healthy":
        return {"ready": True}
    else:
        raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})



@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}


@router.get("/sentry-test")
async def sentry_test_error():
    """Trigger a controlled error to verify Sentry ingestion."""

    if not settings.SENTRY_DSN:
        raise HTTPException(
            status_code=503,
            detail="Sentry DSN is not configured. Set SENTRY_DSN before running the test.",
        )

    try:
        raise RuntimeError(
            "SENTRY TEST ERROR: This is a test error to verify Sentry integration is working"
        )
    except RuntimeError as exc:  # pragma: no cover - behavior verified via response assertions
        sentry_sdk.capture_exception(exc)
        logger.warning("Sentry test error triggered for verification")
        raise HTTPException(
            status_code=500,
            detail="This is a test error to verify Sentry integration is working",
        )
