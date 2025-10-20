#!/usr/bin/env python3
"""
Configuration Verification Script for PaiiD Backend
Run this to verify all API keys are properly loaded from .env

Usage:
    python verify_config.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# Load .env file
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"❌ ERROR: .env file not found at {env_path}")
    print("Create one using .env.example as a template")
    sys.exit(1)

load_dotenv(env_path)


def mask_key(key: str) -> str:
    """Mask API key for safe display"""
    if not key or len(key) < 12:
        return "NOT SET"
    return f"{key[:8]}...{key[-4:]}"


def verify_config():
    """Verify all required configuration is set"""
    print("[*] PaiiD Configuration Verification")
    print("=" * 60)
    print(f"Environment file: {env_path}")
    print("=" * 60)
    print()

    # Required configuration
    required_checks = {
        "Trading Configuration": [
            ("TRADING_MODE", os.getenv("TRADING_MODE")),
            ("LIVE_TRADING", os.getenv("LIVE_TRADING")),
        ],
        "Tradier Broker": [
            ("TRADIER_API_KEY", os.getenv("TRADIER_API_KEY")),
            ("TRADIER_ACCOUNT_ID", os.getenv("TRADIER_ACCOUNT_ID")),
            ("TRADIER_API_BASE_URL", os.getenv("TRADIER_API_BASE_URL")),
        ],
        "Anthropic Claude AI": [
            ("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY")),
            ("AI_MODEL", os.getenv("AI_MODEL")),
        ],
        "API Security": [
            ("API_TOKEN", os.getenv("API_TOKEN")),
            ("API_PORT", os.getenv("API_PORT")),
        ],
        "CORS": [
            ("ALLOW_ORIGIN", os.getenv("ALLOW_ORIGIN")),
        ],
    }

    all_good = True

    for category, checks in required_checks.items():
        print(f"\n[+] {category}")
        print("-" * 60)
        for name, value in checks:
            if value:
                # Mask sensitive values
                if "KEY" in name or "TOKEN" in name or "SECRET" in name:
                    display_value = mask_key(value)
                else:
                    display_value = value
                print(f"  [OK] {name:25} = {display_value}")
            else:
                print(f"  [FAIL] {name:25} = NOT SET")
                all_good = False

    # Optional configuration
    print("\n[+] Optional Configuration")
    print("-" * 60)
    optional_checks = [
        ("ALPHA_VANTAGE_API_KEY", os.getenv("ALPHA_VANTAGE_API_KEY")),
        ("POLYGON_API_KEY", os.getenv("POLYGON_API_KEY")),
        ("FINNHUB_API_KEY", os.getenv("FINNHUB_API_KEY")),
    ]

    for name, value in optional_checks:
        status = "[OK]" if value else "[SKIP]"
        display_value = mask_key(value) if value else "Not configured (optional)"
        print(f"  {status} {name:25} = {display_value}")

    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("[SUCCESS] All required configuration verified!")
        print("\nReady to start backend:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload --port 8001")
        print("\nAPI Documentation will be available at:")
        print("  http://127.0.0.1:8001/docs")
        return True
    else:
        print("[FAILURE] Missing required configuration!")
        print("\nPlease check your .env file and add missing values.")
        print("Use .env.example as a template.")
        return False


if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)
