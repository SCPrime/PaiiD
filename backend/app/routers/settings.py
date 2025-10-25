from ..core.config import settings
from ..core.jwt import get_current_user
from ..core.startup_monitor import get_startup_monitor
from ..models.database import User
from datetime import UTC, datetime
from fastapi import APIRouter, Depends
import os
import sys

router = APIRouter()

_settings = {
    "stop_loss": 2.0,
    "take_profit": 5.0,
    "position_size": 1000,
    "max_positions": 10,
}

@router.get("/settings")
def get_settings():
    return _settings

@router.post("/settings")
def set_settings(payload: dict, current_user: User = Depends(get_current_user)):
    _settings.update({k: float(payload.get(k, v)) for k, v in _settings.items()})
    return _settings

@router.get("/config")
def get_config(current_user: User = Depends(get_current_user)):
    """
    Get safe configuration state for debugging production issues.
    Returns no secrets, only configuration status.
    """
    monitor = get_startup_monitor()
    startup_metrics = monitor.get_metrics()

    # Get external service health from prelaunch validator
    try:
        # Note: We don't run full validation here, just get the structure
        external_services_status = "unknown"  # Would need async context to check
    except Exception:
        external_services_status = "validation_error"

    return {
        "environment": {
            "sentry_environment": settings.SENTRY_ENVIRONMENT,
            "log_level": settings.LOG_LEVEL,
            "python_version": sys.version,
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "os": os.name,
            "port": os.getenv("PORT", "8001"),
        },
        "feature_flags": {
            "use_test_fixtures": settings.USE_TEST_FIXTURES,
            "live_trading": settings.LIVE_TRADING,
            "testing": settings.TESTING,
        },
        "services": {
            "sentry_configured": bool(settings.SENTRY_DSN),
            "redis_configured": bool(settings.REDIS_URL),
            "database_configured": bool(settings.DATABASE_URL),
            "external_services": external_services_status,
        },
        "startup_metrics": startup_metrics,
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
    }
