"""Risk Profiler - Calculates collision probability between parallel tasks.

Part of SUN TZU Squad for strategic batch planning.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any


def calculate(
    tasks: list[dict[str, Any]], dependency_graph: dict[str, Any]
) -> dict[str, Any]:
    """
    Calculate risk profiles for each task and task pair.

    Args:
        tasks: List of task dictionaries
        dependency_graph: Output from task_graph_analyzer

    Returns:
        Risk profiles: {task_id: risk_score, (task_a, task_b): collision_probability}
    """
    # Convert tasks and dependency_graph to JSON for consistent hashing and caching
    tasks_json = json.dumps(tasks, sort_keys=True, default=str)
    graph_json = json.dumps(dependency_graph, sort_keys=True, default=str)
    return _calculate_cached(tasks_json, graph_json)


@lru_cache(maxsize=128)
def _calculate_cached(tasks_json: str, graph_json: str) -> dict[str, Any]:
    """
    Cached calculation of risk profiles for each task and task pair.

    Args:
        tasks_json: JSON-serialized list of tasks
        graph_json: JSON-serialized dependency graph

    Returns:
        Risk profiles: {task_id: risk_score, (task_a, task_b): collision_probability}
    """
    tasks = json.loads(tasks_json)
    dependency_graph = json.loads(graph_json)
    risk_profiles = {"individual": {}, "pairs": {}}

    # Calculate individual task risk
    for task in tasks:
        task_id = task.get("id", "unknown")
        risk_score = _calculate_individual_risk(task)
        risk_profiles["individual"][task_id] = risk_score

    # Calculate pairwise collision probability
    for i, task_a in enumerate(tasks):
        for task_b in tasks[i + 1 :]:
            task_a_id = task_a.get("id", "unknown")
            task_b_id = task_b.get("id", "unknown")

            collision_prob = _calculate_collision_probability(
                task_a, task_b, dependency_graph
            )

            pair_key = f"{task_a_id}+{task_b_id}"
            risk_profiles["pairs"][pair_key] = collision_prob

    return risk_profiles


def _calculate_individual_risk(task: dict[str, Any]) -> float:
    """
    Calculate risk score for a single task based on complexity.

    Risk factors:
    - Number of files modified
    - Presence of database migrations
    - External API calls
    - Critical system files
    """
    risk_score = 0.0

    files = task.get("files", [])
    file_count = len(files)

    # Base risk from file count
    if file_count == 1:
        risk_score += 0.1
    elif file_count <= 3:
        risk_score += 0.2
    elif file_count <= 5:
        risk_score += 0.3
    else:
        risk_score += 0.5

    # Critical file patterns (higher risk)
    critical_patterns = [
        "main.py",
        "__init__.py",
        "config.py",
        "database.py",
        "migrations/",
    ]

    for file_path in files:
        for pattern in critical_patterns:
            if pattern in file_path:
                risk_score += 0.1
                break

    # Database migrations (high risk)
    if any("migrations" in f or "alembic" in f for f in files):
        risk_score += 0.2

    # Cap risk score at 0.5% (our per-extension threshold)
    return min(risk_score, 0.5)


def _calculate_collision_probability(
    task_a: dict[str, Any],
    task_b: dict[str, Any],
    dependency_graph: dict[str, Any],
) -> float:
    """
    Calculate probability that task_a and task_b will collide if run in parallel.

    Collision factors:
    - File overlap
    - Dependency relationship
    - Directory overlap
    """
    task_a_id = task_a.get("id", "unknown")
    task_b_id = task_b.get("id", "unknown")

    # Check for explicit dependencies
    if task_b_id in dependency_graph.get(task_a_id, []):
        return 1.0  # 100% collision (sequential dependency)

    if task_a_id in dependency_graph.get(task_b_id, []):
        return 1.0  # 100% collision (sequential dependency)

    files_a = set(task_a.get("files", []))
    files_b = set(task_b.get("files", []))

    # Exact file overlap
    file_overlap = files_a & files_b
    if file_overlap:
        return 0.9  # 90% collision (same file modification)

    # Directory overlap (same parent directory)
    dirs_a = {str(Path(f).parent) for f in files_a}
    dirs_b = {str(Path(f).parent) for f in files_b}

    dir_overlap = dirs_a & dirs_b
    if dir_overlap:
        # Calculate overlap percentage
        overlap_pct = len(dir_overlap) / max(len(dirs_a), len(dirs_b))
        return overlap_pct * 0.5  # Up to 50% collision for directory overlap

    # No overlap detected
    return 0.1  # 10% base collision probability (unknown factors)
