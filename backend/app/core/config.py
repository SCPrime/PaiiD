from pydantic import BaseModel, AnyHttpUrl
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file BEFORE reading env vars (works even when imported directly)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(ENV_PATH)

class Settings(BaseModel):
    # Read directly from environment variables (loaded above)
    API_TOKEN: str = os.getenv("API_TOKEN", "change-me")
    ALLOW_ORIGIN: Optional[str] = os.getenv("ALLOW_ORIGIN")
    LIVE_TRADING: bool = os.getenv("LIVE_TRADING", "false").lower() == "true"
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
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")

    # Redis (Phase 2.5)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")

    # Sentry Error Tracking (Phase 2.5)
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

settings = Settings()