#!/usr/bin/env python3
"""CLI entry point for PaiiD backend pre-launch checks."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

# Ensure repository root is on the import path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.prelaunch import PrelaunchError, run_prelaunch_checks


def configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 0:
        level = logging.INFO
    elif verbosity >= 1:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PaiiD backend pre-launch checks")
    parser.add_argument(
        "--context",
        default=os.getenv("PRELAUNCH_CONTEXT", "cli"),
        help="Identifier for the caller (default: cli)",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Disable JSON payload output",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase log verbosity",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    logger = logging.getLogger("paiid.prelaunch.cli")

    try:
        report = run_prelaunch_checks(
            emit_json=not args.no_json,
            raise_on_error=True,
            context=args.context,
        )
        logger.info("Pre-launch checks completed with status=%s", report["status"])
        return 0
    except PrelaunchError as exc:
        logger.error("Pre-launch checks failed: %s", exc)
        return 1
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.exception("Unexpected error running pre-launch checks: %s", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
