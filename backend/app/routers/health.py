"""Enhanced health check endpoints with metrics."""
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.core.time_utils import utc_now_isoformat
from app.services.health_monitor import health_monitor

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check - public"""
    current_time = utc_now_isoformat()
    # Maintain backwards compatibility with existing clients expecting a
    # ``time`` field while also exposing the more explicit ``timestamp`` key.
    return {"status": "ok", "time": current_time, "timestamp": current_time}


@router.get("/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health():
    """Detailed health metrics - requires auth"""
    return health_monitor.get_system_health()


def _evaluate_readiness() -> bool:
    health = health_monitor.get_system_health()
    return health.get("status") == "healthy"


@router.get("/ready")
async def ready_check():
    """Legacy readiness endpoint used by tests and monitoring."""
    if _evaluate_readiness():
        return {"ready": True}
    raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})


@router.get("/readiness")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    if _evaluate_readiness():
        return {"ready": True}
    raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}


@router.get("/sentry-test")
async def sentry_test():
    """Endpoint used to verify Sentry captures server errors."""
    raise HTTPException(status_code=500, detail="Intentional error for Sentry testing")
