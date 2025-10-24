import os
from pathlib import Path

from dotenv import load_dotenv


# Load .env file before importing settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print("\n===== BACKEND STARTUP =====")
print(f".env path: {env_path}")
print(f".env exists: {env_path.exists()}")
print(f"API_TOKEN from env: {os.getenv('API_TOKEN', 'NOT_SET')}")
print(f"TRADIER_API_KEY configured: {'YES' if os.getenv('TRADIER_API_KEY') else 'NO'}")
print("Deployed from: main branch - Tradier integration active")
print("===========================\n", flush=True)


import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .recommendations.router import router as recommendations_router
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
print(f"settings.API_TOKEN: {settings.API_TOKEN}")
print("===========================\n", flush=True)

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
    print("[OK] Rate limiting enabled", flush=True)
else:
    print("[TEST MODE] Rate limiting disabled for tests", flush=True)


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


# Shutdown scheduler and streaming gracefully
@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown scheduler
    try:
        from .scheduler import get_scheduler

        scheduler_instance = get_scheduler()
        scheduler_instance.shutdown()
        print("[OK] Scheduler shut down gracefully", flush=True)
    except Exception as e:
        print(f"[ERROR] Scheduler shutdown error: {e!s}", flush=True)

    # Stop Tradier streaming
    try:
        from .services.tradier_stream import stop_tradier_stream

        await stop_tradier_stream()
        print("[OK] Tradier stream stopped", flush=True)
    except Exception as e:
        print(f"[ERROR] Tradier shutdown error: {e}", flush=True)


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
app.include_router(recommendations_router, prefix="/api")
