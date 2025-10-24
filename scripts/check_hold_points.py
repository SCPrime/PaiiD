#!/usr/bin/env python3
"""
Git Hold Point Validator

Checks compliance with .cursorrules and hold-points.json.
Validates locked files haven't been modified without approval.
"""

import json
import subprocess
import sys
from pathlib import Path


def check_locked_files(config):
    """Check if locked files have been modified"""
    locked_files = config.get("locked_files", [])

    # Get modified files in current branch
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True,
    )

    modified_files = result.stdout.strip().split("\n")

    # Check for locked file modifications
    violations = [f for f in modified_files if f in locked_files]

    if violations:
        print(f"❌ Locked files modified: {violations}")
        print("   Requires approval from Dr. SC Prime")
        return False

    print("✅ No locked files modified")
    return True


def main():
    config_path = Path(__file__).parent.parent / "infra" / "git" / "hold-points.json"

    with open(config_path) as f:
        config = json.load(f)

    success = check_locked_files(config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
