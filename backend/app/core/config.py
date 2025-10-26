import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


# Load .env file BEFORE reading env vars (works even when imported directly)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)


class Settings(BaseModel):
    # =====================================
    # REQUIRED SECRETS - Must be set in production
    # =====================================

    # Backend API Authentication Token
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    API_TOKEN: str = Field(
        default_factory=lambda: os.getenv("API_TOKEN", ""),
        description="Backend API authentication token (REQUIRED)"
    )

    # Tradier API credentials (MARKET DATA, NEWS, QUOTES)
    TRADIER_API_KEY: str = Field(
        default_factory=lambda: os.getenv("TRADIER_API_KEY", ""),
        description="Tradier API key for market data (REQUIRED)"
    )
    TRADIER_ACCOUNT_ID: str = Field(
        default_factory=lambda: os.getenv("TRADIER_ACCOUNT_ID", ""),
        description="Tradier account ID (REQUIRED)"
    )
    TRADIER_API_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("TRADIER_API_BASE_URL", "https://api.tradier.com/v1"),
        description="Tradier API base URL"
    )

    # Alpaca API credentials (PAPER TRADING EXECUTION ONLY)
    ALPACA_API_KEY: str = Field(
        default_factory=lambda: os.getenv("ALPACA_PAPER_API_KEY", ""),
        description="Alpaca paper trading API key (REQUIRED)"
    )
    ALPACA_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("ALPACA_PAPER_SECRET_KEY", ""),
        description="Alpaca paper trading secret key (REQUIRED)"
    )
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"

    # Database Connection (REQUIRED for multi-user auth)
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", ""),
        description="PostgreSQL database URL (REQUIRED for production)"
    )

    # JWT Authentication Secret (REQUIRED for multi-user system)
    # CRITICAL: Must be cryptographically secure in production
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv(
            "JWT_SECRET_KEY",
            secrets.token_urlsafe(32) if os.getenv("TESTING") != "true" else "test-secret-key-do-not-use-in-production"
        ),
        description="JWT signing secret (REQUIRED, auto-generated if not set)"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # =====================================
    # OPTIONAL SECRETS - Enhance functionality
    # =====================================

    # Anthropic API (AI recommendations and chat)
    ANTHROPIC_API_KEY: str = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""),
        description="Anthropic API key for AI features (optional)"
    )

    # GitHub Webhook Secret (Repository Monitor)
    GITHUB_WEBHOOK_SECRET: str = Field(
        default_factory=lambda: os.getenv("GITHUB_WEBHOOK_SECRET", ""),
        description="GitHub webhook secret for repo monitoring (optional)"
    )

    # Redis Cache (Improves performance)
    REDIS_URL: str | None = Field(
        default_factory=lambda: os.getenv("REDIS_URL"),
        description="Redis connection URL for caching (optional)"
    )

    # Sentry Error Tracking (Recommended for production)
    SENTRY_DSN: str = Field(
        default_factory=lambda: os.getenv("SENTRY_DSN", ""),
        description="Sentry DSN for error tracking (recommended for production)"
    )
    SENTRY_ENVIRONMENT: str = Field(
        default_factory=lambda: os.getenv("SENTRY_ENVIRONMENT", "development"),
        description="Sentry environment name"
    )

    # =====================================
    # CONFIGURATION (Non-secret)
    # =====================================

    # CORS and Server Configuration
    ALLOW_ORIGIN: str | None = Field(
        default_factory=lambda: os.getenv("ALLOW_ORIGIN"),
        description="Allowed CORS origin"
    )

    # Trading Mode
    LIVE_TRADING: bool = Field(
        default_factory=lambda: os.getenv("LIVE_TRADING", "false").lower() == "true",
        description="Enable live trading (default: paper trading only)"
    )

    # Testing Mode
    TESTING: bool = Field(
        default_factory=lambda: os.getenv("TESTING", "false").lower() == "true",
        description="Enable testing mode"
    )

    # Idempotency TTL
    IDMP_TTL_SECONDS: int = Field(
        default_factory=lambda: int(os.getenv("IDMP_TTL_SECONDS", "600")),
        description="Idempotency key TTL in seconds"
    )

    # Logging Configuration
    LOG_LEVEL: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Application log level"
    )

    # Test Fixtures (for Playwright deterministic testing)
    USE_TEST_FIXTURES: bool = Field(
        default_factory=lambda: os.getenv("USE_TEST_FIXTURES", "false").lower() == "true",
        description="Use test fixtures for deterministic testing"
    )

    # =====================================
    # CACHE TTL CONFIGURATION (in seconds)
    # =====================================

    # Real-time market data (very short TTL for live updates)
    CACHE_TTL_QUOTE: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_QUOTE", "5")),
        description="Quote cache TTL in seconds (default: 5s for real-time data)"
    )

    # Options data (moderate TTL, updated less frequently)
    CACHE_TTL_OPTIONS_CHAIN: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_OPTIONS_CHAIN", "60")),
        description="Options chain cache TTL in seconds (default: 60s)"
    )
    CACHE_TTL_OPTIONS_EXPIRY: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_OPTIONS_EXPIRY", "300")),
        description="Options expiration dates cache TTL in seconds (default: 5 minutes)"
    )

    # Historical data (long TTL, static past data)
    CACHE_TTL_HISTORICAL_BARS: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_HISTORICAL_BARS", "3600")),
        description="Historical bars cache TTL in seconds (default: 1 hour)"
    )

    # News articles (moderate TTL)
    CACHE_TTL_NEWS: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_NEWS", "300")),
        description="News articles cache TTL in seconds (default: 5 minutes)"
    )

    # Company/static data (long TTL, rarely changes)
    CACHE_TTL_COMPANY_INFO: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_COMPANY_INFO", "86400")),
        description="Company info cache TTL in seconds (default: 24 hours)"
    )

    # Scanner results (moderate TTL)
    CACHE_TTL_SCANNER: int = Field(
        default_factory=lambda: int(os.getenv("CACHE_TTL_SCANNER", "180")),
        description="Market scanner cache TTL in seconds (default: 3 minutes)"
    )

    @field_validator("API_TOKEN")
    @classmethod
    def validate_api_token(cls, v: str) -> str:
        """Validate API_TOKEN is set and not a placeholder."""
        if not v or v == "change-me":
            raise ValueError(
                "API_TOKEN must be set to a secure random value. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        if len(v) < 20:
            raise ValueError("API_TOKEN must be at least 20 characters long for security")
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT_SECRET_KEY is cryptographically secure."""
        if not v:
            raise ValueError("JWT_SECRET_KEY cannot be empty")
        if "dev-secret" in v.lower() or "change" in v.lower() or "test" in v.lower():
            # Allow test keys only in testing mode
            if os.getenv("TESTING") != "true":
                raise ValueError(
                    "JWT_SECRET_KEY must be a cryptographically secure random value in production. "
                    "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
        if len(v) < 32 and os.getenv("TESTING") != "true":
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long for security")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL is properly formatted."""
        if not v:
            # Allow empty in testing mode
            if os.getenv("TESTING") == "true":
                return "sqlite:///./test.db"
            raise ValueError(
                "DATABASE_URL must be set for production. "
                "Format: postgresql://user:password@host:port/database"
            )
        if not v.startswith(("postgresql://", "sqlite://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL or SQLite connection string")
        return v


settings = Settings()


def get_settings() -> Settings:
    """Get the settings singleton instance."""
    return settings


def validate_required_secrets(strict: bool = False) -> tuple[bool, list[str]]:
    """
    Validate that all required secrets are properly configured.

    Args:
        strict: If True, require all optional secrets as well

    Returns:
        Tuple of (success: bool, missing_secrets: list[str])
    """
    missing = []

    # Required secrets for core functionality
    required_secrets = {
        "API_TOKEN": settings.API_TOKEN,
        "TRADIER_API_KEY": settings.TRADIER_API_KEY,
        "TRADIER_ACCOUNT_ID": settings.TRADIER_ACCOUNT_ID,
        "ALPACA_API_KEY": settings.ALPACA_API_KEY,
        "ALPACA_SECRET_KEY": settings.ALPACA_SECRET_KEY,
        "DATABASE_URL": settings.DATABASE_URL,
        "JWT_SECRET_KEY": settings.JWT_SECRET_KEY,
    }

    # Optional but recommended secrets
    recommended_secrets = {
        "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
        "SENTRY_DSN": settings.SENTRY_DSN,
    }

    # Check required secrets
    for key, value in required_secrets.items():
        if not value or value in ["change-me", "", "your-key-here"]:
            missing.append(f"{key} (REQUIRED)")

    # Check recommended secrets in strict mode
    if strict:
        for key, value in recommended_secrets.items():
            if not value:
                missing.append(f"{key} (RECOMMENDED)")

    return (len(missing) == 0, missing)
