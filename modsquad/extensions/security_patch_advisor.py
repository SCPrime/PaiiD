"""Security patch advisor for MOD SQUAD vulnerability tracking."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "security_patch_advisor"


def run() -> None:
    """Check for security vulnerabilities and advisories."""

    config = load_extension_config()
    settings = config.get("security_patch_advisor")
    if not settings or not settings.get("enabled", False):
        return

    results: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "python_audit": _check_python_deps(),
        "npm_audit": _check_npm_deps(),
    }

    dump_jsonl(ARTIFACT_DIR / "security_patch_advisor.jsonl", results)


def _check_python_deps() -> dict[str, Any]:
    """Run pip-audit on Python dependencies."""
    try:
        cmd = ["pip-audit", "--format", "json"]
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if completed.returncode == 0:
            try:
                audit_data = json.loads(completed.stdout)
                return {
                    "tool": "pip-audit",
                    "status": "clean",
                    "vulnerabilities": len(audit_data.get("vulnerabilities", [])),
                }
            except json.JSONDecodeError:
                return {
                    "tool": "pip-audit",
                    "status": "clean",
                    "vulnerabilities": 0,
                }
        else:
            return {
                "tool": "pip-audit",
                "status": "issues_found",
                "output": completed.stdout[:500],
            }
    except FileNotFoundError:
        return {
            "tool": "pip-audit",
            "status": "not_installed",
            "message": "pip-audit not available (pip install pip-audit)",
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "tool": "pip-audit",
            "status": "error",
            "error": str(exc),
        }


def _check_npm_deps() -> dict[str, Any]:
    """Run npm audit on frontend dependencies."""
    try:
        cmd = ["npm", "audit", "--json"]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="frontend"
        )

        try:
            audit_data = json.loads(completed.stdout)
            vulnerabilities = audit_data.get("metadata", {}).get("vulnerabilities", {})
            total = sum(vulnerabilities.values())

            return {
                "tool": "npm-audit",
                "status": "clean" if total == 0 else "issues_found",
                "total_vulnerabilities": total,
                "breakdown": vulnerabilities,
            }
        except json.JSONDecodeError:
            return {
                "tool": "npm-audit",
                "status": "error",
                "error": "Failed to parse npm audit output",
            }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "tool": "npm-audit",
            "status": "error",
            "error": str(exc),
        }


def cli() -> None:
    run()


__all__ = ["run"]
