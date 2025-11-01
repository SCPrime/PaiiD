"""Command-line orchestrator for MOD SQUAD extensions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from . import (
    maintenance_notifier,
    metrics_streamer,
    secrets_watchdog,
    strategy_verifier,
)


def after_maintenance(
    window: str,
    status: str,
    metrics_json: Path | None,
    details_json: Path | None,
    run_verifier: bool,
) -> None:
    """Execute sequential extension suite after a maintenance batch."""

    details = load_json(details_json) if details_json else {}
    maintenance_notifier.run(window=window, status=status, details=details)

    metrics_payload: Dict[str, Any] = {
        "maintenance_window": window,
        "guardrail_status": status,
        "execution_time_ms": details.get("execution_time_ms", 0),
        "token_spend": details.get("token_spend", 0),
    }
    if metrics_json:
        metrics_payload.update(load_json(metrics_json))
    metrics_streamer.run(metrics_payload)

    secrets_watchdog.audit()

    if run_verifier:
        strategy_verifier.run()


def run_secrets_audit() -> None:
    secrets_watchdog.audit()


def run_strategy_verifier() -> None:
    strategy_verifier.run()


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return {"data": data}
    return data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run MOD SQUAD extension routines.")
    sub = parser.add_subparsers(dest="command", required=True)

    after = sub.add_parser(
        "after-maintenance", help="Run notifier/metrics/secrets (optional verifier)"
    )
    after.add_argument("--window", required=True, help="Maintenance window identifier")
    after.add_argument(
        "--status", default="complete", help="Maintenance outcome status"
    )
    after.add_argument("--metrics-json", type=Path, help="Path to metrics JSON payload")
    after.add_argument("--details-json", type=Path, help="Path to details JSON payload")
    after.add_argument(
        "--verify", action="store_true", help="Run strategy verifier commands"
    )

    sub.add_parser("secrets-audit", help="Run only the secrets watchdog")
    sub.add_parser("verify-strategies", help="Run only the strategy verifier commands")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "after-maintenance":
        after_maintenance(
            window=args.window,
            status=args.status,
            metrics_json=args.metrics_json,
            details_json=args.details_json,
            run_verifier=args.verify,
        )
    elif args.command == "secrets-audit":
        run_secrets_audit()
    elif args.command == "verify-strategies":
        run_strategy_verifier()


if __name__ == "__main__":
    main()
