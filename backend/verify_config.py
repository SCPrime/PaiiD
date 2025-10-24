"""Verify PaiiD backend configuration before launching services."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure project root is on PYTHONPATH so `app` package resolves when invoked from anywhere.
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

ENV_PATH = REPO_ROOT / ".env"

if not ENV_PATH.exists():
    print(f"❌ ERROR: .env file not found at {ENV_PATH}")
    print("Create one using .env.example as a template")
    sys.exit(1)

load_dotenv(ENV_PATH)

from app.core.bootstrap import emit_startup_summary  # noqa: E402
from app.core.config import Settings  # noqa: E402
from app.core.prelaunch import mask_secret  # noqa: E402


def _print_optional_settings(settings: Settings) -> None:
    optional_keys = [
        "ALPHA_VANTAGE_API_KEY",
        "POLYGON_API_KEY",
        "FINNHUB_API_KEY",
        "NEWSAPI_API_KEY",
    ]

    print("\n[+] Optional Integrations")
    print("-" * 60)
    for key in optional_keys:
        value = os.getenv(key)
        status = "[OK]" if value else "[SKIP]"
        display = mask_secret(value) if value else "Not configured (optional)"
        print(f"  {status} {key:25} = {display}")


def _print_database_settings(settings: Settings) -> None:
    print("\n[+] Database & Cache")
    print("-" * 60)
    db_url = os.getenv("DATABASE_URL")
    redis_url = os.getenv("REDIS_URL")
    print(
        "  [OK] DATABASE_URL configured"
        if db_url
        else "  [WARN] DATABASE_URL not configured (required for multi-user deployments)"
    )
    print(
        "  [OK] REDIS_URL configured"
        if redis_url
        else "  [WARN] REDIS_URL not configured (required for caching/queues)"
    )


def verify_config() -> bool:
    """Run the shared prelaunch validators and report optional context."""

    settings = Settings()
    report = emit_startup_summary(
        settings=settings,
        application="paiid-backend-config",
        env_path=ENV_PATH,
    )

    _print_database_settings(settings)
    _print_optional_settings(settings)

    if report.has_errors:
        print("\n[FAILURE] Critical configuration missing. Resolve errors above before deploying.")
        return False

    if report.has_warnings:
        print("\n[NOTICE] Configuration includes warnings. Review before production deploy.")

    print("\n[SUCCESS] Core configuration verified!")
    return True


if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)
