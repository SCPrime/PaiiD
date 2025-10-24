import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv


# Load .env file before importing settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("\n===== BACKEND STARTUP =====")
print(f".env path: {env_path}")
print(f".env exists: {env_path.exists()}")
print("API_TOKEN from env: " + ("***" if os.getenv("API_TOKEN") else "NOT_SET"))
print(
    "TRADIER_API_KEY configured: " + ("YES" if os.getenv("TRADIER_API_KEY") else "NO")
)
print("Deployed from: main branch - Tradier integration active")
print("===========================\n", flush=True)


import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from slowapi.errors import RateLimitExceeded

from .core.config import settings
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
    print("[OK] Sentry error tracking initialized", flush=True)
else:
    print("[WARNING] SENTRY_DSN not configured - error tracking disabled", flush=True)

print("\n===== SETTINGS LOADED =====")
print(f"settings.API_TOKEN: {'***' if settings.API_TOKEN else 'NOT_SET'}")
print("===========================\n", flush=True)

# Register signal handlers for graceful shutdown BEFORE creating app
from .core.signals import setup_shutdown_handlers


setup_shutdown_handlers()

app = FastAPI(
    title="PaiiD Trading API",
    description="Personal Artificial Intelligence Investment Dashboard",
    version="1.0.0",
)

# Add Request ID middleware early for correlation
from .middleware.kill_switch import KillSwitchMiddleware
from .middleware.request_id import RequestIDMiddleware


app.add_middleware(RequestIDMiddleware)
app.add_middleware(KillSwitchMiddleware)

# Configure rate limiting (Phase 3: Bulletproof Reliability)
# Skip rate limiting in test environment to avoid middleware conflicts with TestClient
if not settings.TESTING:
    from .middleware.rate_limit import custom_rate_limit_exceeded_handler, limiter

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)
    print("[OK] Rate limiting enabled", flush=True)
else:
    print("[TEST MODE] Rate limiting disabled for tests", flush=True)


# Initialize scheduler, cache, and streaming on startup
@app.on_event("startup")
async def startup_event():
    # Skip startup initialization in test environment
    # Tests manage their own fixtures and don't need external service connections
    if settings.TESTING:
        print("[TEST MODE] Skipping startup event initialization", flush=True)
        return

    import logging
    from datetime import datetime

    from .core.prelaunch import PrelaunchValidator
    from .core.startup_monitor import get_startup_monitor

    # Configure structured logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Enhanced startup logging with comprehensive telemetry
    logger.info("=" * 70)
    logger.info(f"🚀 Backend startup initiated at {datetime.utcnow().isoformat()}")
    logger.info(f"   Environment: {settings.SENTRY_ENVIRONMENT}")
    logger.info(f"   Port: {os.getenv('PORT', '8001')}")
    logger.info(f"   Hostname: {os.getenv('HOSTNAME', 'unknown')}")
    logger.info(f"   Python Version: {sys.version}")
    logger.info(f"   OS: {os.name} - {os.getenv('OS', 'unknown')}")
    logger.info(
        f"   Sentry DSN: {'✅ Configured' if settings.SENTRY_DSN else '❌ Missing'}"
    )
    logger.info(
        f"   Test Fixtures: {'✅ Enabled' if settings.USE_TEST_FIXTURES else '❌ Disabled'}"
    )
    logger.info(
        f"   Live Trading: {'✅ Enabled' if settings.LIVE_TRADING else '❌ Disabled'}"
    )
    logger.info(f"   Log Level: {settings.LOG_LEVEL}")
    logger.info(
        f"   Redis URL: {'✅ Configured' if settings.REDIS_URL else '❌ Missing (in-memory fallback)'}"
    )
    logger.info(
        f"   Database URL: {'✅ Configured' if settings.DATABASE_URL else '❌ Missing'}"
    )

    # Log key package versions
    try:
        import fastapi
        import sentry_sdk
        import uvicorn

        logger.info(f"   FastAPI: {fastapi.__version__}")
        logger.info(f"   Uvicorn: {uvicorn.__version__}")
        logger.info(f"   Sentry SDK: {sentry_sdk.VERSION}")
    except Exception as e:
        logger.warning(f"   Package version check failed: {e}")

    # Log environment variable states (redacted secrets)
    env_vars = {
        "API_TOKEN": "***" if settings.API_TOKEN else "NOT_SET",
        "TRADIER_API_KEY": "***" if settings.TRADIER_API_KEY else "NOT_SET",
        "ALPACA_API_KEY": "***" if settings.ALPACA_API_KEY else "NOT_SET",
        "ANTHROPIC_API_KEY": "***" if settings.ANTHROPIC_API_KEY else "NOT_SET",
        "SENTRY_DSN": "***" if settings.SENTRY_DSN else "NOT_SET",
        "REDIS_URL": "***" if settings.REDIS_URL else "NOT_SET",
        "DATABASE_URL": "***" if settings.DATABASE_URL else "NOT_SET",
        "USE_TEST_FIXTURES": str(settings.USE_TEST_FIXTURES),
        "LIVE_TRADING": str(settings.LIVE_TRADING),
        "TESTING": str(settings.TESTING),
        "LOG_LEVEL": settings.LOG_LEVEL,
        "SENTRY_ENVIRONMENT": settings.SENTRY_ENVIRONMENT,
    }

    logger.info("   Environment Variables:")
    for key, value in env_vars.items():
        logger.info(f"     {key}: {value}")

    logger.info("=" * 70)

    monitor = get_startup_monitor()
    monitor.start()

    # Run pre-launch validation
    try:
        async with monitor.phase("prelaunch_validation", timeout=10.0):
            validator = PrelaunchValidator(strict_mode=True)
            success, errors, warnings = await validator.validate_all()

            if not success:
                logger.error("🚨 Pre-launch validation failed!")
                for error in errors:
                    logger.error(f"   • {error}")
                raise RuntimeError(f"Pre-launch validation failed: {errors}")
            else:
                logger.info("✅ Pre-launch validation passed")
    except Exception as e:
        logger.error(f"❌ Pre-launch validation error: {e}")
        raise

    # Verify database connectivity early
    try:
        async with monitor.phase("database_check", timeout=5.0):
            from sqlalchemy import text

            from .db.session import engine

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("[OK] Database connection verified")
    except Exception as e:
        logger.error(f"[DB] Connection failed: {e}")
        raise

    # Initialize cache service
    try:
        async with monitor.phase("cache_init", timeout=5.0):
            from .services.cache import init_cache

            init_cache()
    except Exception as e:
        print(f"[ERROR] Failed to initialize cache: {e!s}", flush=True)

    # Initialize scheduler
    try:
        async with monitor.phase("scheduler_init", timeout=5.0):
            scheduler_instance = init_scheduler()
            print("[OK] Scheduler initialized and started", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to initialize scheduler: {e!s}", flush=True)

    # ⚠️ ARCHITECTURE NOTE: Tradier provides ALL market data (quotes, streaming, analysis)
    # Alpaca is used ONLY for paper trade execution (orders, positions, account)
    # Future: Tradier will also handle live trading post-MVP
    print(
        "[INFO] Market data: Tradier API | Trade execution: Alpaca Paper Trading",
        flush=True,
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
                print(
                    "[INFO] Queued subscription to $DJI and COMP (will connect when circuit breaker clears)",
                    flush=True,
                )
    except Exception as e:
        print(
            f"[WARNING] Tradier stream startup failed (non-blocking): {e}", flush=True
        )
        print(
            "[INFO] Application will continue - streaming will retry automatically",
            flush=True,
        )

    # Finish monitoring and log summary
    monitor.finish()

    # Log startup completion with duration
    startup_duration = (
        time.time() - monitor.start_time if hasattr(monitor, "start_time") else 0
    )
    logger.info("=" * 70)
    logger.info(f"✅ Backend startup completed successfully in {startup_duration:.2f}s")
    logger.info("   All systems operational")
    logger.info("   Ready to accept requests")
    logger.info("=" * 70)


# Shutdown scheduler and streaming gracefully
@app.on_event("shutdown")
async def shutdown_event():
    """
    Enhanced shutdown handler with PID file cleanup and metrics logging
    Timeout: Max 30 seconds for graceful shutdown
    """
    # Skip shutdown in test environment
    if settings.TESTING:
        print("[TEST MODE] Skipping shutdown event", flush=True)
        return

    import time
    from pathlib import Path

    shutdown_start = time.time()
    import logging

    logger = logging.getLogger(__name__)

    logger.info("=" * 70)
    logger.info("FastAPI shutdown event triggered")
    logger.info("=" * 70)

    # Shutdown scheduler
    try:
        from .scheduler import get_scheduler

        scheduler_instance = get_scheduler()
        scheduler_instance.shutdown(wait=False)  # Don't wait indefinitely
        logger.info("[OK] Scheduler shut down gracefully")
    except Exception as e:
        logger.error(f"[ERROR] Scheduler shutdown error: {e!s}")

    # Stop Tradier streaming
    try:
        from .services.tradier_stream import stop_tradier_stream

        await stop_tradier_stream()
        logger.info("[OK] Tradier stream stopped")
    except Exception as e:
        logger.error(f"[ERROR] Tradier shutdown error: {e}")

    # Remove PID file
    try:
        project_root = Path(__file__).parent.parent.parent
        pid_file = project_root / "backend" / ".run" / "backend-server.pid"

        if pid_file.exists():
            pid_content = pid_file.read_text().strip()
            pid_file.unlink()
            logger.info(f"[OK] Removed PID file (PID: {pid_content})")
        else:
            logger.info("[INFO] No PID file found to remove")
    except Exception as e:
        logger.error(f"[ERROR] PID file removal error: {e}")

    # Log shutdown metrics
    shutdown_duration = time.time() - shutdown_start
    logger.info(f"[METRICS] Shutdown duration: {shutdown_duration:.2f}s")

    logger.info("=" * 70)
    logger.info("Shutdown complete")
    logger.info("=" * 70)


# Add Sentry context middleware if Sentry is enabled
if settings.SENTRY_DSN:
    from .middleware.sentry import SentryContextMiddleware

    app.add_middleware(SentryContextMiddleware)

# Add Cache-Control headers for SWR support (Phase 2: Performance)
from .middleware.cache_control import CacheControlMiddleware
from .middleware.metrics import metrics_middleware
from .middleware.security_headers import SecurityHeadersMiddleware


app.add_middleware(CacheControlMiddleware)
app.middleware("http")(metrics_middleware)
app.add_middleware(SecurityHeadersMiddleware)

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
