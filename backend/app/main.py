import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file before importing settings
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

print(f"\n===== BACKEND STARTUP =====")
print(f".env path: {env_path}")
print(f".env exists: {env_path.exists()}")
print(f"API_TOKEN from env: {os.getenv('API_TOKEN', 'NOT_SET')}")
print(f"TRADIER_API_KEY configured: {'YES' if os.getenv('TRADIER_API_KEY') else 'NO'}")
print(f"Deployed from: main branch - Tradier integration active")
print(f"===========================\n", flush=True)

import atexit

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
    orders,
    portfolio,
    scheduler,
    screening,
)
from .routers import settings as settings_router
from .routers import (
    stock,
    strategies,
    stream,
    telemetry,
    users,
)
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
            "production" if "render.com" in os.getenv("RENDER_EXTERNAL_URL", "") else "development"
        ),
        release=f"paiid-backend@1.0.0",
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

print(f"\n===== SETTINGS LOADED =====")
print(f"settings.API_TOKEN: {settings.API_TOKEN}")
print(f"===========================\n", flush=True)

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
    # Initialize cache service
    try:
        from .services.cache import init_cache

        init_cache()
    except Exception as e:
        print(f"[ERROR] Failed to initialize cache: {str(e)}", flush=True)

    # Initialize scheduler
    try:
        scheduler_instance = init_scheduler()
        print("[OK] Scheduler initialized and started", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to initialize scheduler: {str(e)}", flush=True)

    # ⚠️ ARCHITECTURE NOTE: Tradier provides ALL market data (quotes, streaming, analysis)
    # Alpaca is used ONLY for paper trade execution (orders, positions, account)
    # Future: Tradier will also handle live trading post-MVP
    print("[INFO] Market data: Tradier API | Trade execution: Alpaca Paper Trading", flush=True)

    # Start Tradier streaming service
    try:
        from .services.tradier_stream import get_tradier_stream, start_tradier_stream

        await start_tradier_stream()
        print("[OK] Tradier streaming initialized", flush=True)

        # Subscribe to market indices for radial menu real-time updates
        stream = get_tradier_stream()
        await stream.subscribe_quotes(["$DJI", "COMP:GIDS"])
        print("[OK] Subscribed to $DJI and COMP for real-time streaming", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to start Tradier stream: {e}", flush=True)


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
        print(f"[ERROR] Scheduler shutdown error: {str(e)}", flush=True)

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

app.add_middleware(CacheControlMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
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
app.include_router(stream.router, prefix="/api")
app.include_router(screening.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(market_data.router, prefix="/api", tags=["market-data"])
app.include_router(news.router, prefix="/api", tags=["news"])
app.include_router(ai.router, prefix="/api")
app.include_router(claude.router, prefix="/api")
app.include_router(stock.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(backtesting.router, prefix="/api")
app.include_router(telemetry.router)
