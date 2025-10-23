import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, model_validator


# Load .env file BEFORE reading env vars (works even when imported directly)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)


logger = logging.getLogger(__name__)

DEFAULT_JWT_SECRET = "dev-only-jwt-secret-override-please-1234567890!ABC"


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

    # JWT Authentication (Week 2-4: Multi-User System)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", DEFAULT_JWT_SECRET)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    jwt_secret_strength: str = "unknown"
    jwt_secret_diagnostics: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_jwt_secret(cls, values: "Settings") -> "Settings":
        secret = values.JWT_SECRET_KEY
        diagnostics: list[str] = []

        if not secret:
            diagnostics.append("JWT secret must be set via JWT_SECRET_KEY environment variable.")

        if secret and len(secret) < 32:
            diagnostics.append("JWT secret must be at least 32 characters long.")

        if secret in {"change-me", "dev-secret-key-change-in-production-NEVER-COMMIT-THIS"}:
            diagnostics.append("JWT secret uses a known insecure placeholder value.")

        if secret:
            categories = {
                "uppercase": any(ch.isupper() for ch in secret),
                "lowercase": any(ch.islower() for ch in secret),
                "digit": any(ch.isdigit() for ch in secret),
                "symbol": any(not ch.isalnum() for ch in secret),
            }
            missing_categories = [name for name, present in categories.items() if not present]
            if missing_categories:
                diagnostics.append(
                    "JWT secret is missing character classes: " + ", ".join(missing_categories)
                )

        if diagnostics:
            values.jwt_secret_strength = "invalid"
            values.jwt_secret_diagnostics = tuple(diagnostics)
            logger.critical("JWT secret validation failed: %s", " | ".join(diagnostics))
            raise ValueError(" ".join(diagnostics))

        if secret == DEFAULT_JWT_SECRET:
            warning = (
                "Default development JWT secret is in use. Override JWT_SECRET_KEY for production."
            )
            values.jwt_secret_strength = "development"
            values.jwt_secret_diagnostics = (warning,)
            logger.warning(warning)
        else:
            values.jwt_secret_strength = "strong"
            values.jwt_secret_diagnostics = ()
            logger.info(
                "JWT secret validated successfully (length=%d, strength=%s)",
                len(secret),
                values.jwt_secret_strength,
            )

        return values


settings = Settings()
