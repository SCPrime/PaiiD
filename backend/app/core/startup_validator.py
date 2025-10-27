"""
Startup validation module for PaiiD Trading Platform.
Validates environment configuration and API connectivity on application startup.

Purpose:
- Fail fast on startup with clear error messages
- Prevent runtime failures due to missing/invalid configuration
- Validate Tradier account ID configuration (Wave 4 finding)
- Test external API connectivity before accepting requests

Usage:
    from app.core.startup_validator import validate_startup

    @app.on_event("startup")
    async def startup_event():
        if not validate_startup():
            sys.exit(1)
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import httpx
from app.core.config import settings

# Initialize logger
logger = logging.getLogger(__name__)


class StartupValidator:
    """Validates application configuration and dependencies on startup."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.validations: Dict[str, Tuple[bool, str]] = {}

    def validate_all(self) -> bool:
        """
        Run all startup validations.

        Returns:
            bool: True if all critical validations pass, False otherwise
        """
        logger.info("=" * 70)
        logger.info("🔍 Running startup validation...")
        logger.info("=" * 70)

        # Critical validations (must pass)
        self._validate_required_env_vars()
        self._validate_tradier_connection()
        self._validate_alpaca_connection()

        # Non-critical validations (warnings only)
        self._validate_optional_env_vars()
        self._validate_database_connection()

        # Log results
        self._log_results()

        # Return True only if no critical errors
        return len(self.errors) == 0

    def _validate_required_env_vars(self):
        """Validate required environment variables are set."""
        required_vars = {
            "API_TOKEN": settings.API_TOKEN,
            "TRADIER_API_KEY": settings.TRADIER_API_KEY,
            "TRADIER_ACCOUNT_ID": settings.TRADIER_ACCOUNT_ID,
            "ALPACA_API_KEY": settings.ALPACA_API_KEY,
            "ALPACA_SECRET_KEY": settings.ALPACA_SECRET_KEY,
        }

        for var_name, var_value in required_vars.items():
            if not var_value or var_value == "":
                self.errors.append(f"❌ {var_name} is not set")
                self.validations[var_name] = (False, "Not configured")
                logger.error(f"❌ {var_name} is not set")
            else:
                self.validations[var_name] = (True, "Configured")
                logger.info(f"✅ {var_name} configured")

    def _validate_optional_env_vars(self):
        """Validate optional environment variables."""
        optional_vars = {
            "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
            "SENTRY_DSN": getattr(settings, "SENTRY_DSN", None),
        }

        for var_name, var_value in optional_vars.items():
            if not var_value or var_value == "":
                self.warnings.append(f"⚠️ {var_name} not set (optional)")
                self.validations[var_name] = (False, "Not configured (optional)")
                logger.warning(f"⚠️ {var_name} not set (optional)")
            else:
                self.validations[var_name] = (True, "Configured")
                logger.info(f"✅ {var_name} configured")

    def _validate_tradier_connection(self):
        """Test Tradier API connection and account access."""
        if not settings.TRADIER_API_KEY:
            logger.warning("⚠️ Skipping Tradier validation (API key not set)")
            return  # Already logged error

        try:
            url = f"{settings.TRADIER_API_BASE_URL}/user/profile"
            headers = {
                "Authorization": f"Bearer {settings.TRADIER_API_KEY}",
                "Accept": "application/json"
            }

            logger.info(f"Testing Tradier API connection to {url}...")

            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)

            if response.status_code == 200:
                profile = response.json().get("profile", {})
                account_id = profile.get("account", {}).get("account_number")

                if account_id != settings.TRADIER_ACCOUNT_ID:
                    error_msg = (
                        f"❌ Tradier account ID mismatch: "
                        f"configured={settings.TRADIER_ACCOUNT_ID}, "
                        f"actual={account_id}"
                    )
                    self.errors.append(error_msg)
                    self.validations["tradier_account"] = (False, "Account ID mismatch")
                    logger.error(error_msg)
                    logger.error(
                        "Fix: Update TRADIER_ACCOUNT_ID in .env to match your account"
                    )
                else:
                    success_msg = f"Account {account_id} verified"
                    self.validations["tradier_connection"] = (True, success_msg)
                    logger.info(f"✅ Tradier API connected ({success_msg})")

            elif response.status_code == 401:
                error_msg = "❌ Tradier API authentication failed (invalid API key)"
                self.errors.append(error_msg)
                self.validations["tradier_connection"] = (False, "Authentication failed")
                logger.error(error_msg)
                logger.error("Fix: Check TRADIER_API_KEY in .env")

            else:
                error_msg = f"❌ Tradier API error: HTTP {response.status_code}"
                self.errors.append(error_msg)
                self.validations["tradier_connection"] = (False, f"HTTP {response.status_code}")
                logger.error(error_msg)
                logger.error(f"Response: {response.text[:200]}")

        except Exception as e:
            error_msg = f"❌ Tradier API connection failed: {e!s}"
            self.errors.append(error_msg)
            self.validations["tradier_connection"] = (False, str(e))
            logger.error(error_msg)
            logger.error("Fix: Check network connectivity and Tradier API status")

    def _validate_alpaca_connection(self):
        """Test Alpaca API connection and paper account access."""
        if not settings.ALPACA_API_KEY or not settings.ALPACA_SECRET_KEY:
            logger.warning("⚠️ Skipping Alpaca validation (credentials not set)")
            return  # Already logged error

        try:
            from alpaca.trading.client import TradingClient

            logger.info("Testing Alpaca API connection...")

            client = TradingClient(
                settings.ALPACA_API_KEY,
                settings.ALPACA_SECRET_KEY,
                paper=True
            )

            account = client.get_account()

            success_msg = f"Paper account connected (equity: ${float(account.equity):,.2f})"
            self.validations["alpaca_connection"] = (True, success_msg)
            logger.info(f"✅ Alpaca API connected ({success_msg})")

        except Exception as e:
            error_msg = f"❌ Alpaca API connection failed: {e!s}"
            self.errors.append(error_msg)
            self.validations["alpaca_connection"] = (False, str(e))
            logger.error(error_msg)
            logger.error("Fix: Check ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY in .env")

    def _validate_database_connection(self):
        """Test database connection (non-critical)."""
        database_url = getattr(settings, "DATABASE_URL", None)

        if not database_url:
            warning_msg = "⚠️ DATABASE_URL not set (using in-memory storage)"
            self.warnings.append(warning_msg)
            self.validations["database"] = (False, "Not configured")
            logger.warning(warning_msg)
        else:
            # Test database connection
            try:
                from sqlalchemy import create_engine, text

                logger.info("Testing database connection...")

                engine = create_engine(database_url)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

                self.validations["database"] = (True, "Connected")
                logger.info("✅ Database connection verified")
            except Exception as e:
                warning_msg = f"⚠️ Database connection failed: {e!s}"
                self.warnings.append(warning_msg)
                self.validations["database"] = (False, str(e))
                logger.warning(warning_msg)

    def _log_results(self):
        """Log validation results summary."""
        logger.info("=" * 70)
        logger.info("STARTUP VALIDATION RESULTS")
        logger.info("=" * 70)

        if self.errors:
            logger.error(f"❌ {len(self.errors)} CRITICAL ERROR(S):")
            for error in self.errors:
                logger.error(f"  {error}")

        if self.warnings:
            logger.warning(f"⚠️ {len(self.warnings)} WARNING(S):")
            for warning in self.warnings:
                logger.warning(f"  {warning}")

        if not self.errors:
            logger.info("✅ All critical validations passed")

        logger.info("=" * 70)


def validate_startup() -> bool:
    """
    Run startup validation and fail fast if critical errors found.

    Returns:
        bool: True if validation passed, False otherwise
    """
    validator = StartupValidator()
    passed = validator.validate_all()

    if not passed:
        logger.error("🚨 STARTUP VALIDATION FAILED - APPLICATION CANNOT START")
        logger.error("Fix configuration errors and restart the application")
        return False

    logger.info("🚀 Startup validation complete - application ready")
    return True
