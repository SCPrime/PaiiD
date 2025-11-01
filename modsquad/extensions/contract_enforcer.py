"""API contract enforcement extension for MOD SQUAD."""

from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

NPX = "npx.cmd" if os.name == "nt" else "npx"
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "contract_enforcer"


def run() -> None:
    """Execute API contract validation."""

    config = load_extension_config()
    settings = config.get("contract_enforcer")
    if not settings or not settings.get("enabled", False):
        return

    guardrails = _load_guardrail_profile(settings)
    contract_cfg = guardrails.get("contract_testing", {})

    if not contract_cfg.get("enabled", True):
        dump_jsonl(
            ARTIFACT_DIR / "contract_enforcer.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "status": "skipped",
                "reason": "Contract testing disabled in guardrail config",
            },
        )
        return

    spec_path = contract_cfg.get("spec_path") or settings.get(
        "spec_path", "backend/docs/openapi.yaml"
    )
    target_url = _resolve_target_url(settings)

    results = _run_dredd(spec_path, target_url)

    dump_jsonl(
        ARTIFACT_DIR / "contract_enforcer.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "spec_path": spec_path,
            "target_url": target_url,
            "result": results,
        },
    )

    # GUARDRAIL ENFORCEMENT: Check block_on_drift and exit if contract fails
    _enforce_guardrails(results, contract_cfg)


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


def _resolve_target_url(settings: dict[str, Any]) -> str:
    env_key = settings.get("target_url_env")
    if env_key:
        env_value = os.getenv(env_key)
        if env_value:
            return env_value.rstrip("/")
    default = settings.get("default_target_url", "http://localhost:8001")
    return str(default).rstrip("/")


def _run_dredd(spec_path: str, base_url: str) -> dict[str, Any]:
    """Run Dredd contract tests."""
    try:
        repo_root = CONFIG_PATH.parent.parent
        spec_path_obj = Path(spec_path)
        if not spec_path_obj.is_absolute():
            spec_path_obj = (repo_root / spec_path_obj).resolve()

        cmd = [NPX, "dredd", str(spec_path_obj), base_url]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=FRONTEND_DIR,
        )
        status = "passed" if completed.returncode == 0 else "failed"
        return {
            "tool": "dredd",
            "status": status,
            "returncode": completed.returncode,
            "stdout": completed.stdout[:1000],
            "stderr": completed.stderr[:500] if completed.stderr else "",
        }
    except FileNotFoundError:
        return {
            "tool": "dredd",
            "status": "error",
            "error": "dredd not installed (npm install -g dredd)",
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "tool": "dredd",
            "status": "error",
            "error": str(exc),
        }


def _enforce_guardrails(result: dict[str, Any], contract_cfg: dict[str, Any]) -> None:
    """
    Enforce guardrail block_on_drift policy.
    Exits with code 1 if contract test fails and has block_on_drift=true.
    """
    status = result.get("status")

    # Skip if not failed
    if status != "failed":
        return

    # Check if block_on_drift is enabled
    block_on_drift = contract_cfg.get("block_on_drift", False)

    if block_on_drift:
        import sys

        print("API CONTRACT DRIFT DETECTED (block_on_drift=true)")
        print(f"   Tool: {result.get('tool')}")
        print(f"   Return code: {result.get('returncode')}")
        print("   Blocking CI due to guardrail policy")
        sys.exit(1)


def cli() -> None:
    run()
