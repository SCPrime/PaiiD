"""
Enhanced health check endpoints with metrics
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check - public"""
    now = datetime.utcnow().isoformat() + "Z"
    return {
        "status": "ok",
        "time": now,
        "timestamp": now,
    }


@router.get("/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health():
    """Detailed health metrics - requires auth"""
    return health_monitor.get_system_health()


@router.get("/ready")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    return {"ready": True, "checked_at": datetime.utcnow().isoformat() + "Z"}


@router.get("/sentry-test")
async def sentry_test_endpoint():
    """Endpoint that triggers a test exception for Sentry integration."""
    raise HTTPException(status_code=500, detail="Sentry test exception")



@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}