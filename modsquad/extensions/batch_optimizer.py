"""Batch Optimizer - Constraint satisfaction solver for maximum parallelization.

Part of SUN TZU Squad for strategic batch planning. Applies constraint satisfaction
to create optimal batches with maximum parallelization while respecting:
- Max 5 parallel batches
- <10% collision probability
- <0.5% risk per batch
- Topological ordering with cycle detection
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "batch_optimizer"

__all__ = ["optimize"]


# Constraint thresholds
MAX_PARALLEL_BATCHES = 5
MAX_BATCH_RISK = 0.005  # 0.5% per batch
MAX_COLLISION_PROBABILITY = 0.10  # 10% collision threshold


def optimize(
    tasks: list[dict[str, Any]],
    dependency_graph: dict[str, Any],
    risk_profiles: dict[str, Any],
) -> dict[str, Any]:
    """
    Optimize task batching to maximize parallelization under constraints.

    Args:
        tasks: List of task dictionaries with 'id', 'files', 'dependencies'
        dependency_graph: Task dependency mapping from task_graph_analyzer
        risk_profiles: Risk scores and collision probabilities from risk_profiler

    Returns:
        Batch plan with optimized task assignments and metadata
    """
    config = load_extension_config()
    settings = config.get("batch_optimizer", {})

    if not settings.get("enabled", False):
        return {"status": "disabled", "reason": "Batch optimizer not enabled"}

    # Step 1: Detect cycles in dependency graph
    if _has_cycles(dependency_graph):
        return {
            "status": "error",
            "reason": "Circular dependencies detected in task graph",
            "dependency_graph": dependency_graph,
        }

    # Step 2: Compute topological levels (independent tasks at same level)
    levels = _compute_topological_levels(tasks, dependency_graph)

    # Step 3: Create batches from levels while respecting constraints
    batches = _create_batches(levels, risk_profiles, tasks)

    # Step 4: Validate constraints
    validation = _validate_constraints(batches, risk_profiles)

    # Step 5: Compute metadata
    metadata = _compute_metadata(batches, tasks, validation)

    batch_plan = {
        "status": "success",
        "batches": batches,
        "levels": levels,
        "metadata": metadata,
        "validation": validation,
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


def _has_cycles(dependency_graph: dict[str, Any]) -> bool:
    """
    Detect cycles in dependency graph using depth-first search.

    Args:
        dependency_graph: {task_id: [dependent_task_ids]}

    Returns:
        True if cycles detected, False otherwise
    """
    visited = set()
    rec_stack = set()

    def dfs(node: str) -> bool:
        visited.add(node)
        rec_stack.add(node)

        for neighbor in dependency_graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True  # Cycle detected

        rec_stack.remove(node)
        return False

    for task_id in dependency_graph:
        if task_id not in visited:
            if dfs(task_id):
                return True

    return False


def _compute_topological_levels(
    tasks: list[dict[str, Any]], dependency_graph: dict[str, Any]
) -> list[list[str]]:
    """
    Compute topological levels using Kahn's algorithm.

    Tasks at the same level have no dependencies on each other and can
    be executed in parallel.

    Args:
        tasks: List of task dictionaries
        dependency_graph: Task dependency mapping

    Returns:
        List of levels, where each level is a list of task IDs
    """
    # Compute in-degree for each task
    in_degree = defaultdict(int)
    adj_list = defaultdict(list)

    all_task_ids = {task.get("id", "unknown") for task in tasks}

    for task_id in all_task_ids:
        in_degree[task_id] = 0

    for task_id, dependencies in dependency_graph.items():
        for dep in dependencies:
            adj_list[dep].append(task_id)
            in_degree[task_id] += 1

    # Start with tasks that have no dependencies
    queue = deque([task_id for task_id in all_task_ids if in_degree[task_id] == 0])

    levels = []

    while queue:
        # All tasks in current queue are at the same level
        current_level = list(queue)
        levels.append(current_level)

        # Process current level
        next_queue = deque()
        for task_id in current_level:
            for neighbor in adj_list[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)

        queue = next_queue

    return levels


def _create_batches(
    levels: list[list[str]],
    risk_profiles: dict[str, Any],
    tasks: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Create batches from topological levels while respecting risk constraints.

    Strategy:
    1. Tasks at the same level can potentially run in parallel
    2. Split levels into batches if collision probability exceeds threshold
    3. Limit to MAX_PARALLEL_BATCHES concurrent batches
    4. Ensure each batch stays below MAX_BATCH_RISK

    Args:
        levels: Topological levels from _compute_topological_levels
        risk_profiles: Risk scores and collision probabilities
        tasks: List of task dictionaries

    Returns:
        Dictionary of batches: {batch_id: {tasks, risk, level, ...}}
    """
    batches = {}
    batch_counter = 0
    task_map = {task.get("id", "unknown"): task for task in tasks}

    for level_idx, level_tasks in enumerate(levels):
        # Try to fit all tasks in this level into batches
        remaining_tasks = level_tasks.copy()

        while remaining_tasks:
            batch_id = f"batch_{batch_counter}"
            batch_tasks = []
            batch_risk = 0.0

            for task_id in remaining_tasks[:]:
                # Check if adding this task would violate constraints
                if _can_add_to_batch(
                    task_id, batch_tasks, batch_risk, risk_profiles, task_map
                ):
                    batch_tasks.append(task_id)
                    batch_risk += risk_profiles.get("individual", {}).get(task_id, 0.1)
                    remaining_tasks.remove(task_id)

            if batch_tasks:
                batches[batch_id] = {
                    "tasks": batch_tasks,
                    "level": level_idx,
                    "risk": round(batch_risk, 4),
                    "task_count": len(batch_tasks),
                    "files": _collect_batch_files(batch_tasks, task_map),
                }
                batch_counter += 1

            # Safety: prevent infinite loops
            if not batch_tasks and remaining_tasks:
                # Force at least one task into a batch
                task_id = remaining_tasks.pop(0)
                batch_id = f"batch_{batch_counter}"
                batches[batch_id] = {
                    "tasks": [task_id],
                    "level": level_idx,
                    "risk": risk_profiles.get("individual", {}).get(task_id, 0.1),
                    "task_count": 1,
                    "files": _collect_batch_files([task_id], task_map),
                }
                batch_counter += 1

    return batches


def _can_add_to_batch(
    task_id: str,
    batch_tasks: list[str],
    current_batch_risk: float,
    risk_profiles: dict[str, Any],
    task_map: dict[str, dict[str, Any]],
) -> bool:
    """
    Check if adding task_id to batch_tasks would violate constraints.

    Args:
        task_id: Task to potentially add
        batch_tasks: Current tasks in batch
        current_batch_risk: Current cumulative risk
        risk_profiles: Risk scores and collision probabilities
        task_map: Map of task_id to task dictionary

    Returns:
        True if task can be safely added, False otherwise
    """
    # Check individual risk
    task_risk = risk_profiles.get("individual", {}).get(task_id, 0.1)
    if current_batch_risk + task_risk > MAX_BATCH_RISK:
        return False

    # Check collision probability with existing batch tasks
    for existing_task_id in batch_tasks:
        pair_key_1 = f"{existing_task_id}+{task_id}"
        pair_key_2 = f"{task_id}+{existing_task_id}"

        collision_prob = risk_profiles.get("pairs", {}).get(
            pair_key_1, risk_profiles.get("pairs", {}).get(pair_key_2, 0.1)
        )

        if collision_prob > MAX_COLLISION_PROBABILITY:
            return False

    return True


def _collect_batch_files(
    task_ids: list[str], task_map: dict[str, dict[str, Any]]
) -> list[str]:
    """Collect all files modified by tasks in this batch."""
    files = set()
    for task_id in task_ids:
        task = task_map.get(task_id, {})
        files.update(task.get("files", []))
    return sorted(files)


def _validate_constraints(
    batches: dict[str, Any], risk_profiles: dict[str, Any]
) -> dict[str, Any]:
    """
    Validate that all constraints are satisfied.

    Args:
        batches: Generated batches
        risk_profiles: Risk scores and collision probabilities

    Returns:
        Validation results with pass/fail status
    """
    validation = {
        "passed": True,
        "violations": [],
        "warnings": [],
    }

    # Check batch count constraint
    if len(batches) > MAX_PARALLEL_BATCHES:
        validation["passed"] = False
        validation["violations"].append(
            f"Batch count {len(batches)} exceeds MAX_PARALLEL_BATCHES ({MAX_PARALLEL_BATCHES})"
        )

    # Check batch risk constraints
    for batch_id, batch_info in batches.items():
        batch_risk = batch_info.get("risk", 0.0)
        if batch_risk > MAX_BATCH_RISK:
            validation["passed"] = False
            validation["violations"].append(
                f"{batch_id} risk {batch_risk} exceeds MAX_BATCH_RISK ({MAX_BATCH_RISK})"
            )

    # Check collision probabilities within batches
    for batch_id, batch_info in batches.items():
        batch_tasks = batch_info.get("tasks", [])
        for i, task_a in enumerate(batch_tasks):
            for task_b in batch_tasks[i + 1 :]:
                pair_key_1 = f"{task_a}+{task_b}"
                pair_key_2 = f"{task_b}+{task_a}"

                collision_prob = risk_profiles.get("pairs", {}).get(
                    pair_key_1, risk_profiles.get("pairs", {}).get(pair_key_2, 0.0)
                )

                if collision_prob > MAX_COLLISION_PROBABILITY:
                    validation["passed"] = False
                    validation["violations"].append(
                        f"{batch_id}: collision probability {collision_prob} "
                        f"between {task_a} and {task_b} exceeds threshold "
                        f"({MAX_COLLISION_PROBABILITY})"
                    )

    return validation


def _compute_metadata(
    batches: dict[str, Any], tasks: list[dict[str, Any]], validation: dict[str, Any]
) -> dict[str, Any]:
    """
    Compute metadata about the batch plan.

    Args:
        batches: Generated batches
        tasks: Original task list
        validation: Validation results

    Returns:
        Metadata dictionary
    """
    total_tasks = len(tasks)
    total_batches = len(batches)

    # Compute max parallel tasks
    level_counts = defaultdict(int)
    for batch_info in batches.values():
        level = batch_info.get("level", 0)
        level_counts[level] += batch_info.get("task_count", 0)

    max_parallel = max(level_counts.values()) if level_counts else 0

    # Compute parallelization factor
    parallelization_factor = (
        round(max_parallel / total_tasks * 100, 1) if total_tasks > 0 else 0.0
    )

    return {
        "total_tasks": total_tasks,
        "total_batches": total_batches,
        "total_levels": len(set(b.get("level", 0) for b in batches.values())),
        "max_parallel_tasks": max_parallel,
        "parallelization_factor": f"{parallelization_factor}%",
        "constraints_satisfied": validation.get("passed", False),
        "total_files": len(
            set(f for b in batches.values() for f in b.get("files", []))
        ),
    }


def cli() -> None:
    """CLI entry point for batch optimizer."""
    print("Batch Optimizer - SUN TZU Squad")
    print("Run via elite_strategist.run() for full batch planning")
