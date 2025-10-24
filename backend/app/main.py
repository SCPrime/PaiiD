import logging
import os
from pathlib import Path

from dotenv import load_dotenv


# Load .env file before importing settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from .core.config import settings
from .core.observability import (
    configure_logging,
    init_datadog,
    init_sentry,
    verify_error_ingestion,
    wrap_with_new_relic,
)


configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger("paiid.main")

logger.info(
    "Backend startup",
    extra={
        "event": "backend_startup",
        "env_file": str(env_path),
        "env_file_exists": env_path.exists(),
        "app_env": settings.APP_ENV,
        "tradier_api_key_configured": bool(os.getenv("TRADIER_API_KEY")),
    },
)

lifecycle_logger = logging.getLogger("paiid.lifecycle")

init_datadog(settings)
init_sentry(settings)
verify_error_ingestion(settings)


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from .routers import (
    ai,
    analytics,
    auth,
    backtesting,
    claude,
    health,
    market,
    market_data,
    news,
    options,
    orders,
    portfolio,
    positions,
    proposals,
    scheduler,
    screening,
    stock,
    strategies,
    stream,
    telemetry,
    users,
)
from .routers import settings as settings_router
from .scheduler import init_scheduler
from .services.health_monitor import health_monitor

app = FastAPI(
    title="PaiiD Trading API",
    description="Personal Artificial Intelligence Investment Dashboard",
    version="1.0.0",
)

app = wrap_with_new_relic(app, settings)

logger.info(
    "Settings loaded",
    extra={
        "event": "settings_loaded",
        "api_token_configured": bool(settings.API_TOKEN and settings.API_TOKEN != "change-me"),
    },
)

# Configure rate limiting (Phase 3: Bulletproof Reliability)
# Skip rate limiting in test environment to avoid middleware conflicts with TestClient
if not settings.TESTING:
    from .middleware.rate_limit import custom_rate_limit_exceeded_handler, limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
    lifecycle_logger.info("Rate limiting enabled", extra={"event": "rate_limit_enabled"})
else:
    lifecycle_logger.info(
        "Rate limiting disabled for test environment",
        extra={"event": "rate_limit_disabled", "reason": "testing"},
    )


# Initialize scheduler, cache, and streaming on startup
@app.on_event("startup")
async def startup_event():
    from .core.startup_monitor import get_startup_monitor

    monitor = get_startup_monitor()
    monitor.start()

    # Initialize cache service
    try:
        async with monitor.phase("cache_init", timeout=5.0):
            from .services.cache import init_cache

            init_cache()
    except Exception as e:
        lifecycle_logger.exception(
            "Failed to initialize cache",
            extra={"event": "cache_initialization_failed"},
        )

    # Initialize scheduler
    try:
        async with monitor.phase("scheduler_init", timeout=5.0):
            scheduler_instance = init_scheduler()
            lifecycle_logger.info(
                "Scheduler initialized and started",
                extra={"event": "scheduler_started"},
            )
    except Exception as e:
        lifecycle_logger.exception(
            "Failed to initialize scheduler",
            extra={"event": "scheduler_initialization_failed"},
        )

    # ⚠️ ARCHITECTURE NOTE: Tradier provides ALL market data (quotes, streaming, analysis)
    # Alpaca is used ONLY for paper trade execution (orders, positions, account)
    # Future: Tradier will also handle live trading post-MVP
    lifecycle_logger.info(
        "Market data sourced from Tradier API; Alpaca used for paper trading",
        extra={"event": "market_data_overview"},
    )

    # Start Tradier streaming service (non-blocking background task)
    # The streaming service runs independently and should NOT block application startup
    # If circuit breaker is active, it will wait in the background without blocking HTTP requests
    try:
        async with monitor.phase("tradier_stream_init", timeout=10.0):
            from .services.tradier_stream import (
                get_tradier_stream,
                start_tradier_stream,
            )

            # Start returns immediately - WebSocket connection happens in background
            await start_tradier_stream()
            print(
                "[OK] Tradier streaming service started (running in background)",
                flush=True,
            )

            # Queue subscription request (non-blocking) - will be sent when WebSocket connects
            stream = get_tradier_stream()
            if stream:
                # Add symbols to active set - they'll be subscribed when WebSocket connects
                stream.active_symbols.update(["$DJI", "COMP:GIDS"])
                lifecycle_logger.info(
                    "Queued initial Tradier stream subscriptions",
                    extra={
                        "event": "tradier_stream_subscription_queued",
                        "symbols": ["$DJI", "COMP:GIDS"],
                    },
                )
    except Exception as e:
        lifecycle_logger.warning(
            "Tradier stream startup failed but will retry",
            extra={"event": "tradier_stream_start_failed", "error": str(e)},
        )

    # Finish monitoring and log summary
    monitor.finish()


# Shutdown scheduler and streaming gracefully
@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown scheduler
    try:
        from .scheduler import get_scheduler

        scheduler_instance = get_scheduler()
        scheduler_instance.shutdown()
        lifecycle_logger.info(
            "Scheduler shut down gracefully",
            extra={"event": "scheduler_shutdown"},
        )
    except Exception as e:
        lifecycle_logger.exception(
            "Scheduler shutdown error",
            extra={"event": "scheduler_shutdown_failed"},
        )

    # Stop Tradier streaming
    try:
        from .services.tradier_stream import stop_tradier_stream

        await stop_tradier_stream()
        lifecycle_logger.info(
            "Tradier stream stopped",
            extra={"event": "tradier_stream_shutdown"},
        )
    except Exception as e:
        lifecycle_logger.exception(
            "Tradier stream shutdown error",
            extra={"event": "tradier_stream_shutdown_failed"},
        )


# Add Sentry context middleware if Sentry is enabled
if settings.SENTRY_DSN:
    from .middleware.sentry import SentryContextMiddleware

    app.add_middleware(SentryContextMiddleware)

# Add Cache-Control headers for SWR support (Phase 2: Performance)
from .middleware.cache_control import CacheControlMiddleware
from .middleware.metrics import metrics_middleware


app.add_middleware(CacheControlMiddleware)
app.middleware("http")(metrics_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3003",  # Alternative dev server port
        "https://paiid-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router, prefix="/api")  # Authentication endpoints
app.include_router(settings_router.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(positions.router)  # Position management
app.include_router(stream.router, prefix="/api")
app.include_router(screening.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(market_data.router, prefix="/api", tags=["market-data"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(options.router, prefix="/api")  # Options Greeks calculator
app.include_router(proposals.router)  # Options trade proposals
app.include_router(ai.router, prefix="/api")
app.include_router(claude.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(backtesting.router, prefix="/api")
app.include_router(telemetry.router)


@app.get("/api/sentry-test", include_in_schema=False)
async def sentry_test_endpoint() -> None:
    """Trigger a synthetic exception for Sentry integration testing."""

    raise RuntimeError("SENTRY TEST: manual trigger")


@app.get("/api/ready", include_in_schema=False)
async def ready_endpoint() -> dict[str, bool | str]:
    """Readiness probe compatible with the legacy /api/ready contract."""

    system_health = health_monitor.get_system_health()
    if system_health.get("status") == "healthy":
        return {"ready": True}

    raise HTTPException(
        status_code=503,
        detail={"ready": False, "reason": system_health.get("status", "unknown")},
    )
