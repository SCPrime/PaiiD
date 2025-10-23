"""Enhanced health check endpoints with metrics."""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.jwt import get_current_user
from app.models.database import User
from app.routers.error_utils import log_and_sanitize_exceptions
from app.services.health_monitor import health_monitor


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check - public"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/detailed")
@log_and_sanitize_exceptions(
    logger,
    public_message="Failed to fetch detailed health status",
    log_message="Unable to fetch detailed health status",
)
async def detailed_health(_current_user: User = Depends(get_current_user)):
    """Detailed health metrics - requires auth"""
    return health_monitor.get_system_health()


@router.get("/readiness")
@log_and_sanitize_exceptions(
    logger,
    public_message="Readiness probe failed",
    log_message="Readiness probe failed",
)
async def readiness_check():
    """Kubernetes-style readiness probe"""
    health = health_monitor.get_system_health()

    if health["status"] == "healthy":
        return {"ready": True}
    else:
        raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})



@router.get("/liveness")
@log_and_sanitize_exceptions(
    logger,
    public_message="Liveness probe failed",
    log_message="Liveness probe failed",
)
async def liveness_check():
    """Kubernetes-style liveness probe"""
    return {"alive": True}
