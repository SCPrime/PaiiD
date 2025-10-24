"""Health check endpoints used by monitoring and observability tools."""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import require_bearer
from app.services.health_monitor import health_monitor

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> Dict[str, Any]:
    """Return a lightweight health payload for external uptime monitors."""

    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@router.get("/detailed", dependencies=[Depends(require_bearer)])
async def detailed_health() -> Dict[str, Any]:
    """Return detailed system health metrics. Protected with bearer auth."""

    return health_monitor.get_system_health()


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Report application readiness for load balancers without requiring auth."""

    details: Dict[str, Any] = {"status": "unknown", "dependencies": {}}

    try:
        health = health_monitor.get_system_health()
        details = {
            "status": health.get("status", "unknown"),
            "timestamp": health.get("timestamp"),
            "dependencies": health.get("dependencies", {}),
        }
    except Exception as exc:  # pragma: no cover - defensive guard
        details["note"] = f"health monitor unavailable: {exc}"  # fall back to safe default

    return {"ready": True, "details": details}


@router.get("/sentry-test")
async def sentry_test_endpoint() -> Dict[str, Any]:
    """Endpoint used to verify Sentry reporting without requiring auth."""

    raise HTTPException(status_code=500, detail="Intentional error for Sentry testing")


@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """Basic liveness probe for orchestrators. Publicly accessible."""

    return {"alive": True}
