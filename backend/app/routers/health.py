"""
Enhanced health check endpoints with metrics
"""

import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.unified_auth import get_current_user_unified
from app.db.session import engine
from app.models.database import User
from app.services.cache import get_cache
from app.services.health_monitor import health_monitor
from app.services.tradier_stream import get_tradier_stream


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check - public"""
    return {"status": "ok", "time": datetime.now().isoformat()}


@router.get("/detailed")
async def detailed_health(current_user: User = Depends(get_current_user_unified)):
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


@router.get("/ready/full")
async def ready_full_check():
    """Comprehensive readiness probe: DB, Redis, streaming, AI proxy."""
    checks: dict[str, dict] = {}

    # DB check
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        checks["database"] = {"status": "up"}
    except Exception as e:
        checks["database"] = {"status": "down", "error": str(e)}

    # Redis check
    cache = get_cache()
    checks["redis"] = {"status": "up" if cache.available else "down"}

    # Streaming service check
    stream = get_tradier_stream()
    checks["streaming"] = {
        "status": "up" if stream.is_running() else "down",
        "active_symbols": len(stream.get_active_symbols()),
    }

    # Anthropic API config check
    checks["anthropic"] = {
        "status": "up" if os.getenv("ANTHROPIC_API_KEY") else "unconfigured"
    }

    # Aggregate status
    overall = "up"
    for v in checks.values():
        if v.get("status") in ("down", "unconfigured"):
            overall = "degraded"
            break

    return {"status": overall, "checks": checks, "time": datetime.now().isoformat()}


@router.get("/sentry-test")
async def sentry_test():
    """Test endpoint that raises an exception for Sentry testing"""
    raise Exception("SENTRY TEST - This is an intentional test exception")
