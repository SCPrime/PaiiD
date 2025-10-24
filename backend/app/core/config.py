import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


# Load .env file BEFORE reading env vars (works even when imported directly)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)


class Settings(BaseModel):
    # Read directly from environment variables (loaded above)
    API_TOKEN: str = os.getenv("API_TOKEN", "change-me")
    ALLOW_ORIGIN: str | None = os.getenv("ALLOW_ORIGIN")
    LIVE_TRADING: bool = os.getenv("LIVE_TRADING", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    IDMP_TTL_SECONDS: int = int(os.getenv("IDMP_TTL_SECONDS", "600"))

    # Alpaca API credentials (PAPER TRADING EXECUTION ONLY)
    ALPACA_API_KEY: str = os.getenv("ALPACA_PAPER_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_PAPER_SECRET_KEY", "")
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"

    # Tradier API credentials (MARKET DATA, NEWS, QUOTES)
    TRADIER_API_KEY: str = os.getenv("TRADIER_API_KEY", "")
    TRADIER_ACCOUNT_ID: str = os.getenv("TRADIER_ACCOUNT_ID", "")
    TRADIER_API_BASE_URL: str = os.getenv("TRADIER_API_BASE_URL", "https://api.tradier.com/v1")

    # Anthropic API (AI FALLBACK for market data)
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Database (Phase 2.5)
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # Redis (Phase 2.5)
    REDIS_URL: str | None = os.getenv("REDIS_URL")

    # Sentry Error Tracking (Phase 2.5)
    SENTRY_DSN: str | None = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", APP_ENV)
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    SENTRY_PROFILES_SAMPLE_RATE: float = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))
    SENTRY_RELEASE: str = os.getenv("SENTRY_RELEASE", "paiid-backend@1.0.0")

    # Datadog tracing
    DATADOG_TRACE_ENABLED: bool = os.getenv("DATADOG_TRACE_ENABLED", "false").lower() == "true"
    DATADOG_SERVICE_NAME: str = os.getenv("DATADOG_SERVICE_NAME", "paiid-backend")
    DATADOG_ENVIRONMENT: str = os.getenv("DATADOG_ENVIRONMENT", APP_ENV)
    DATADOG_TRACE_AGENT_URL: str | None = os.getenv("DATADOG_TRACE_AGENT_URL")

    # New Relic agent
    NEW_RELIC_ENABLED: bool = os.getenv("NEW_RELIC_ENABLED", "false").lower() == "true"
    NEW_RELIC_CONFIG_FILE: str | None = os.getenv("NEW_RELIC_CONFIG_FILE")
    NEW_RELIC_ENVIRONMENT: str = os.getenv("NEW_RELIC_ENVIRONMENT", APP_ENV)
    NEW_RELIC_APP_NAME: str = os.getenv("NEW_RELIC_APP_NAME", "PaiiD Backend")

    # Observability verification
    OBSERVABILITY_VERIFY_ON_STARTUP: bool = (
        os.getenv("OBSERVABILITY_VERIFY_ON_STARTUP", "false").lower() == "true"
    )

    # JWT Authentication (Week 2-4: Multi-User System)
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "dev-secret-key-change-in-production-NEVER-COMMIT-THIS"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days


settings = Settings()
