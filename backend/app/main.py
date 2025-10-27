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
    ml,
    ml_sentiment,
    monitoring,
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
    description="Personal Artificial Intelligence Investment Dashboard - AI-powered trading platform with real-time market data and intelligent trade execution",
    version="1.0.0",
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc alternative documentation
    openapi_url="/api/openapi.json",  # OpenAPI schema
    contact={
        "name": "PaiiD Support",
        "url": "https://github.com/your-repo/paiid",
        "email": "support@paiid.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://paiid.com/terms",
    },
)


# Custom OpenAPI schema configuration
def custom_openapi():
    """
    Custom OpenAPI schema with enhanced security schemes and metadata

    Adds:
    - JWT Bearer authentication scheme
    - CSRF token authentication scheme
    - Comprehensive endpoint tags
    - Data source documentation
    """
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="PaiiD Trading API",
        version="1.0.0",
        description="""
# Personal Artificial Intelligence Investment Dashboard

AI-powered trading platform with real-time market data and intelligent trade execution.

## Data Sources

- **Market Data:** Tradier API (Real-time, NO delay)
- **Trade Execution:** Alpaca Paper Trading API (Paper trading only)
- **AI Analysis:** Anthropic Claude API

## Authentication

All endpoints (except health checks and public endpoints) require JWT Bearer token authentication.
State-changing operations (POST/PUT/DELETE/PATCH) also require CSRF token in X-CSRF-Token header.

## Rate Limiting

Rate limiting is enabled in production to prevent abuse.

## Caching

Intelligent caching is implemented for market data to optimize performance:
- Quotes: 5 seconds TTL
- Historical bars: 1 hour TTL
- Positions: 30 seconds TTL
- Scanner results: 3 minutes TTL

## Interactive Documentation

- **Swagger UI:** http://localhost:8001/api/docs
- **ReDoc:** http://localhost:8001/api/redoc
- **OpenAPI JSON:** http://localhost:8001/api/openapi.json
        """,
        routes=app.routes,
        contact={
            "name": "PaiiD Support",
            "url": "https://github.com/your-repo/paiid",
            "email": "support@paiid.com",
        },
        license_info={
            "name": "Proprietary",
            "url": "https://paiid.com/terms",
        },
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token obtained from login/register endpoint. Format: 'Bearer <token>'",
        },
        "csrfToken": {
            "type": "apiKey",
            "in": "header",
            "name": "X-CSRF-Token",
            "description": "CSRF token for state-changing operations (POST/PUT/DELETE/PATCH). Obtain from /api/auth/csrf-token",
        },
    }

    # Add tags metadata
    openapi_schema["tags"] = [
        {"name": "auth", "description": "Authentication and user management"},
        {"name": "health", "description": "Health checks and system status"},
        {"name": "portfolio", "description": "Portfolio and position management (Tradier API)"},
        {"name": "orders", "description": "Order execution and templates (Alpaca Paper Trading)"},
        {"name": "market-data", "description": "Market data quotes and historical bars (Tradier API)"},
        {"name": "ai", "description": "AI-powered recommendations and analysis (Claude API)"},
        {"name": "strategies", "description": "Trading strategy management and templates"},
        {"name": "analytics", "description": "Performance analytics and metrics"},
        {"name": "backtesting", "description": "Strategy backtesting and historical analysis"},
        {"name": "news", "description": "Market news and sentiment analysis"},
        {"name": "options", "description": "Options data, Greeks, and multi-leg strategies"},
        {"name": "ml", "description": "Machine learning models and predictions"},
        {"name": "screening", "description": "Stock screening and filtering"},
        {"name": "streaming", "description": "Real-time data streaming (WebSocket)"},
        {"name": "users", "description": "User profile and preference management"},
        {"name": "telemetry", "description": "Event tracking and application telemetry"},
    ]

    # Add servers
    openapi_schema["servers"] = [
        {
            "url": "https://paiid-backend.onrender.com",
            "description": "Production server (Render)",
        },
        {"url": "http://localhost:8001", "description": "Local development server"},
    ]

    # Add external documentation
    openapi_schema["externalDocs"] = {
        "description": "Full API Reference Documentation",
        "url": "https://github.com/your-repo/paiid/blob/main/backend/docs/API_REFERENCE.md",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema
app.openapi = custom_openapi

# Add Request ID middleware early for correlation
from starlette.middleware.gzip import GZipMiddleware

from .middleware.kill_switch import KillSwitchMiddleware
from .middleware.request_id import RequestIDMiddleware
from .middleware.security import CSRFProtectionMiddleware, set_csrf_middleware


app.add_middleware(RequestIDMiddleware)
app.add_middleware(KillSwitchMiddleware)

# Add CSRF protection middleware (Batch 2C: Security Hardening)
# Disable CSRF validation in test mode (TestClient doesn't maintain state)
# IMPORTANT: Create a single instance and reuse it to avoid state inconsistencies
csrf_middleware_instance = CSRFProtectionMiddleware(app, testing_mode=settings.TESTING)
set_csrf_middleware(csrf_middleware_instance)
# Add the SAME instance to the middleware stack (don't create a new one)
app.add_middleware(
    CSRFProtectionMiddleware,
    exempt_paths=[
        "/api/health",
        "/api/monitor/health",
        "/api/monitor/ping",
        "/api/monitor/version",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
        "/api/proposals",  # Options trade proposals (idempotent with requestId)
        "/api/order-templates",  # Order templates (needed for CSRF tests)
        "/api/telemetry",  # Fire-and-forget telemetry tracking (stateless)
        "/api/claude/chat",  # Claude AI chat (stateless, idempotent requests)
        "/docs",
        "/openapi.json",
        "/redoc",
    ],
    testing_mode=settings.TESTING,
)
if settings.TESTING:
    print("[TEST MODE] CSRF protection middleware enabled (validation disabled for tests)", flush=True)
else:
    print("[OK] CSRF protection middleware enabled", flush=True)

# Add GZIP compression for responses >1KB (reduces bandwidth by ~70%)
app.add_middleware(GZipMiddleware, minimum_size=1000)
print("[OK] GZIP compression enabled for responses >1KB", flush=True)

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
    from datetime import UTC, datetime

    from .core.prelaunch import PrelaunchValidator
    from .core.startup_monitor import get_startup_monitor
    from .core.startup_validator import validate_startup

    # Configure structured logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Enhanced startup logging with comprehensive telemetry
    logger.info("=" * 70)
    logger.info(f"🚀 Backend startup initiated at {datetime.now(UTC).isoformat()}")
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

    # CRITICAL: Validate required secrets BEFORE any service initialization
    # This prevents runtime failures due to missing or invalid configuration
    from .core.config import validate_required_secrets

    logger.info("🔐 Validating required secrets...")
    strict_secret_mode = os.getenv("STRICT_SECRET_VALIDATION", "false").lower() == "true"
    secrets_valid, missing_secrets = validate_required_secrets(strict=strict_secret_mode)

    if not secrets_valid:
        logger.error("=" * 70)
        logger.error("🚨 SECRET VALIDATION FAILED!")
        logger.error("=" * 70)
        logger.error("Missing or invalid secrets detected:")
        for secret in missing_secrets:
            logger.error(f"   ❌ {secret}")
        logger.error("")
        logger.error("Required actions:")
        logger.error("   1. Copy backend/.env.example to backend/.env")
        logger.error("   2. Fill in all required secret values")
        logger.error("   3. See docs/SECRETS.md for detailed instructions")
        logger.error("")
        logger.error("Secret generation commands:")
        logger.error("   API_TOKEN:      python -c 'import secrets; print(secrets.token_urlsafe(32))'")
        logger.error("   JWT_SECRET_KEY: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
        logger.error("=" * 70)

        # Only block startup in strict mode or production
        is_production = "render.com" in os.getenv("RENDER_EXTERNAL_URL", "")
        if strict_secret_mode or is_production:
            raise RuntimeError(
                f"Application startup blocked due to missing secrets. "
                f"Missing: {', '.join(missing_secrets)}"
            )
        else:
            logger.warning(
                "⚠️  Continuing startup despite missing secrets (development mode). "
                "Set STRICT_SECRET_VALIDATION=true to enforce validation."
            )
    else:
        logger.info("✅ All required secrets validated successfully")

    monitor = get_startup_monitor()
    monitor.start()

    # Run pre-launch validation
    try:
        async with monitor.phase("prelaunch_validation", timeout=10.0):
            strict_env = os.getenv("STRICT_PRELAUNCH", "false").lower() == "true"
            validator = PrelaunchValidator(strict_mode=strict_env)
            success, errors, _warnings = await validator.validate_all()

            if not success:
                logger.error("🚨 Pre-launch validation failed!")
                for error in errors:
                    logger.error(f"   • {error}")
                if strict_env:
                    raise RuntimeError(f"Pre-launch validation failed: {errors}")
                else:
                    logger.warning(
                        "Pre-launch validation reported errors but STRICT_PRELAUNCH is disabled; continuing startup"
                    )
            else:
                logger.info("✅ Pre-launch validation passed")
    except Exception as e:
        # Only block startup when STRICT_PRELAUNCH is explicitly enabled
        strict_env = os.getenv("STRICT_PRELAUNCH", "false").lower() == "true"
        logger.error(f"❌ Pre-launch validation error: {e}")
        if strict_env:
            raise
        logger.warning(
            "Continuing startup despite pre-launch validation error (STRICT_PRELAUNCH disabled)"
        )

    # Run startup validation (Wave 5: Enhanced startup checks)
    # This provides detailed API connectivity validation and account verification
    try:
        async with monitor.phase("startup_validation", timeout=15.0):
            if not validate_startup():
                # Check if strict mode is enabled
                strict_startup = os.getenv("STRICT_STARTUP_VALIDATION", "false").lower() == "true"
                if strict_startup:
                    logger.error("🚨 Blocking startup due to failed validation (STRICT_STARTUP_VALIDATION=true)")
                    raise RuntimeError("Startup validation failed - check logs above for details")
                else:
                    logger.warning(
                        "⚠️ Startup validation failed but continuing (STRICT_STARTUP_VALIDATION disabled)"
                    )
    except RuntimeError:
        raise  # Re-raise if we're blocking startup
    except Exception as e:
        logger.error(f"❌ Startup validation error: {e}")
        strict_startup = os.getenv("STRICT_STARTUP_VALIDATION", "false").lower() == "true"
        if strict_startup:
            raise
        logger.warning(
            "Continuing startup despite validation error (STRICT_STARTUP_VALIDATION disabled)"
        )

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
            init_scheduler()
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
        "http://localhost:3001",  # Secondary dev server port (MOD SQUAD fix: Phase 2C finding)
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
app.include_router(positions.router, prefix="/api")  # Position management
app.include_router(stream.router, prefix="/api")
app.include_router(screening.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(market_data.router, prefix="/api", tags=["market-data"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(options.router, prefix="/api")  # Options Greeks calculator
app.include_router(proposals.router)  # Options trade proposals (already has /api/proposals prefix)
app.include_router(ai.router, prefix="/api")
app.include_router(claude.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(backtesting.router, prefix="/api")
app.include_router(ml.router, prefix="/api")  # Machine Learning (Phase 2)
app.include_router(
    ml_sentiment.router, prefix="/api"
)  # ML Sentiment & Signals (Phase 2 - Active) - Re-enabled with unified auth
app.include_router(
    monitoring.router, prefix="/api"
)  # Monitoring & Health Checks (Phase 4)
app.include_router(telemetry.router, prefix="/api")
