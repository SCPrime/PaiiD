"""Browser validation extension for MOD SQUAD."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "browser_validator"
NPX = "npx.cmd" if os.name == "nt" else "npx"
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def run() -> None:
    """Execute browser validation checks sequentially and persist results."""

    config = load_extension_config()
    settings = config.get("browser_validator")
    if not settings or not settings.get("enabled", False):
        return

    guardrails = _load_guardrail_profile(settings)
    target_url = _resolve_target_url(settings)

    results: list[dict[str, Any]] = []

    accessibility_cfg = guardrails.get("accessibility")
    if accessibility_cfg and accessibility_cfg.get("tool") == "axe-core":
        results.append(_run_axe_core(target_url, accessibility_cfg))

    performance_cfg = guardrails.get("performance")
    if performance_cfg and performance_cfg.get("tool") == "lighthouse":
        results.append(_run_lighthouse(target_url, performance_cfg))

    visual_cfg = guardrails.get("visual_regression")
    if visual_cfg:
        tool = visual_cfg.get("tool", "argos")
        if tool == "argos":
            argos_result = _run_argos(target_url, visual_cfg)
            stderr = (argos_result.get("stderr") or "").lower()
            argos_cli_missing = "argos" in stderr and (
                "not recognized" in stderr
                or "argos: not found" in stderr
                or "command not found" in stderr
            )

            if argos_cli_missing:
                argos_result["status"] = "skipped"
                argos_result["reason"] = "Argos CLI unavailable"

            results.append(argos_result)

            if argos_cli_missing and visual_cfg.get("fallback_tool") == "playwright":
                fallback = _run_playwright_native(target_url, visual_cfg)
                fallback["note"] = "Argos CLI unavailable; executed Playwright fallback"
                results.append(fallback)
        elif tool == "playwright":
            results.append(_run_playwright_native(target_url, visual_cfg))
        else:
            # Default to Argos if tool not recognized
            results.append(_run_argos(target_url, visual_cfg))

    # Record remaining guardrails as informational placeholders
    for key in ("runtime_errors", "session_replay", "bundle_analysis"):
        if key in guardrails:
            results.append(
                {
                    "check": key,
                    "status": "not_automated",
                    "details": "Guardrail monitored by external services",
                }
            )

    dump_jsonl(
        ARTIFACT_DIR / "browser_validator.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "target_url": target_url,
            "results": results,
        },
    )

    # GUARDRAIL ENFORCEMENT: Check block_on_fail and exit if violations found
    _enforce_guardrails(results, guardrails)


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
    default = settings.get("default_target_url", "http://localhost:3000")
    return str(default).rstrip("/")


def _run_axe_core(base_url: str, config: dict[str, Any]) -> dict[str, Any]:
    """Run axe-core accessibility scan."""
    try:
        cmd = [NPX, "axe", base_url, "--exit"]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=FRONTEND_DIR,
        )
        score = 100 if completed.returncode == 0 else 0
        min_score = int(config.get("min_score", 90))
        status = "passed" if score >= min_score else "failed"
        return {
            "check": "accessibility",
            "tool": "axe-core",
            "status": status,
            "score": score,
            "min_score": min_score,
            "output": completed.stdout[:500],
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "check": "accessibility",
            "tool": "axe-core",
            "status": "error",
            "score": 0,
            "min_score": int(config.get("min_score", 90)),
            "error": str(exc),
        }


def _run_lighthouse(base_url: str, config: dict[str, Any]) -> dict[str, Any]:
    """Run Lighthouse performance audit with Web Vitals threshold enforcement."""
    try:
        cmd = [
            NPX,
            "lighthouse",
            base_url,
            "--output=json",
            "--quiet",
            "--chrome-flags=--headless",
        ]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=FRONTEND_DIR,
        )
        min_score = int(config.get("min_score", 85))

        if completed.returncode == 0 and completed.stdout:
            report = json.loads(completed.stdout)
            perf_score = int(report["categories"]["performance"]["score"] * 100)

            # Extract Web Vitals metrics
            audits = report.get("audits", {})
            fcp = (
                audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000
            )  # Convert to seconds
            tti = audits.get("interactive", {}).get("numericValue", 0) / 1000
            cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 0)

            # Check thresholds from config
            max_fcp = config.get("max_fcp_seconds", 1.8)
            max_tti = config.get("max_tti_seconds", 3.8)
            max_cls = config.get("max_cls", 0.1)

            # Determine if Web Vitals pass
            vitals_pass = fcp <= max_fcp and tti <= max_tti and cls <= max_cls
            overall_pass = perf_score >= min_score and vitals_pass

            status = "passed" if overall_pass else "failed"

            return {
                "check": "performance",
                "tool": "lighthouse",
                "status": status,
                "score": perf_score,
                "min_score": min_score,
                "web_vitals": {
                    "fcp": round(fcp, 2),
                    "max_fcp": max_fcp,
                    "fcp_pass": fcp <= max_fcp,
                    "tti": round(tti, 2),
                    "max_tti": max_tti,
                    "tti_pass": tti <= max_tti,
                    "cls": round(cls, 3),
                    "max_cls": max_cls,
                    "cls_pass": cls <= max_cls,
                },
                "error": completed.stderr[:500] if completed.stderr else "",
            }
        else:
            perf_score = 0
            status = "failed"
            return {
                "check": "performance",
                "tool": "lighthouse",
                "status": status,
                "score": perf_score,
                "min_score": min_score,
                "error": completed.stderr[:500] if completed.stderr else "",
            }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "check": "performance",
            "tool": "lighthouse",
            "status": "error",
            "score": 0,
            "min_score": int(config.get("min_score", 85)),
            "error": str(exc),
        }


def _run_argos(base_url: str, config: dict[str, Any]) -> dict[str, Any]:
    """Run Argos visual regression via Playwright tests."""
    try:
        # Run Playwright visual tests with Argos integration
        # Match files containing "argos" in the name or path
        cmd = [NPX, "playwright", "test", "tests/visual/argos-snapshots.spec.ts"]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=FRONTEND_DIR,
        )

        status = "passed" if completed.returncode == 0 else "failed"
        return {
            "check": "visual_regression",
            "tool": "argos",
            "status": status,
            "returncode": completed.returncode,
            "output": completed.stdout[:500] if completed.stdout else "",
            "stderr": completed.stderr[:500] if completed.stderr else "",
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "check": "visual_regression",
            "tool": "argos",
            "status": "error",
            "error": str(exc),
        }


def _run_playwright_native(base_url: str, config: dict[str, Any]) -> dict[str, Any]:
    """Run Playwright native visual tests (no-cost fallback to Argos)."""
    try:
        # Run only Playwright native tests (no Argos upload)
        cmd = [
            NPX,
            "playwright",
            "test",
            "tests/visual/critical-components.visual.spec.ts",
            "--project=chromium",
        ]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=FRONTEND_DIR,
        )

        status = "passed" if completed.returncode == 0 else "failed"
        return {
            "check": "visual_regression",
            "tool": "playwright_native",
            "status": status,
            "returncode": completed.returncode,
            "output": completed.stdout[:500] if completed.stdout else "",
            "stderr": completed.stderr[:500] if completed.stderr else "",
            "note": "Fallback mode - Playwright native tests only (no cloud upload)",
        }
    except Exception as exc:  # pragma: no cover - subprocess safety
        return {
            "check": "visual_regression",
            "tool": "playwright_native",
            "status": "error",
            "error": str(exc),
        }


def _enforce_guardrails(
    results: list[dict[str, Any]], guardrails: dict[str, Any]
) -> None:
    """
    Enforce guardrail block_on_fail policy.
    Exits with code 1 if any guardrail fails and has block_on_fail=true.
    """
    violations = []

    for result in results:
        check_name = result.get("check")
        status = result.get("status")

        # Skip if not failed or not a check
        if status != "failed" or not check_name:
            continue

        # Get guardrail config for this check
        guardrail_cfg = guardrails.get(check_name, {})
        block_on_fail = guardrail_cfg.get("block_on_fail", False)

        if block_on_fail:
            violations.append(
                {
                    "check": check_name,
                    "tool": result.get("tool"),
                    "score": result.get("score"),
                    "min_score": result.get("min_score"),
                }
            )

    if violations:
        import sys

        print(f"GUARDRAIL VIOLATIONS (block_on_fail=true): {len(violations)}")
        for v in violations:
            print(
                f"   FAIL {v['check']}: score {v.get('score')} < {v.get('min_score')} (tool: {v.get('tool')})"
            )
        print("   Blocking CI due to guardrail policy")
        sys.exit(1)


def cli() -> None:
    run()
