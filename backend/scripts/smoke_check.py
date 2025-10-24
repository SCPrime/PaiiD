"""Simple smoke test to verify Alpaca credentials and connectivity."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Ensure backend package is on the path when running as a module or script
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.alpaca_client import get_alpaca_client


def format_account_summary(account: dict[str, Any]) -> dict[str, Any]:
    """Return a trimmed summary of the Alpaca account for display."""
    return {
        "account_number": account.get("account_number"),
        "status": account.get("status"),
        "currency": account.get("currency"),
        "cash": account.get("cash"),
        "portfolio_value": account.get("portfolio_value"),
        "buying_power": account.get("buying_power"),
    }


def main() -> int:
    print("[Smoke] Validating Alpaca configuration...")

    missing_keys: list[str] = []
    if not settings.ALPACA_API_KEY:
        missing_keys.append("ALPACA_PAPER_API_KEY")
    if not settings.ALPACA_SECRET_KEY:
        missing_keys.append("ALPACA_PAPER_SECRET_KEY")

    if missing_keys:
        print(
            "[Smoke] ❌ Missing required environment variables:",
            ", ".join(missing_keys),
        )
        return 1

    if settings.TESTING:
        print("[Smoke] ⚠️ TESTING mode enabled – skipping live Alpaca call.")
        return 0

    try:
        client = get_alpaca_client()
        account = client.get_account()
    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"[Smoke] ❌ Alpaca verification failed: {exc}")
        return 1

    print("[Smoke] ✅ Alpaca credentials verified!")
    print(json.dumps(format_account_summary(account), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
