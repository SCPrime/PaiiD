"""CLI entry point to run strategies via API."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests


def run_strategy(base_url: str, token: str, strategy_type: str, dry_run: bool) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/api/strategies/run"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        url,
        headers=headers,
        json={"strategy_type": strategy_type, "dry_run": dry_run},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run PaiiD strategy engine")
    parser.add_argument("strategy", help="Strategy type, e.g. under4-multileg")
    parser.add_argument("--base-url", default=os.getenv("PAIID_API_BASE", "http://127.0.0.1:8011"))
    parser.add_argument("--token", default=os.getenv("PAIID_API_TOKEN"), help="Bearer token for auth")
    parser.add_argument("--live", action="store_true", help="Execute live (default dry run)")
    parser.add_argument("--output", type=Path, help="Path to write JSON results")

    args = parser.parse_args(argv)

    if not args.token:
        parser.error("API token required via --token or PAIID_API_TOKEN env var")

    result = run_strategy(args.base_url, args.token, args.strategy, not args.live)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()

