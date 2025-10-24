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
    current_time = datetime.now().isoformat()
    return {
        "status": "ok",
        "timestamp": current_time,
        "time": current_time,
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