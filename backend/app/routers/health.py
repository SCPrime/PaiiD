"""
Enhanced health check endpoints with metrics
"""

import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from ..core.unified_auth import get_current_user_unified
from ..db.session import engine
from ..models.database import User
from ..services.cache import get_cache
from ..services.health_monitor import health_monitor
from ..services.tradier_stream import get_tradier_stream


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check - public"""
    try:
        return {"status": "ok", "time": datetime.now().isoformat()}
    except Exception as e:
        from ..core.config import logger
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed") from e


@router.get("/detailed")
async def detailed_health(current_user: User = Depends(get_current_user_unified)):
    """Detailed health metrics - requires auth"""
    try:
        return health_monitor.get_system_health()
    except Exception as e:
        from ..core.config import logger
        logger.error(f"Detailed health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Detailed health check failed") from e


@router.get("/readiness")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    try:
        health = health_monitor.get_system_health()

        if health["status"] == "healthy":
            return {"ready": True}
        else:
            raise HTTPException(
                status_code=503, detail={"ready": False, "reason": "System degraded"}
            )
    except HTTPException:
        raise
    except Exception as e:
        from ..core.config import logger
        logger.error(f"Readiness check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Readiness check failed") from e


@router.get("/liveness")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    try:
        return {"alive": True}
    except Exception as e:
        from ..core.config import logger
        logger.error(f"Liveness check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Liveness check failed") from e


@router.get("/ready")
async def ready_check():
    """Kubernetes-style readiness probe - alias for readiness"""
    try:
        health = health_monitor.get_system_health()

        if health["status"] == "healthy":
            return {"ready": True}
        else:
            raise HTTPException(
                status_code=503, detail={"ready": False, "reason": "System degraded"}
            )
    except HTTPException:
        raise
    except Exception as e:
        from ..core.config import logger
        logger.error(f"Ready check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Ready check failed") from e


@router.get("/ready/full")
async def ready_full_check():
    """Comprehensive readiness probe: DB, Redis, streaming, AI proxy."""
    checks: dict[str, dict] = {}

    # DB check
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
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
