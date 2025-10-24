"""Health check endpoints for readiness, liveness, and monitoring validation."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from ..core.jwt import get_current_user
from ..services.health_monitor import health_monitor

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check that remains unauthenticated."""
    current_time = datetime.now().isoformat()
    return {
        "status": "ok",
        "timestamp": current_time,
        "time": current_time,
    }


@router.get("/health/detailed", dependencies=[Depends(get_current_user)])
async def detailed_health() -> dict:
    """Detailed health metrics that require authentication."""
    return health_monitor.get_system_health()


@router.get("/ready")
@router.get("/health/readiness")
async def readiness_check() -> dict[str, bool]:
    """Kubernetes-style readiness probe."""
    health = health_monitor.get_system_health()

    if health["status"] == "healthy":
        return {"ready": True}

    raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})


@router.get("/health/liveness")
@router.get("/liveness")
async def liveness_check() -> dict[str, bool]:
    """Kubernetes-style liveness probe."""
    return {"alive": True}


@router.get("/sentry-test")
async def sentry_test() -> None:
    """Endpoint that intentionally raises an error to validate Sentry reporting."""
    raise RuntimeError("SENTRY TEST - intentional exception for monitoring")
