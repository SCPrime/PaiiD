#!/usr/bin/env python3
"""
META-DASHBOARD - Real-time agent oversight and monitoring
Displays live execution status for all MOD SQUAD agents

Author: Dr. SC Prime
Date: October 31, 2025
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def load_latest_execution_log(logs_dir: Path) -> List[Dict[str, Any]]:
    """Load the latest execution log from JSONL files"""
    log_files = sorted(logs_dir.glob("execution_log_*.jsonl"))
    if not log_files:
        return []

    latest = log_files[-1]
    tasks = []
    with open(latest, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))
    return tasks


def calculate_metrics(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate dashboard metrics from task log"""
    if not tasks:
        return {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "in_progress": 0,
            "pending": 0,
            "errors": 0,
            "warnings": 0,
            "risk_rate": 0.0
        }

    # Get latest state of each task (JSONL may have multiple entries per task)
    latest_tasks = {}
    for task in tasks:
        task_id = task["task_id"]
        latest_tasks[task_id] = task

    completed = sum(1 for t in latest_tasks.values() if t["status"] == "completed")
    failed = sum(1 for t in latest_tasks.values() if t["status"] == "failed")
    in_progress = sum(1 for t in latest_tasks.values() if t["status"] == "in_progress")
    pending = sum(1 for t in latest_tasks.values() if t["status"] == "pending")

    total_errors = sum(len(t.get("errors", [])) for t in latest_tasks.values())
    total_warnings = sum(len(t.get("warnings", [])) for t in latest_tasks.values())

    return {
        "total": len(latest_tasks),
        "completed": completed,
        "failed": failed,
        "in_progress": in_progress,
        "pending": pending,
        "errors": total_errors,
        "warnings": total_warnings,
        "risk_rate": (total_errors / max(1, len(latest_tasks))) * 100
    }


def render_dashboard(tasks: List[Dict[str, Any]], metrics: Dict[str, Any], refresh_interval: int):
    """Render dashboard UI"""
    # Clear screen (Windows compatible)
    print("\033[2J\033[H", end="")

    # Header
    print("="*100)
    print(" "*30 + "META-ORCHESTRATOR LIVE DASHBOARD")
    print("="*100)
    print(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Refresh: Every {refresh_interval}s (Ctrl+C to exit)")
    print("")

    # Metrics Summary
    print("EXECUTION METRICS:")
    print("-"*100)
    print(f"  Total Tasks:      {metrics['total']:>5d}")
    print(f"  Completed:        {metrics['completed']:>5d}  [{_progress_bar(metrics['completed'], metrics['total'])}]")
    print(f"  In Progress:      {metrics['in_progress']:>5d}  [{_status_icon('in_progress')}]")
    print(f"  Failed:           {metrics['failed']:>5d}  [{_status_icon('failed')}]")
    print(f"  Pending:          {metrics['pending']:>5d}  [{_status_icon('pending')}]")
    print("")
    print(f"  Total Errors:     {metrics['errors']:>5d}")
    print(f"  Total Warnings:   {metrics['warnings']:>5d}")
    print("")

    # Risk Rate
    risk_rate = metrics['risk_rate']
    risk_status = "[OK]" if risk_rate < 0.5 else ("[WARN]" if risk_rate < 2.0 else "[CRITICAL]")
    print(f"  RISK RATE:        {risk_rate:>5.2f}%  {risk_status}")
    print("")

    # Recent Tasks (last 10)
    print("RECENT ACTIVITY:")
    print("-"*100)

    # Get latest state of each task
    latest_tasks = {}
    for task in tasks:
        task_id = task["task_id"]
        latest_tasks[task_id] = task

    # Sort by start time (most recent first)
    sorted_tasks = sorted(
        latest_tasks.values(),
        key=lambda t: t.get("start_time", ""),
        reverse=True
    )[:10]

    for task in sorted_tasks:
        status_icon = _status_icon(task["status"])
        agent = task.get("agent", "unknown")[:20].ljust(20)
        desc = task.get("description", "")[:50].ljust(50)
        duration = ""
        if task.get("duration_seconds"):
            duration = f"{task['duration_seconds']:.1f}s"
        print(f"  {status_icon} {agent} | {desc} | {duration}")

    print("")
    print("="*100)


def _status_icon(status: str) -> str:
    """Get status icon for task"""
    icons = {
        "completed": "[OK]   ",
        "failed": "[FAIL] ",
        "in_progress": "[EXEC] ",
        "pending": "[WAIT] "
    }
    return icons.get(status, "[???]  ")


def _progress_bar(completed: int, total: int, width: int = 30) -> str:
    """Generate ASCII progress bar"""
    if total == 0:
        return " " * width

    pct = completed / total
    filled = int(width * pct)
    bar = "#" * filled + "-" * (width - filled)
    return f"{bar} {pct*100:.0f}%"


def main():
    parser = argparse.ArgumentParser(description="META-DASHBOARD - Real-time agent monitoring")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds")
    parser.add_argument("--once", action="store_true", help="Display once and exit (no auto-refresh)")

    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    logs_dir = root / "modsquad" / "logs"

    if not logs_dir.exists():
        print(f"[ERROR] Logs directory not found: {logs_dir}")
        print("Run meta_orchestrator.py first to generate execution logs.")
        return 1

    try:
        while True:
            tasks = load_latest_execution_log(logs_dir)
            metrics = calculate_metrics(tasks)
            render_dashboard(tasks, metrics, args.refresh)

            if args.once:
                break

            time.sleep(args.refresh)

    except KeyboardInterrupt:
        print("\n\n[INFO] Dashboard stopped by user")
        return 0


if __name__ == "__main__":
    exit(main())
