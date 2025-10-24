"""FastAPI router providing public and authenticated health endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor


router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Basic service health")
async def health_check() -> dict[str, str]:
    """Return a simple status payload for uptime monitoring."""

    now = datetime.utcnow().isoformat()
    return {"status": "ok", "timestamp": now, "time": now}


@router.get("/ready", summary="Readiness probe")
async def readiness_check() -> dict[str, bool]:
    """Expose readiness information for orchestrators such as Kubernetes."""

    health = health_monitor.get_system_health()
    if health.get("status") == "healthy":
        return {"ready": True}

    raise HTTPException(status_code=503, detail={"ready": False, "reason": "System degraded"})


@router.get("/sentry-test", summary="Sentry verification endpoint")
async def sentry_test_endpoint() -> None:
    """Trigger an exception so Sentry reporting can be verified."""

    raise HTTPException(status_code=500, detail="Intentional Sentry test error")


@router.get("/detailed", dependencies=[Depends(require_bearer)], summary="Detailed health")
async def detailed_health() -> dict[str, object]:
    """Return full system metrics; requires authentication."""

    return health_monitor.get_system_health()


@router.get("/live", summary="Liveness probe")
async def liveness_check() -> dict[str, bool]:
    """Used by load balancers to ensure the service process is running."""

    return {"alive": True}

