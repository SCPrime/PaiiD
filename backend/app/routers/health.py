from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from time import perf_counter
from ..core.idempotency import get_redis
import sentry_sdk

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

    return info

@router.get("/ready")
def ready():
    return {"ready": True}


@router.get("/sentry-test")
def sentry_test():
    """
    Test endpoint to verify Sentry error tracking is working

    This endpoint intentionally raises an error to test Sentry integration.
    Only use in development/staging environments.
    """
    sentry_sdk.capture_message("Sentry test message", level="info")

    # Raise a test exception
    raise HTTPException(
        status_code=500,
        detail="This is a test error to verify Sentry integration is working"
    )