"""
Pre-launch Validation Module

Comprehensive validation checks before application startup to prevent common deployment issues:
- Port availability (prevents zombie process conflicts)
- Python version requirements
- Critical dependency verification
- Environment variable validation
- External service connectivity

Usage:
    python -m app.core.prelaunch --strict
    python -m app.core.prelaunch --check-only
"""

import asyncio
import logging
import os
import socket
import sys
from typing import Any

import httpx
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of a validation check"""

    name: str
    success: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class PrelaunchValidator:
    """
    Comprehensive pre-launch validation for PaiiD backend.

    Validates:
    - Port availability (prevents zombie process conflicts)
    - Python version (3.10+ required)
    - Critical dependencies (fastapi, uvicorn, etc.)
    - Environment variables (required vs optional)
    - External service connectivity (Tradier, Alpaca)
    """

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.results: list[ValidationResult] = []
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_port_availability(self) -> ValidationResult:
        """Check if target port is available (prevents zombie process conflicts)"""
        port = int(os.getenv("PORT", "8001"))

        try:
            # Test if we can bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.bind(("127.0.0.1", port))
            sock.close()

            return ValidationResult(
                name="port_availability",
                success=True,
                message=f"Port {port} is available",
                details={"port": port},
            )
        except OSError as e:
            error_msg = f"Port {port} is in use - run cleanup first"
            if self.strict_mode:
                self.errors.append(error_msg)

            return ValidationResult(
                name="port_availability",
                success=False,
                message=error_msg,
                details={"port": port, "error": str(e)},
            )

    def validate_python_version(self) -> ValidationResult:
        """Ensure Python 3.10+ requirement"""
        major, minor = sys.version_info[:2]
        required_version = (3, 10)

        if (major, minor) >= required_version:
            return ValidationResult(
                name="python_version",
                success=True,
                message=f"Python {major}.{minor} meets requirement (3.10+)",
                details={"version": f"{major}.{minor}", "required": "3.10+"},
            )
        else:
            error_msg = f"Python 3.10+ required, found {major}.{minor}"
            if self.strict_mode:
                self.errors.append(error_msg)

            return ValidationResult(
                name="python_version",
                success=False,
                message=error_msg,
                details={"version": f"{major}.{minor}", "required": "3.10+"},
            )

    def validate_critical_dependencies(self) -> ValidationResult:
        """Test import of critical dependencies"""
        critical_packages = [
            "fastapi",
            "uvicorn",
            "cachetools",
            "anthropic",
            "psutil",
            "sentry_sdk",
            "redis",
            "sqlalchemy",
        ]

        missing = []
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)

        if not missing:
            return ValidationResult(
                name="critical_dependencies",
                success=True,
                message=f"All {len(critical_packages)} critical dependencies available",
                details={"packages": critical_packages},
            )
        else:
            error_msg = f"Missing critical dependencies: {', '.join(missing)}"
            if self.strict_mode:
                self.errors.append(error_msg)

            return ValidationResult(
                name="critical_dependencies",
                success=False,
                message=error_msg,
                details={"missing": missing, "total": len(critical_packages)},
            )

    def validate_required_secrets(self) -> ValidationResult:
        """Validate required environment variables"""
        # Detect production environment
        sentry_env = os.getenv("SENTRY_ENVIRONMENT", "development")
        render_url = os.getenv("RENDER_EXTERNAL_URL", "")
        is_production = sentry_env == "production" or "render.com" in render_url

        # Base required vars
        required_vars = [
            "API_TOKEN",
            "ALPACA_PAPER_API_KEY",
            "ALPACA_PAPER_SECRET_KEY",
            "TRADIER_API_KEY",
        ]

        # SENTRY_DSN required in production only
        if is_production:
            required_vars.append("SENTRY_DSN")

        missing = []
        security_errors = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        # Additional production security validations
        if is_production:
            jwt_key = os.getenv("JWT_SECRET_KEY", "")
            default_jwt = "dev-secret-key-change-in-production-NEVER-COMMIT-THIS"
            if (not jwt_key) or (jwt_key == default_jwt) or (len(jwt_key) < 32):
                security_errors.append(
                    "Invalid JWT_SECRET_KEY for production (unset/default/too short)"
                )

            live_trading = os.getenv("LIVE_TRADING", "false").lower() == "true"
            if (
                live_trading
                and os.getenv("LIVE_TRADING_CONFIRMED", "no").lower() != "yes"
            ):
                security_errors.append(
                    "LIVE_TRADING requires LIVE_TRADING_CONFIRMED=yes in production"
                )

        # Build result
        if not missing and not security_errors:
            return ValidationResult(
                name="required_secrets",
                success=True,
                message=f"All {len(required_vars)} required secrets configured",
                details={
                    "variables": required_vars,
                    "environment": sentry_env,
                    "is_production": is_production,
                },
            )
        else:
            messages = []
            if missing:
                if "SENTRY_DSN" in missing:
                    messages.append(
                        f"Missing required secrets: {', '.join(missing)}. SENTRY_DSN is required for production"
                    )
                else:
                    messages.append(f"Missing required secrets: {', '.join(missing)}")
            if security_errors:
                messages.extend(security_errors)

            error_msg = "; ".join(messages)
            if self.strict_mode:
                self.errors.append(error_msg)

            return ValidationResult(
                name="required_secrets",
                success=False,
                message=error_msg,
                details={
                    "missing": missing,
                    "security_errors": security_errors,
                    "total": len(required_vars),
                    "environment": sentry_env,
                    "is_production": is_production,
                },
            )

    def validate_observability_config(self) -> ValidationResult:
        """Validate observability configuration settings"""
        errors = []
        warnings = []

        # Validate LOG_LEVEL
        log_level = os.getenv("LOG_LEVEL", "INFO")
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_log_levels:
            errors.append(
                f"Invalid LOG_LEVEL '{log_level}'. Must be one of: {', '.join(valid_log_levels)}"
            )

        # Validate SENTRY_ENVIRONMENT
        sentry_env = os.getenv("SENTRY_ENVIRONMENT", "development")
        valid_sentry_envs = ["development", "staging", "production"]
        if sentry_env not in valid_sentry_envs:
            errors.append(
                f"Invalid SENTRY_ENVIRONMENT '{sentry_env}'. Must be one of: {', '.join(valid_sentry_envs)}"
            )

        # Check for conflicts
        use_test_fixtures = os.getenv("USE_TEST_FIXTURES", "false").lower() == "true"
        if use_test_fixtures and sentry_env == "production":
            warnings.append(
                "USE_TEST_FIXTURES=true in production environment - this should only be used for testing"
            )

        # Check REDIS_URL (non-blocking warning)
        if not os.getenv("REDIS_URL"):
            warnings.append(
                "REDIS_URL not configured - using in-memory fallback (not recommended for production)"
            )

        if errors:
            return ValidationResult(
                name="observability_config",
                success=False,
                message=f"Observability configuration errors: {'; '.join(errors)}",
                details={"errors": errors, "warnings": warnings},
            )
        else:
            return ValidationResult(
                name="observability_config",
                success=True,
                message=f"Observability configuration valid ({len(warnings)} warnings)",
                details={
                    "warnings": warnings,
                    "log_level": log_level,
                    "sentry_env": sentry_env,
                },
            )

    def validate_optional_secrets(self) -> ValidationResult:
        """Check optional environment variables"""
        optional_vars = [
            "ANTHROPIC_API_KEY",
            "DATABASE_URL",
            "REDIS_URL",
            "SENTRY_ENVIRONMENT",
            "LOG_LEVEL",
        ]

        configured = []
        missing = []
        for var in optional_vars:
            if os.getenv(var):
                configured.append(var)
            else:
                missing.append(var)

        return ValidationResult(
            name="optional_secrets",
            success=True,
            message=f"{len(configured)}/{len(optional_vars)} optional secrets configured",
            details={"configured": configured, "missing": missing},
        )

    async def validate_external_services(self) -> ValidationResult:
        """Test connectivity to external services"""
        services = {
            "Tradier API": "https://api.tradier.com/v1",
            "Alpaca API": "https://paper-api.alpaca.markets",
        }

        results = {}
        async with httpx.AsyncClient(timeout=5.0) as client:
            for name, url in services.items():
                try:
                    response = await client.get(f"{url}/health", follow_redirects=True)
                    results[name] = {
                        "status": "reachable",
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                    }
                except Exception as e:
                    results[name] = {"status": "unreachable", "error": str(e)}

        reachable = sum(1 for r in results.values() if r["status"] == "reachable")
        total = len(results)

        if reachable == total:
            return ValidationResult(
                name="external_services",
                success=True,
                message=f"All {total} external services reachable",
                details={"services": results},
            )
        else:
            warning_msg = f"Only {reachable}/{total} external services reachable"
            self.warnings.append(warning_msg)

            return ValidationResult(
                name="external_services",
                success=True,  # Non-blocking
                message=warning_msg,
                details={"services": results},
            )

    async def validate_all(self) -> tuple[bool, list[str], list[str]]:
        """
        Run all validation checks.

        Returns:
            (success, errors, warnings)
        """
        logger.info("🔍 Starting pre-launch validation...")

        # Core system validations
        self.results.append(self.validate_port_availability())
        self.results.append(self.validate_python_version())
        self.results.append(self.validate_critical_dependencies())

        # Environment validations
        self.results.append(self.validate_required_secrets())
        self.results.append(self.validate_observability_config())
        self.results.append(self.validate_optional_secrets())

        # External service validations
        self.results.append(await self.validate_external_services())

        # Calculate results
        failed_checks = [r for r in self.results if not r.success]
        success = len(failed_checks) == 0

        # Log results
        logger.info("=" * 60)
        logger.info("🎯 Pre-launch Validation Results")
        logger.info("=" * 60)

        for result in self.results:
            status = "✅" if result.success else "❌"
            logger.info(f"{status} {result.name}: {result.message}")

        if self.warnings:
            logger.warning(f"⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings:
                logger.warning(f"   • {warning}")

        if self.errors:
            logger.error(f"🚨 {len(self.errors)} errors:")
            for error in self.errors:
                logger.error(f"   • {error}")

        logger.info("=" * 60)

        if success:
            logger.info("✅ All pre-launch validations passed!")
        else:
            logger.error("❌ Pre-launch validation failed!")

        return success, self.errors, self.warnings


async def main():
    """CLI entrypoint for pre-launch validation"""
    import argparse

    parser = argparse.ArgumentParser(description="PaiiD Backend Pre-launch Validation")
    parser.add_argument(
        "--strict", action="store_true", help="Fail on warnings (production mode)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run validation without modifying anything",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    validator = PrelaunchValidator(strict_mode=args.strict)
    success, errors, warnings = await validator.validate_all()

    if not success:
        logger.error("Pre-launch validation failed!")
        sys.exit(1)
    else:
        logger.info("Pre-launch validation completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
