#!/usr/bin/env python3
"""Standalone test script for MOD SQUAD guardrail extensions."""

import importlib
import os
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

# Ensure guardrail targets point to local dev services unless already set
os.environ.setdefault("PRODUCTION_URL", "http://localhost:3000")
os.environ.setdefault("BACKEND_API_BASE_URL", "http://localhost:8002")


def _load_guardrail_runner(module_name: str):
    """Import a guardrail extension and return its run() function."""
    module = importlib.import_module(f"modsquad.extensions.{module_name}")
    return getattr(module, "run")


if __name__ == "__main__":
    print("[OK] Testing MOD SQUAD Guardrail Extensions")
    print()

    infra_health_run = _load_guardrail_runner("infra_health")
    browser_validator_run = _load_guardrail_runner("browser_validator")
    contract_enforcer_run = _load_guardrail_runner("contract_enforcer")

    # Test 1: Infrastructure Health
    print("[TEST] infra_health extension...")
    try:
        infra_health_run()
        print("[OK] infra_health completed")
    except Exception as e:
        print(f"[WARN] infra_health: {e}")

    print()

    # Test 2: Browser Validator (may fail if frontend not running)
    print("[TEST] browser_validator extension...")
    try:
        browser_validator_run()
        print("[OK] browser_validator completed (check logs for results)")
    except Exception as e:
        print(f"[WARN] browser_validator: {e}")

    print()

    # Test 3: Contract Enforcer (may fail if backend not running)
    print("[TEST] contract_enforcer extension...")
    try:
        contract_enforcer_run()
        print("[OK] contract_enforcer completed (check logs for results)")
    except Exception as e:
        print(f"[WARN] contract_enforcer: {e}")

    print()
    print("[OK] Guardrail test suite complete!")
    print("Check logs in: modsquad/logs/run-history/")
