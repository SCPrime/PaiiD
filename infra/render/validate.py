#!/usr/bin/env python3
"""Validate Render service configuration exports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent
REQUIRED_FIELDS = {
    "backend": {"name", "runtime", "plan", "region", "branch", "rootDir", "buildCommand", "startCommand"},
    "frontend": {"name", "runtime", "plan", "region", "branch", "rootDir", "buildCommand", "startCommand"},
}


def validate(service: str) -> None:
    config_path = CONFIG_DIR / f"{service}.json"
    if not config_path.exists():
        raise SystemExit(f"Missing Render export: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    missing = REQUIRED_FIELDS[service] - data.keys()
    if missing:
        raise SystemExit(f"{service} configuration missing keys: {', '.join(sorted(missing))}")

    if "env" not in data or not isinstance(data["env"], dict):
        raise SystemExit(f"{service} configuration must contain an 'env' object")

    print(f"✅ Render configuration for {service} validated")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Render service exports")
    parser.add_argument("--service", choices=REQUIRED_FIELDS.keys(), required=True)
    args = parser.parse_args()
    validate(args.service)


if __name__ == "__main__":
    main()
