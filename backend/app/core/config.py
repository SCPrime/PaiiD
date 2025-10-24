import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, model_validator


# Load .env file BEFORE reading env vars (works even when imported directly)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)


class Settings(BaseModel):
    # Read directly from environment variables (loaded above)
    APP_ENV: str = os.getenv("APP_ENV", "local")
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

    # Deployment metadata
    GIT_COMMIT: str | None = os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_COMMIT")
    RELEASE_VERSION: str | None = os.getenv("RELEASE_VERSION")

    # JWT Authentication (Week 2-4: Multi-User System)
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "dev-secret-key-change-in-production-NEVER-COMMIT-THIS"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    @model_validator(mode="after")
    def _enforce_production_requirements(self):
        """Require production-only settings when APP_ENV is non-local."""

        normalized_env = self.app_env

        if normalized_env not in {"local", "development", "dev", "test"} and not self.SENTRY_DSN:
            raise ValueError(
                "SENTRY_DSN must be configured when APP_ENV is set to a non-development profile"
            )

        if not self.GIT_COMMIT:
            # Attempt to resolve the current commit locally for richer logging.
            self.GIT_COMMIT = self._resolve_local_commit()

        return self

    @property
    def app_env(self) -> str:
        """Return the normalized application environment profile."""

        return (self.APP_ENV or "local").strip().lower()

    @property
    def environment_label(self) -> str:
        """Return a human-friendly environment label for logging."""

        mapping = {
            "dev": "development",
            "development": "development",
            "local": "local",
            "test": "test",
            "staging": "staging",
            "preview": "preview",
            "production": "production",
        }

        return mapping.get(self.app_env, self.APP_ENV)

    def _resolve_local_commit(self) -> str | None:
        """Attempt to resolve the local git commit when not provided."""

        path = Path(__file__).resolve()

        for candidate in path.parents:
            if (candidate / ".git").exists():
                repo_root = candidate
                break
        else:
            # Fallback to repository root heuristic (4 levels up from this file)
            try:
                repo_root = path.parents[3]
            except IndexError:
                repo_root = path.parent

        try:
            result = subprocess.run(
                ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            )
        except Exception:
            return None

        return result.stdout.strip() or None


settings = Settings()
