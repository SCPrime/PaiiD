from dotenv import load_dotenv
from pathlib import Path
import os

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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .routers import health, settings as settings_router, portfolio, orders, stream, screening, market, ai, telemetry, strategies, scheduler, claude, market_data, news, analytics, backtesting
from .scheduler import init_scheduler
import atexit
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

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
        environment="production" if "render.com" in os.getenv("RENDER_EXTERNAL_URL", "") else "development",
        release=f"paiid-backend@1.0.0",
        send_default_pii=False,  # Don't send personally identifiable info
        before_send=lambda event, hint: event if not event.get("request", {}).get("headers", {}).get("Authorization") else {**event, "request": {**event.get("request", {}), "headers": {**event.get("request", {}).get("headers", {}), "Authorization": "[REDACTED]"}}}
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
    version="1.0.0"
)

# Initialize scheduler and cache on startup
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

# Shutdown scheduler gracefully
@app.on_event("shutdown")
async def shutdown_event():
    try:
        from .scheduler import get_scheduler
        scheduler_instance = get_scheduler()
        scheduler_instance.shutdown()
        print("[OK] Scheduler shut down gracefully", flush=True)
    except Exception as e:
        print(f"[ERROR] Scheduler shutdown error: {str(e)}", flush=True)

# Add Sentry context middleware if Sentry is enabled
if settings.SENTRY_DSN:
    from .middleware.sentry import SentryContextMiddleware
    app.add_middleware(SentryContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "https://paiid-snowy.vercel.app",
        "https://paiid-scprimes-projects.vercel.app",
        "https://paiid-git-main-scprimes-projects.vercel.app",
        "https://frontend-scprimes-projects.vercel.app",
        "https://frontend-three-rho-84.vercel.app",
        "https://frontend-scprime-scprimes-projects.vercel.app",
        "https://frontend-mftcsnbqx-scprimes-projects.vercel.app",
        settings.ALLOW_ORIGIN
    ] if settings.ALLOW_ORIGIN else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
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
app.include_router(strategies.router, prefix="/api")
app.include_router(scheduler.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(backtesting.router, prefix="/api")
app.include_router(telemetry.router)