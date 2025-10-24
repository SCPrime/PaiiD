#!/usr/bin/env python3
"""Validate branch hold points defined in infra/git/hold-points.json."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "infra" / "git" / "hold-points.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise SystemExit(f"Hold point configuration missing: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def current_branch() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    config = load_config()
    branch = current_branch()
    protected = set(config.get("protectedBranches", []))
    pattern = config.get("releaseBranchPattern")
    bypass_env = config.get("allowBypassEnv")

    if branch in protected:
        if bypass_env and os.getenv(bypass_env):
            print(f"⚠️  {branch} is protected but {bypass_env} is set. Continuing.")
            return
        raise SystemExit(
            f"Branch '{branch}' is protected by infra/git/hold-points.json. "
            f"Set {bypass_env}=1 to override."
        )

    if pattern and re.match(pattern, branch):
        print(f"✅ Branch '{branch}' matches release pattern {pattern}")
    else:
        print(f"✅ Branch '{branch}' passes hold point checks")


if __name__ == "__main__":
    main()
