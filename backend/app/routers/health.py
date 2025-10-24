"""Health and readiness endpoints for the PaiiD backend."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, object]:
    """Basic liveness endpoint exposed publicly."""

    now = datetime.utcnow().isoformat()
    return {
        "status": "ok",
        "time": now,
        "timestamp": now,
    }


@router.get("/health/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health() -> dict[str, object]:
    """Detailed health metrics that require authentication."""

    return health_monitor.get_system_health()


def _evaluate_readiness() -> tuple[bool, dict[str, object]]:
    """Determine whether the service is ready to serve traffic."""

    system_health = health_monitor.get_system_health()
    ready = system_health.get("status") == "healthy"
    details = {
        "ready": ready,
        "details": system_health,
    }
    return ready, details


@router.get("/ready")
async def readiness_check() -> dict[str, object]:
    """Readiness probe used by orchestrators and integration tests."""

    ready, details = _evaluate_readiness()
    if not ready:
        raise HTTPException(status_code=503, detail=details)
    return {"ready": True}


@router.get("/health/readiness")
async def readiness_probe() -> dict[str, object]:
    """Legacy readiness endpoint retained for backward compatibility."""

    ready, details = _evaluate_readiness()
    if not ready:
        raise HTTPException(status_code=503, detail=details)
    return {"ready": True}


@router.get("/health/liveness")
async def liveness_check() -> dict[str, object]:
    """Legacy liveness endpoint reporting basic availability."""

    return {"alive": True}


@router.get("/sentry-test")
async def sentry_test_endpoint() -> None:
    """Endpoint that intentionally raises for Sentry integration tests."""

    raise RuntimeError("SENTRY TEST: intentional exception for monitoring validation")
