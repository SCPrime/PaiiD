#!/usr/bin/env python3
"""
Auto Status Update - Updates at-a-glance every 1 minute
Runs full audit every 5 minutes

Author: Meta-Orchestrator
Date: October 31, 2025
"""

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def get_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def run_command(cmd, timeout=120):
    """Run a command and capture output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def update_at_a_glance():
    """Update the at-a-glance status file with current timestamp"""
    root = Path(__file__).resolve().parents[1]
    status_file = root / "modsquad" / "STATUS_AT_A_GLANCE.md"

    timestamp = get_timestamp()
    next_update = datetime.now(timezone.utc)
    next_update = next_update.replace(second=0, microsecond=0)
    from datetime import timedelta
    next_update = next_update + timedelta(minutes=1)
    next_update_str = next_update.strftime("%Y-%m-%d %H:%M:%S UTC")

    if status_file.exists():
        content = status_file.read_text(encoding="utf-8")

        # Update timestamp in header
        import re
        content = re.sub(
            r'\*\*Updated:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC',
            f'**Updated:** {timestamp}',
            content
        )

        # Update Last Refresh
        content = re.sub(
            r'\*\*Last Refresh:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC',
            f'**Last Refresh:** {timestamp}',
            content
        )

        # Update Last Update at bottom
        content = re.sub(
            r'\*\*Last Update:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC',
            f'**Last Update:** {timestamp}',
            content
        )

        # Update Next Update
        content = re.sub(
            r'\*\*Next Update:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC',
            f'**Next Update:** {next_update_str}',
            content
        )

        status_file.write_text(content, encoding="utf-8")
        print(f"[{timestamp}] At-a-glance updated")
        return True
    else:
        print(f"[{timestamp}] ERROR: Status file not found")
        return False


def run_full_audit():
    """Run full meta-orchestrator audit"""
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] === RUNNING FULL AUDIT ===")

    success, stdout, stderr = run_command(
        "python scripts/meta_orchestrator.py --mode quick --risk-target 0.5",
        timeout=180
    )

    if success:
        print(f"[{timestamp}] Full audit PASSED")
        # Extract key metrics
        if "RISK RATE:" in stdout:
            for line in stdout.split('\n'):
                if "RISK RATE:" in line or "Total Tasks:" in line or "Completed:" in line:
                    print(f"  {line.strip()}")
    else:
        print(f"[{timestamp}] Full audit had issues (non-blocking)")
        if stderr:
            print(f"  Error: {stderr[:200]}")

    print(f"[{timestamp}] === AUDIT COMPLETE ===\n")
    return success


def main():
    """Main loop - 1 min at-a-glance, 5 min full audit"""
    print(f"[INFO] Starting auto status update loop")
    print(f"[INFO] At-a-glance: Every 60 seconds")
    print(f"[INFO] Full audit: Every 5 minutes")
    print(f"[INFO] Press Ctrl+C to stop\n")

    minute_counter = 0

    try:
        while True:
            # Update at-a-glance every minute
            update_at_a_glance()

            # Run full audit every 5 minutes
            minute_counter += 1
            if minute_counter >= 5:
                run_full_audit()
                minute_counter = 0

            # Sleep for 60 seconds
            time.sleep(60)

    except KeyboardInterrupt:
        print(f"\n[INFO] Auto status update stopped by user")
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
