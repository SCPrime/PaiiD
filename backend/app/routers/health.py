from datetime import datetime, timezone
from time import perf_counter

import sentry_sdk
from fastapi import APIRouter, HTTPException

from ..core.idempotency import get_redis

router = APIRouter()


@router.get("/health")
def health():
    info = {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # Check Redis connection
    r = get_redis()
    if r:
        t0 = perf_counter()
        try:
            r.ping()
            ms = int((perf_counter() - t0) * 1000)
            info["redis"] = {"connected": True, "latency_ms": ms}
        except Exception:
            info["redis"] = {"connected": False}
    else:
        info["redis"] = {"connected": False}

    # Include startup performance metrics
    try:
        from ..core.startup_monitor import get_startup_monitor

        startup_metrics = get_startup_monitor().get_metrics()
        info["startup"] = startup_metrics
    except Exception:
        pass  # Startup monitor not initialized yet

    return info


@router.get("/ready")
def ready():
    return {"ready": True}


@router.get("/sentry-test")
def sentry_test():
    """
    Test endpoint to verify Sentry error tracking is working.

    This endpoint intentionally raises a Python exception to test Sentry integration.
    Visit: https://paiid-backend.onrender.com/api/sentry-test

    Expected: Error appears in Sentry dashboard within 30 seconds.
    """
    # First, send a test message to Sentry
    sentry_sdk.capture_message(
        "🧪 SENTRY TEST: Test message sent from /api/sentry-test", level="info"
    )

    # Then, raise an unhandled exception (guaranteed to be captured)
    raise Exception(
        "🧪 SENTRY TEST: This is an intentional error to verify error tracking is working! If you see this in Sentry, error tracking is operational."
    )
