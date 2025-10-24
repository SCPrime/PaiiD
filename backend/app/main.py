import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# Load .env file before importing settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    stream=sys.stdout,
)

logger = logging.getLogger("paiid.main")


def _mask_secret(value: str | None) -> str:
    if not value:
        return "<unset>"
    return "****" if len(value) <= 4 else f"****{value[-4:]}"


logger.info("===== BACKEND STARTUP =====")
logger.info(".env path: %s (exists=%s)", env_path, env_path.exists())
logger.info(
    "Render deployment: %s",
    "yes" if os.getenv("RENDER_EXTERNAL_URL") else "no",
)
logger.info("API_TOKEN configured: %s", _mask_secret(os.getenv("API_TOKEN")))
logger.info(
    "TRADIER_API_KEY configured: %s",
    "yes" if os.getenv("TRADIER_API_KEY") else "no",
)
logger.info("Branch reference: main | Tradier integration active")


import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .core.prelaunch import PrelaunchError, run_prelaunch_checks
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


try:
    prelaunch_report = run_prelaunch_checks(
        emit_json=False,
        raise_on_error=True,
        context="uvicorn-import",
    )
    logger.info("Pre-launch checks status=%s", prelaunch_report["status"])
except PrelaunchError as exc:
    logger.critical("Pre-launch checks failed during import: %s", exc)
    raise
except Exception as exc:  # pragma: no cover - defensive guard
    logger.exception("Unexpected error running pre-launch checks: %s", exc)
    raise


# Initialize Sentry if DSN is configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        profiles_sample_rate=0.1,  # 10% profiling
        environment=(
            "production"
            if "render.com" in os.getenv("RENDER_EXTERNAL_URL", "")
            else "development"
        ),
        release="paiid-backend@1.0.0",
        send_default_pii=False,  # Don't send personally identifiable info
        before_send=lambda event, hint: (
            event
            if not event.get("request", {}).get("headers", {}).get("Authorization")
            else {
                **event,
                "request": {
                    **event.get("request", {}),
                    "headers": {
                        **event.get("request", {}).get("headers", {}),
                        "Authorization": "[REDACTED]",
                    },
                },
            }
        ),
    )
    logger.info("[Sentry] Error tracking initialized")
else:
    logger.warning("[Sentry] DSN not configured - error tracking disabled")

logger.info("===== SETTINGS LOADED =====")
logger.info("settings.API_TOKEN configured: %s", _mask_secret(settings.API_TOKEN))
logger.info("===========================")

app = FastAPI(
    title="PaiiD Trading API",
    description="Personal Artificial Intelligence Investment Dashboard",
    version="1.0.0",
)

# Configure rate limiting (Phase 3: Bulletproof Reliability)
# Skip rate limiting in test environment to avoid middleware conflicts with TestClient
if not settings.TESTING:
    from .middleware.rate_limit import custom_rate_limit_exceeded_handler, limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
    logger.info("[RateLimit] Enabled")
else:
    logger.info("[RateLimit] Test mode - disabled")


# Initialize scheduler, cache, and streaming on startup
@app.on_event("startup")
async def startup_event():
    from .core.startup_monitor import get_startup_monitor

    monitor = get_startup_monitor()
    monitor.start()

    startup_failures: list[tuple[str, str]] = []
    critical_failures: list[tuple[str, str]] = []
    metrics: dict | None = None

    try:
        # Initialize cache service
        try:
            async with monitor.phase("cache_init", timeout=5.0):
                from .services.cache import init_cache

                init_cache()
                logger.info("[startup][cache_init] Cache initialized")
        except Exception as exc:
            logger.exception("[startup][cache_init] Failed: %s", exc)
            startup_failures.append(("cache_init", str(exc)))
            critical_failures.append(("cache_init", str(exc)))

        # Initialize scheduler
        try:
            async with monitor.phase("scheduler_init", timeout=5.0):
                scheduler_instance = init_scheduler()
                logger.info(
                    "[startup][scheduler_init] Scheduler initialized", extra={"scheduler": str(scheduler_instance)}
                )
        except Exception as exc:
            logger.exception("[startup][scheduler_init] Failed: %s", exc)
            startup_failures.append(("scheduler_init", str(exc)))
            critical_failures.append(("scheduler_init", str(exc)))

        # ⚠️ ARCHITECTURE NOTE: Tradier provides ALL market data (quotes, streaming, analysis)
        # Alpaca is used ONLY for paper trade execution (orders, positions, account)
        # Future: Tradier will also handle live trading post-MVP
        logger.info(
            "[startup] Market data provider=Tradier API | Trade execution=Alpaca Paper Trading"
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
                logger.info(
                    "[startup][tradier_stream] Streaming service started (background)",
                )

                # Queue subscription request (non-blocking) - will be sent when WebSocket connects
                stream = get_tradier_stream()
                if stream:
                    stream.active_symbols.update(["$DJI", "COMP:GIDS"])
                    logger.info(
                        "[startup][tradier_stream] Subscription queued for $DJI and COMP",
                        extra={"symbols": list(stream.active_symbols)},
                    )
        except Exception as exc:
            logger.warning(
                "[startup][tradier_stream] Non-blocking failure: %s", exc, exc_info=True
            )
            startup_failures.append(("tradier_stream_init", str(exc)))
    finally:
        monitor.finish()
        metrics = monitor.get_metrics()

    summary_status = "ok"
    if critical_failures:
        summary_status = "failed"
    elif startup_failures:
        summary_status = "degraded"

    summary_payload = {
        "status": summary_status,
        "failures": startup_failures,
        "critical_failures": critical_failures,
        "metrics": metrics,
    }
    logger.info("[startup] summary %s", summary_payload)

    allow_degraded = os.getenv("ALLOW_DEGRADED_STARTUP", "false").lower() in {
        "1",
        "true",
        "yes",
    }

    if critical_failures and not allow_degraded:
        logger.error("[startup] Critical failures detected: %s", critical_failures)
        raise RuntimeError(
            "Critical startup steps failed: "
            + ", ".join(f"{name}: {reason}" for name, reason in critical_failures)
        )


# Shutdown scheduler and streaming gracefully
@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown scheduler
    try:
        from .scheduler import get_scheduler

        scheduler_instance = get_scheduler()
        scheduler_instance.shutdown()
        logger.info("[shutdown] Scheduler shut down gracefully")
    except Exception as e:
        logger.exception("[shutdown] Scheduler error: %s", e)

    # Stop Tradier streaming
    try:
        from .services.tradier_stream import stop_tradier_stream

        await stop_tradier_stream()
        logger.info("[shutdown] Tradier stream stopped")
    except Exception as e:
        logger.exception("[shutdown] Tradier stream error: %s", e)


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

app.include_router(health.router, prefix="/api")
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
