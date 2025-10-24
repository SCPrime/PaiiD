"""
Enhanced health check endpoints with metrics
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check - public"""
    return {
        "status": "ok",
        "time": datetime.now().isoformat()
    }


@router.get("/health/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health():
    """Detailed health metrics - requires auth"""
    return health_monitor.get_system_health()


@router.get("/ready")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    health = health_monitor.get_system_health()

    if health["status"] == "healthy":
        return {"ready": True}
    else:
        raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})



@router.get("/health/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}


@router.get("/sentry-test")
async def sentry_test():
    """Endpoint that intentionally raises an error to test Sentry wiring."""
    raise RuntimeError("SENTRY TEST EXCEPTION: verifying Sentry pipeline")