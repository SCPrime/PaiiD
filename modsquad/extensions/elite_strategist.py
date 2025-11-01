"""Elite Strategist - SUN TZU Squad Leader for Strategic Batch Planning.

The Art of Parallel Warfare: Analyzes task dependencies, orchestrates optimal batching,
and coordinates the creation of intersection maps for seamless integration.
"""

from __future__ import annotations

import json
import os
import requests
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

# Import SUN TZU squad members at module level (prevent circular import issues)
from . import task_graph_analyzer, risk_profiler, batch_optimizer, intersection_mapper

# Import ALPHA squad for pause/resume during batch execution
from modsquad.squads import alpha

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "elite_strategist"


def run(tasks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Orchestrate strategic batch planning for parallel task execution.

    Args:
        tasks: List of task dictionaries with 'id', 'description', 'files', 'dependencies'

    Returns:
        Batch plan with intersection points for ARMANI weaving
    """
    config = load_extension_config()
    settings = config.get("elite_strategist", {})

    if not settings.get("enabled", False):
        return {"status": "disabled", "reason": "Elite strategist not enabled"}

    # SAFETY: Block batching if server is running
    if not _is_safe_to_batch():
        return {
            "status": "blocked",
            "reason": "Backend or frontend server running - cannot batch system files",
            "fix": "Stop servers (Ctrl+C) or set MODSQUAD_ALLOW_LIVE_BATCHING=true (not recommended)",
            "safety_note": "Batching while servers are running can cause file corruption"
        }

    # Import foxtrot for batch lock
    from modsquad.squads import foxtrot

    # Acquire batch execution lock (prevents concurrent orchestration)
    if not foxtrot.acquire_batch_lock(timeout=60):
        return {
            "status": "locked",
            "reason": "Another batch execution or orchestration in progress",
            "fix": "Wait for current operation to complete"
        }

    # Pause ALPHA squad always-on tasks during batch execution
    alpha.pause_alpha_squad()

    try:
        # Phase 1: Build dependency graph
        dependency_graph = task_graph_analyzer.analyze(tasks or [])

        # Phase 2: Calculate risk profiles
        risk_profiles = risk_profiler.calculate(tasks or [], dependency_graph)

        # Phase 3: Optimize batching
        batch_plan = batch_optimizer.optimize(tasks or [], dependency_graph, risk_profiles)

        # Phase 4: Map intersection points
        intersections = intersection_mapper.map_intersections(batch_plan, dependency_graph)

        # Enrich batch plan with intersections
        batch_plan["intersections"] = intersections
        batch_plan["strategist_metadata"] = {
            "total_tasks": len(tasks or []),
            "total_batches": len(batch_plan.get("batches", [])),
            "parallelization_factor": _calculate_parallelization(batch_plan),
            "total_intersections": len(intersections),
            "estimated_speedup": _calculate_speedup(batch_plan),
        }

        # Persist batch plan
        dump_jsonl(
            ARTIFACT_DIR / "batch_plans.jsonl",
            {
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "batch_plan": batch_plan,
            },
        )

        return batch_plan
    finally:
        # Resume ALPHA squad always-on tasks
        alpha.resume_alpha_squad()
        # Release batch execution lock
        foxtrot.release_batch_lock()


def _is_safe_to_batch() -> bool:
    """
    Check if it's safe to execute batch modifications.

    Safety checks:
    - Environment override (MODSQUAD_ALLOW_LIVE_BATCHING)
    - Backend server running (localhost:8001)
    - Frontend dev server running (localhost:3000)

    Returns:
        True if safe to proceed, False if servers running
    """
    # Check environment override
    if os.getenv("MODSQUAD_ALLOW_LIVE_BATCHING", "false").lower() == "true":
        return True  # User explicitly allowed (use with caution)

    # Check if backend is running
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=1)
        if response.status_code == 200:
            return False  # Backend running, NOT safe
    except requests.exceptions.ConnectionError:
        pass  # Backend not running, safe
    except requests.exceptions.Timeout:
        pass  # Timeout, assume safe
    except Exception:
        pass  # Other error, assume safe

    # Check if frontend dev server is running
    try:
        response = requests.get("http://localhost:3000", timeout=1)
        if response.status_code in [200, 404]:  # Next.js returns 404 for API routes
            return False  # Frontend dev running, NOT safe
    except requests.exceptions.ConnectionError:
        pass  # Frontend not running, safe
    except requests.exceptions.Timeout:
        pass  # Timeout, assume safe
    except Exception:
        pass  # Other error, assume safe

    return True  # Safe to proceed


def _calculate_parallelization(batch_plan: dict[str, Any]) -> float:
    """Calculate what percentage of tasks can run in parallel."""
    batches = batch_plan.get("batches", [])
    if not batches:
        return 0.0

    total_tasks = sum(len(batch.get("tasks", [])) for batch in batches)
    max_parallel = max(len(batch.get("tasks", [])) for batch in batches)

    return round(max_parallel / total_tasks * 100, 1) if total_tasks > 0 else 0.0


def _calculate_speedup(batch_plan: dict[str, Any]) -> str:
    """Calculate estimated speedup from parallelization."""
    batches = batch_plan.get("batches", [])
    if not batches:
        return "0%"

    # Sequential time = sum of all task durations
    sequential_time = sum(
        task.get("estimated_duration", 60)
        for batch in batches
        for task in batch.get("tasks", [])
    )

    # Parallel time = sum of longest task per batch
    parallel_time = sum(
        max(
            (task.get("estimated_duration", 60) for task in batch.get("tasks", [])),
            default=60
        )
        for batch in batches
    )

    if sequential_time == 0:
        return "0%"

    speedup = round((1 - parallel_time / sequential_time) * 100, 1)
    return f"{speedup}%"


def strategize(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Public API for strategic batch planning."""
    return run(tasks)


def cli() -> None:
    run()
