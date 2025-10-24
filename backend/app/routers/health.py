"""Health check endpoints exposed under /api/health."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> dict[str, str]:
    """Basic health check that is safe to call publicly."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health() -> dict:
    """Detailed health metrics (requires authentication)."""
    return health_monitor.get_system_health()


@router.get("/readiness")
async def readiness_check() -> dict[str, bool]:
    """Kubernetes-style readiness probe."""
    health = health_monitor.get_system_health()

    if health["status"] == "healthy":
        return {"ready": True}

    raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})


@router.get("/liveness")
async def liveness_check() -> dict[str, bool]:
    """Kubernetes-style liveness probe."""
    return {"alive": True}
