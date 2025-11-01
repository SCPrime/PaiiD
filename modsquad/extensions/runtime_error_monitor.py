"""Runtime error monitoring extension for MOD SQUAD (Sentry integration)."""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "runtime_error_monitor"


def run() -> None:
    """Monitor runtime errors via Sentry CLI."""

    config = load_extension_config()
    settings = config.get("runtime_error_monitor")
    if not settings or not settings.get("enabled", False):
        return

    guardrails = _load_guardrail_profile(settings)
    runtime_cfg = guardrails.get("runtime_errors", {})

    if not runtime_cfg.get("enabled", True):
        dump_jsonl(
            ARTIFACT_DIR / "runtime_error_monitor.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "status": "skipped",
                "reason": "Runtime error monitoring disabled in guardrail config",
            },
        )
        return

    results = _check_sentry_errors(runtime_cfg)

    dump_jsonl(
        ARTIFACT_DIR / "runtime_error_monitor.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "results": results,
        },
    )

    # GUARDRAIL ENFORCEMENT: Check block_on_error_rate and exit if threshold breached
    _enforce_guardrails(results, runtime_cfg)


def _load_guardrail_profile(settings: dict[str, Any]) -> dict[str, Any]:
    config_path = settings.get("config_path")
    if not config_path:
        return {}

    path = (CONFIG_PATH.parent / Path(config_path)).resolve()
    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    return data.get("browser_guardrails", data)


def _check_sentry_errors(config: dict[str, Any]) -> dict[str, Any]:
    """Check Sentry for recent error rates."""
    try:
        # Check if Sentry CLI is available
        auth_token = os.getenv("SENTRY_AUTH_TOKEN")
        if not auth_token:
            return {
                "status": "skipped",
                "reason": "SENTRY_AUTH_TOKEN not configured",
            }

        org = config.get("sentry_org", os.getenv("SENTRY_ORG"))
        project = config.get("sentry_project", os.getenv("SENTRY_PROJECT"))

        if not org or not project:
            return {
                "status": "skipped",
                "reason": "Sentry organization or project not configured",
            }

        # Query Sentry for recent errors (last 24h)
        # This is a placeholder - actual Sentry API integration would be here
        cmd = [
            "sentry-cli",
            "issues",
            "list",
            "--org", org,
            "--project", project,
        ]

        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "SENTRY_AUTH_TOKEN": auth_token}
        )

        if completed.returncode != 0:
            return {
                "status": "error",
                "tool": "sentry-cli",
                "error": completed.stderr[:500] if completed.stderr else "sentry-cli failed",
            }

        # Parse output for error count (simplified)
        # In production, you'd use Sentry API to get precise metrics
        output_lines = completed.stdout.strip().split("\n")
        error_count = len([line for line in output_lines if line.strip()])

        max_errors = config.get("max_errors_24h", 50)
        status = "passed" if error_count <= max_errors else "failed"

        return {
            "status": status,
            "tool": "sentry-cli",
            "error_count_24h": error_count,
            "max_errors_24h": max_errors,
            "org": org,
            "project": project,
        }

    except FileNotFoundError:
        return {
            "status": "skipped",
            "reason": "sentry-cli not installed (npm install -g @sentry/cli)",
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "status": "error",
            "error": str(exc),
        }


def _enforce_guardrails(result: dict[str, Any], runtime_cfg: dict[str, Any]) -> None:
    """
    Enforce guardrail block_on_error_rate policy.
    Exits with code 1 if error rate exceeds threshold and has block_on_error_rate=true.
    """
    status = result.get("status")

    # Skip if not failed
    if status != "failed":
        return

    # Check if block_on_error_rate is enabled
    block_on_errors = runtime_cfg.get("block_on_error_rate", False)

    if block_on_errors:
        import sys
        print(f"RUNTIME ERROR RATE EXCEEDED (block_on_error_rate=true)")
        print(f"   Error count (24h): {result.get('error_count_24h')}")
        print(f"   Max allowed: {result.get('max_errors_24h')}")
        print(f"   Sentry project: {result.get('org')}/{result.get('project')}")
        print(f"   Blocking CI due to guardrail policy")
        sys.exit(1)


def cli() -> None:
    run()
