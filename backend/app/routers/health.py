"""
Enhanced health check endpoints with metrics
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.jwt import get_current_user
from app.models.database import User
from app.services.health_monitor import health_monitor


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check - public"""
    return {"status": "ok", "time": datetime.now().isoformat()}


@router.get("/detailed")
async def detailed_health(current_user: User = Depends(get_current_user)):
    """Detailed health metrics - requires auth"""
    return health_monitor.get_system_health()


@router.get("/readiness")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    health = health_monitor.get_system_health()

    if health["status"] == "healthy":
        return {"ready": True}
    else:
        raise HTTPException(
            status_code=503, detail={"ready": False, "reason": "System degraded"}
        )


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}


@router.get("/ready")
async def ready_check():
    """Kubernetes-style readiness probe - alias for readiness"""
    health = health_monitor.get_system_health()

    if health["status"] == "healthy":
        return {"ready": True}
    else:
        raise HTTPException(
            status_code=503, detail={"ready": False, "reason": "System degraded"}
        )


@router.get("/sentry-test")
async def sentry_test():
    """Test endpoint that raises an exception for Sentry testing"""
    raise Exception("SENTRY TEST - This is an intentional test exception")
