import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


def _coerce_sample_rate(raw_value: str | float | None, default: float) -> float:
    """Convert an environment value into a valid sample rate."""

    if raw_value is None:
        return default

    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return default

    if 0.0 <= value <= 1.0:
        return value

    return default


# Load .env file BEFORE reading env vars (works even when imported directly)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)


class Settings(BaseModel):
    # Read directly from environment variables (loaded above)
    API_TOKEN: str = os.getenv("API_TOKEN", "change-me")
    ALLOW_ORIGIN: str | None = os.getenv("ALLOW_ORIGIN")
    LIVE_TRADING: bool = os.getenv("LIVE_TRADING", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
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
    SENTRY_RELEASE: str | None = os.getenv("SENTRY_RELEASE")
    SENTRY_ENVIRONMENT: str = os.getenv(
        "SENTRY_ENVIRONMENT",
        "production" if os.getenv("RENDER_EXTERNAL_URL") else "development",
    )
    SENTRY_TRACES_SAMPLE_RATE: float = _coerce_sample_rate(
        os.getenv("SENTRY_TRACES_SAMPLE_RATE"),
        0.1,
    )
    SENTRY_PROFILES_SAMPLE_RATE: float = _coerce_sample_rate(
        os.getenv("SENTRY_PROFILES_SAMPLE_RATE"),
        0.1,
    )

    # JWT Authentication (Week 2-4: Multi-User System)
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "dev-secret-key-change-in-production-NEVER-COMMIT-THIS"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days


settings = Settings()
