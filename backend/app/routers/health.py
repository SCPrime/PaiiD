"""
Enhanced health check endpoints with metrics

Provides comprehensive health monitoring for PaiiD Trading Platform:
- Basic health check (always returns 200 if app is running)
- Detailed health check with dependency status
- Startup validation results endpoint
- Kubernetes-style readiness/liveness probes
"""

import os
from datetime import datetime, timezone
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from ..core.config import settings
from ..core.unified_auth import get_current_user_unified
from ..db.session import engine
from ..models.database import User
from ..services.cache import get_cache
from ..services.health_monitor import health_monitor
from ..services.tradier_stream import get_tradier_stream


router = APIRouter(prefix="/health", tags=["health"])

# Store app start time for uptime calculation
APP_START_TIME = datetime.now(timezone.utc)


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str
    time: str


class DependencyStatus(BaseModel):
    """Status of a single dependency."""
    status: str  # "healthy", "degraded", "unavailable"
    latency_ms: Optional[float] = None
    message: Optional[str] = None


class DetailedHealthResponse(BaseModel):
    """Detailed health check with dependency status."""
    status: str
    time: str
    uptime_seconds: float
    dependencies: Dict[str, DependencyStatus]
    version: str = "1.0.0"


@router.get("", response_model=HealthResponse)
async def health_check():
    """Basic health check - always returns 200 if app is running."""
    try:
        return HealthResponse(
            status="ok",
            time=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Health check failed") from e


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Detailed health check with dependency status.

    Returns status of:
    - Tradier API
    - Alpaca API
    - Database (if configured)
    - Cache (if configured)
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        dependencies = {}

        # Check Tradier API
        dependencies["tradier_api"] = await _check_tradier()

        # Check Alpaca API
        dependencies["alpaca_api"] = await _check_alpaca()

        # Check Database
        dependencies["database"] = await _check_database()

        # Check Redis Cache
        dependencies["cache"] = await _check_cache()

        # Determine overall status
        all_healthy = all(
            dep.status == "healthy" for dep in dependencies.values()
        )
        any_degraded = any(
            dep.status == "degraded" for dep in dependencies.values()
        )

        overall_status = "healthy" if all_healthy else ("degraded" if any_degraded else "unavailable")

        uptime = (datetime.now(timezone.utc) - APP_START_TIME).total_seconds()

        return DetailedHealthResponse(
            status=overall_status,
            time=datetime.now(timezone.utc).isoformat(),
            uptime_seconds=uptime,
            dependencies=dependencies
        )
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Detailed health check failed") from e


@router.get("/startup")
async def startup_health_check():
    """
    Startup health check - returns validation results.
    Used by orchestrators to verify startup validation passed.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from ..core.startup_validator import StartupValidator

        validator = StartupValidator()
        passed = validator.validate_all()

        if not passed:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "failed",
                    "errors": validator.errors,
                    "warnings": validator.warnings,
                    "validations": validator.validations
                }
            )

        return {
            "status": "passed",
            "validations": validator.validations,
            "warnings": validator.warnings
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Startup health check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Startup health check failed") from e


@router.get("/readiness")
async def readiness_check():
    """
    Kubernetes-style readiness check.
    Returns 200 if app is ready to serve traffic, 503 otherwise.
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Check critical dependencies
        tradier_status = await _check_tradier()
        alpaca_status = await _check_alpaca()

        if tradier_status.status == "unavailable" or alpaca_status.status == "unavailable":
            raise HTTPException(
                status_code=503,
                detail="Application not ready - dependencies unavailable"
            )

        return {"status": "ready"}
    except HTTPException:
        raise
    except Exception as e:
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


# Helper functions for dependency health checks
async def _check_tradier() -> DependencyStatus:
    """Check Tradier API health."""
    try:
        start_time = datetime.now(timezone.utc)

        url = f"{settings.TRADIER_API_BASE_URL}/markets/quotes?symbols=SPY"
        headers = {
            "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)

        latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        if response.status_code == 200:
            return DependencyStatus(
                status="healthy",
                latency_ms=latency,
                message=f"Tradier API responding ({latency:.0f}ms)"
            )
        elif response.status_code == 401:
            return DependencyStatus(
                status="unavailable",
                latency_ms=latency,
                message="Authentication failed"
            )
        else:
            return DependencyStatus(
                status="degraded",
                latency_ms=latency,
                message=f"HTTP {response.status_code}"
            )

    except Exception as e:
        return DependencyStatus(
            status="unavailable",
            message=str(e)
        )


async def _check_alpaca() -> DependencyStatus:
    """Check Alpaca API health."""
    try:
        from alpaca.trading.client import TradingClient

        start_time = datetime.now(timezone.utc)

        client = TradingClient(
            settings.ALPACA_API_KEY,
            settings.ALPACA_SECRET_KEY,
            paper=True
        )

        account = client.get_account()

        latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return DependencyStatus(
            status="healthy",
            latency_ms=latency,
            message=f"Alpaca API responding ({latency:.0f}ms)"
        )

    except Exception as e:
        return DependencyStatus(
            status="unavailable",
            message=str(e)
        )


async def _check_database() -> DependencyStatus:
    """Check database connection."""
    try:
        start_time = datetime.now(timezone.utc)

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        return DependencyStatus(
            status="healthy",
            latency_ms=latency,
            message=f"Database responding ({latency:.0f}ms)"
        )

    except Exception as e:
        return DependencyStatus(
            status="unavailable",
            message=str(e)
        )


async def _check_cache() -> DependencyStatus:
    """Check Redis cache status."""
    try:
        cache = get_cache()

        if cache.available:
            return DependencyStatus(
                status="healthy",
                message="Redis cache available"
            )
        else:
            return DependencyStatus(
                status="degraded",
                message="Using in-memory fallback"
            )

    except Exception as e:
        return DependencyStatus(
            status="unavailable",
            message=str(e)
        )
