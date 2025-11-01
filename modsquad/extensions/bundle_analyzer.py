"""Bundle size analysis extension for MOD SQUAD."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "bundle_analyzer"
NPX = "npx.cmd" if os.name == "nt" else "npx"


def run() -> None:
    """Analyze webpack bundle sizes and enforce guardrails."""

    config = load_extension_config()
    settings = config.get("bundle_analyzer")
    if not settings or not settings.get("enabled", False):
        return

    guardrails = _load_guardrail_profile(settings)
    bundle_cfg = guardrails.get("bundle_analysis", {})

    if not bundle_cfg.get("enabled", True):
        dump_jsonl(
            ARTIFACT_DIR / "bundle_analyzer.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "status": "skipped",
                "reason": "Bundle analysis disabled in guardrail config",
            },
        )
        return

    frontend_dir = Path(__file__).parent.parent.parent / "frontend"
    results = _analyze_bundle(frontend_dir, bundle_cfg)

    dump_jsonl(
        ARTIFACT_DIR / "bundle_analyzer.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "results": results,
        },
    )

    # GUARDRAIL ENFORCEMENT: Check block_on_size_breach and exit if bundle too large
    _enforce_guardrails(results, bundle_cfg)


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


def _analyze_bundle(frontend_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Analyze Next.js bundle sizes."""
    try:
        # Check if build exists
        build_dir = frontend_dir / ".next"
        if not build_dir.exists():
            return {
                "status": "skipped",
                "reason": "No .next build directory found (run npm run build first)",
            }

        # Read build manifest
        manifest_path = build_dir / "build-manifest.json"
        if not manifest_path.exists():
            return {
                "status": "error",
                "reason": "build-manifest.json not found",
            }

        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Calculate total bundle size
        total_size_kb = 0
        page_sizes = {}

        for page, files in manifest.get("pages", {}).items():
            page_size = 0
            for file_path in files:
                full_path = build_dir / file_path
                if full_path.exists():
                    page_size += full_path.stat().st_size / 1024  # Convert to KB

            page_sizes[page] = round(page_size, 2)
            total_size_kb += page_size

        total_size_kb = round(total_size_kb, 2)
        max_size_kb = config.get("max_bundle_size_kb", 500)

        status = "passed" if total_size_kb <= max_size_kb else "failed"

        return {
            "status": status,
            "total_size_kb": total_size_kb,
            "max_size_kb": max_size_kb,
            "page_sizes": page_sizes,
            "largest_pages": sorted(
                page_sizes.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    except Exception as exc:  # pragma: no cover - file system safety
        return {
            "status": "error",
            "error": str(exc),
        }


def _enforce_guardrails(result: dict[str, Any], bundle_cfg: dict[str, Any]) -> None:
    """
    Enforce guardrail block_on_size_breach policy.
    Exits with code 1 if bundle exceeds max size and has block_on_size_breach=true.
    """
    status = result.get("status")

    # Skip if not failed
    if status != "failed":
        return

    # Check if block_on_size_breach is enabled
    block_on_breach = bundle_cfg.get("block_on_size_breach", False)

    if block_on_breach:
        import sys
        print(f"BUNDLE SIZE BREACH DETECTED (block_on_size_breach=true)")
        print(f"   Total size: {result.get('total_size_kb')}KB")
        print(f"   Max allowed: {result.get('max_size_kb')}KB")
        print(f"   Largest pages: {result.get('largest_pages', [])[:3]}")
        print(f"   Blocking CI due to guardrail policy")
        sys.exit(1)


def cli() -> None:
    run()
