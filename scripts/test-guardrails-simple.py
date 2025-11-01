#!/usr/bin/env python3
"""Standalone test script for MOD SQUAD guardrail extensions (bypasses full modsquad init)."""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

# Import only what we need, bypassing modsquad.__init__


def test_infra_health():
    """Test infra_health extension directly."""
    print("[TEST] infra_health extension...")
    try:
        # Import and run directly
        from modsquad.extensions.infra_health import run

        run()
        print("[OK] infra_health completed")
        return True
    except Exception as e:
        print(f"[WARN] infra_health: {e}")
        return False


def test_browser_validator():
    """Test browser_validator extension directly."""
    print("[TEST] browser_validator extension...")
    try:
        from modsquad.extensions.browser_validator import run

        run()
        print("[OK] browser_validator completed (check logs for results)")
        return True
    except Exception as e:
        print(f"[WARN] browser_validator: {e}")
        return False


def test_contract_enforcer():
    """Test contract_enforcer extension directly."""
    print("[TEST] contract_enforcer extension...")
    try:
        from modsquad.extensions.contract_enforcer import run

        run()
        print("[OK] contract_enforcer completed (check logs for results)")
        return True
    except Exception as e:
        print(f"[WARN] contract_enforcer: {e}")
        return False


if __name__ == "__main__":
    print("[OK] Testing MOD SQUAD Guardrail Extensions")
    print()

    results = []
    results.append(("infra_health", test_infra_health()))
    print()
    results.append(("browser_validator", test_browser_validator()))
    print()
    results.append(("contract_enforcer", test_contract_enforcer()))

    print()
    print("[OK] Guardrail test suite complete!")
    print("Check logs in: modsquad/logs/run-history/")
    print()
    print("Summary:")
    for name, success in results:
        status = "[OK]" if success else "[WARN]"
        print(f"  {status} {name}")
