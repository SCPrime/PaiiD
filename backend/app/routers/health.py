"""Health check endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor


def _current_timestamp() -> str:
    """Return a UTC timestamp string used by health endpoints."""
    return datetime.now(timezone.utc).isoformat()


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check - public."""
    return {"status": "ok", "time": _current_timestamp()}


@router.get("/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health():
    """Detailed health metrics - requires auth."""
    return health_monitor.get_system_health()


@router.get("/ready")
async def readiness_check():
    """Lightweight readiness probe."""
    health = health_monitor.get_system_health()
    if health.get("status") == "healthy":
        return {"ready": True, "time": _current_timestamp()}
    raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})


@router.get("/sentry-test")
async def sentry_test():
    """Endpoint used to validate Sentry reporting."""
    raise RuntimeError("Intentional Sentry test error")


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe."""
    return {"alive": True, "time": _current_timestamp()}
