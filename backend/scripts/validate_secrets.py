#!/usr/bin/env python3
"""
Secrets Validation Script

Validates environment secrets for security best practices:
- Checks if required secrets are set (not empty)
- Detects placeholder values (e.g., "your-api-key-here")
- Validates secret strength (minimum length requirements)
- Checks for common weak secrets
- Validates API key format where applicable

Usage:
    python scripts/validate_secrets.py

Exit Codes:
    0 - All secrets valid
    1 - Validation errors found

Environment:
    Reads from .env file in backend/ directory
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional


# ANSI color codes for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(message: str) -> None:
    """Print formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")


def print_success(message: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}[ERROR] {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}[WARNING] {message}{Colors.RESET}")


def print_info(message: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}[INFO] {message}{Colors.RESET}")


# Secret validation rules
REQUIRED_SECRETS = [
    "API_TOKEN",
    "TRADIER_API_KEY",
    "TRADIER_ACCOUNT_ID",
    "ALPACA_PAPER_API_KEY",
    "ALPACA_PAPER_SECRET_KEY",
    "DATABASE_URL",
    "JWT_SECRET_KEY",
]

OPTIONAL_SECRETS = [
    "ANTHROPIC_API_KEY",
    "GITHUB_WEBHOOK_SECRET",
    "REDIS_URL",
    "SENTRY_DSN",
]

# Placeholder values that should never be used
PLACEHOLDER_VALUES = [
    "your-api-key-here",
    "your-key-here",
    "placeholder",
    "change-me",
    "changeme",
    "replace-me",
    "example",
    "test",
    "demo",
    "sample",
    "xxx",
    "yyy",
    "zzz",
    "<your-key>",
    "<your-api-key>",
    "<your-secret>",
]

# Weak/common secrets (DO NOT USE)
WEAK_SECRETS = [
    "password",
    "secret",
    "admin",
    "root",
    "12345",
    "qwerty",
    "abc123",
    "password123",
    "admin123",
    "secret123",
    "dev-secret-key",
    "test-secret-key",
]

# Minimum length requirements
MIN_LENGTH_REQUIREMENTS = {
    "API_TOKEN": 20,
    "JWT_SECRET_KEY": 32,
    "GITHUB_WEBHOOK_SECRET": 20,
    "ALPACA_PAPER_API_KEY": 20,
    "ALPACA_PAPER_SECRET_KEY": 20,
}


def load_env_file(env_path: Path) -> dict:
    """
    Load environment variables from .env file.

    Args:
        env_path: Path to .env file

    Returns:
        Dictionary of environment variables
    """
    env_vars = {}

    if not env_path.exists():
        print_error(f".env file not found at: {env_path}")
        print_info("Create it from .env.example: cp .env.example .env")
        return env_vars

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value

    except Exception as e:
        print_error(f"Error reading .env file: {e}")

    return env_vars


def check_required_secrets(env_vars: dict) -> List[str]:
    """
    Check if all required secrets are set (non-empty).

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of error messages
    """
    errors = []

    for secret in REQUIRED_SECRETS:
        value = env_vars.get(secret, "")

        if not value:
            errors.append(f"{secret} is not set (REQUIRED)")
        elif len(value.strip()) == 0:
            errors.append(f"{secret} is empty (REQUIRED)")

    return errors


def check_placeholder_values(env_vars: dict) -> List[str]:
    """
    Check if secrets contain placeholder values.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of error messages
    """
    errors = []
    all_secrets = REQUIRED_SECRETS + OPTIONAL_SECRETS

    for secret in all_secrets:
        value = env_vars.get(secret, "").lower()

        if not value:
            continue

        for placeholder in PLACEHOLDER_VALUES:
            if placeholder in value.lower():
                errors.append(
                    f"{secret} contains placeholder value: '{placeholder}'"
                )
                break

    return errors


def check_weak_secrets(env_vars: dict) -> List[str]:
    """
    Check if secrets are weak/common passwords.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of error messages
    """
    errors = []
    secrets_to_check = ["API_TOKEN", "JWT_SECRET_KEY", "GITHUB_WEBHOOK_SECRET"]

    for secret in secrets_to_check:
        value = env_vars.get(secret, "").lower()

        if not value:
            continue

        for weak in WEAK_SECRETS:
            if weak in value.lower():
                errors.append(f"{secret} contains weak/common value: '{weak}'")
                break

    return errors


def check_minimum_length(env_vars: dict) -> List[str]:
    """
    Check if secrets meet minimum length requirements.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of error messages
    """
    errors = []

    for secret, min_length in MIN_LENGTH_REQUIREMENTS.items():
        value = env_vars.get(secret, "")

        if not value:
            continue

        if len(value) < min_length:
            errors.append(
                f"{secret} is too short ({len(value)} chars, minimum {min_length})"
            )

    return errors


def check_api_key_formats(env_vars: dict) -> List[Tuple[str, str]]:
    """
    Validate API key formats where applicable.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of (secret_name, warning_message) tuples
    """
    warnings = []

    # Anthropic API keys should start with sk-ant-api
    anthropic_key = env_vars.get("ANTHROPIC_API_KEY", "")
    if anthropic_key and not anthropic_key.startswith("sk-ant-api"):
        warnings.append(
            (
                "ANTHROPIC_API_KEY",
                "Format warning: Should start with 'sk-ant-api'",
            )
        )

    # Alpaca keys should be alphanumeric
    alpaca_api_key = env_vars.get("ALPACA_PAPER_API_KEY", "")
    if alpaca_api_key and not re.match(r"^[A-Z0-9]+$", alpaca_api_key):
        warnings.append(
            (
                "ALPACA_PAPER_API_KEY",
                "Format warning: Should be uppercase alphanumeric",
            )
        )

    alpaca_secret_key = env_vars.get("ALPACA_PAPER_SECRET_KEY", "")
    if alpaca_secret_key and not re.match(
        r"^[A-Za-z0-9/+=]+$", alpaca_secret_key
    ):
        warnings.append(
            (
                "ALPACA_PAPER_SECRET_KEY",
                "Format warning: Should be alphanumeric with /+=",
            )
        )

    # Database URL should start with postgresql:// or sqlite://
    database_url = env_vars.get("DATABASE_URL", "")
    if database_url:
        if not (
            database_url.startswith("postgresql://")
            or database_url.startswith("sqlite://")
        ):
            warnings.append(
                (
                    "DATABASE_URL",
                    "Format warning: Should start with 'postgresql://' or 'sqlite://'",
                )
            )

    return warnings


def check_optional_secrets(env_vars: dict) -> List[str]:
    """
    Check status of optional secrets.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of info messages
    """
    info = []

    for secret in OPTIONAL_SECRETS:
        value = env_vars.get(secret, "")

        if not value:
            info.append(f"{secret} not set (optional)")
        else:
            info.append(f"{secret} is configured")

    return info


def generate_secret_recommendations(env_vars: dict) -> List[str]:
    """
    Generate recommendations for secret generation.

    Args:
        env_vars: Dictionary of environment variables

    Returns:
        List of recommendation messages
    """
    recommendations = []

    # Check if secrets look randomly generated (high entropy)
    import string

    def has_high_entropy(value: str, min_unique_chars: int = 10) -> bool:
        """Check if string has high entropy (many unique characters)."""
        if len(value) < 20:
            return False
        unique_chars = len(set(value))
        return unique_chars >= min_unique_chars

    # API_TOKEN
    api_token = env_vars.get("API_TOKEN", "")
    if api_token and not has_high_entropy(api_token):
        recommendations.append(
            "API_TOKEN: Consider regenerating with: "
            "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    # JWT_SECRET_KEY
    jwt_secret = env_vars.get("JWT_SECRET_KEY", "")
    if jwt_secret and not has_high_entropy(jwt_secret):
        recommendations.append(
            "JWT_SECRET_KEY: Consider regenerating with: "
            "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    return recommendations


def main() -> int:
    """
    Main validation function.

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    print_header("PAIID SECRETS VALIDATION")

    # Find .env file
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    env_path = backend_dir / ".env"

    print_info(f"Checking environment file: {env_path}")

    # Load environment variables
    env_vars = load_env_file(env_path)

    if not env_vars:
        print_error("No environment variables found")
        return 1

    print_success(f"Loaded {len(env_vars)} environment variables")

    # Run all validation checks
    all_errors = []
    all_warnings = []

    print_header("VALIDATION CHECKS")

    # 1. Required secrets
    print_info("Checking required secrets...")
    errors = check_required_secrets(env_vars)
    if errors:
        all_errors.extend(errors)
        for error in errors:
            print_error(error)
    else:
        print_success("All required secrets are set")

    # 2. Placeholder values
    print_info("\nChecking for placeholder values...")
    errors = check_placeholder_values(env_vars)
    if errors:
        all_errors.extend(errors)
        for error in errors:
            print_error(error)
    else:
        print_success("No placeholder values detected")

    # 3. Weak secrets
    print_info("\nChecking for weak/common secrets...")
    errors = check_weak_secrets(env_vars)
    if errors:
        all_errors.extend(errors)
        for error in errors:
            print_error(error)
    else:
        print_success("No weak secrets detected")

    # 4. Minimum length
    print_info("\nChecking minimum length requirements...")
    errors = check_minimum_length(env_vars)
    if errors:
        all_errors.extend(errors)
        for error in errors:
            print_error(error)
    else:
        print_success("All secrets meet minimum length requirements")

    # 5. API key formats
    print_info("\nValidating API key formats...")
    warnings = check_api_key_formats(env_vars)
    if warnings:
        all_warnings.extend(warnings)
        for secret, warning in warnings:
            print_warning(f"{secret}: {warning}")
    else:
        print_success("All API key formats appear valid")

    # 6. Optional secrets status
    print_header("OPTIONAL SECRETS STATUS")
    info = check_optional_secrets(env_vars)
    for msg in info:
        if "not set" in msg:
            print_info(msg)
        else:
            print_success(msg)

    # 7. Recommendations
    recommendations = generate_secret_recommendations(env_vars)
    if recommendations:
        print_header("RECOMMENDATIONS")
        for rec in recommendations:
            print_info(rec)

    # Final summary
    print_header("VALIDATION SUMMARY")

    if all_errors:
        print_error(f"Found {len(all_errors)} error(s)")
        for error in all_errors:
            print(f"  - {error}")
        print()
        print_error("SECRET VALIDATION FAILED!")
        print_info("Fix the errors above and run validation again.")
        return 1

    if all_warnings:
        print_warning(f"Found {len(all_warnings)} warning(s)")
        for secret, warning in all_warnings:
            print(f"  - {secret}: {warning}")
        print()

    print_success("ALL SECRETS VALIDATED SUCCESSFULLY!")
    print_info("Your environment is properly configured.")

    # Additional security reminders
    print_header("SECURITY REMINDERS")
    print_info("1. Rotate secrets every 90-180 days (see docs/SECRETS_ROTATION_GUIDE.md)")
    print_info("2. Never commit .env files to version control")
    print_info("3. Use different secrets for dev/staging/production")
    print_info("4. Enable 2FA on all API provider accounts")
    print_info("5. Monitor logs for failed authentication attempts")

    return 0


if __name__ == "__main__":
    sys.exit(main())
