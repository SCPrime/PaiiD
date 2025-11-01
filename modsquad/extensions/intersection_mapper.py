"""Intersection Mapper - Pre-identifies exact merge points for batch weaving.

Part of SUN TZU Squad for strategic batch planning. Analyzes batch plans to
identify intersection points where parallel batches must be woven together,
enabling ARMANI squad to orchestrate seamless integration.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "intersection_mapper"

__all__ = ["map_intersections"]


def map_intersections(
    batch_plan: dict[str, Any], dependency_graph: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Pre-identify exact merge points where batches need weaving.

    Intersection types:
    1. File merge: Multiple batches modify the same file
    2. Import chain: Batch B imports code created by Batch A
    3. Function handoff: Batch B calls functions defined in Batch A
    4. Data flow: Batch B depends on data structures from Batch A

    Args:
        batch_plan: Output from batch_optimizer with batches and levels
        dependency_graph: Task dependency mapping

    Returns:
        List of intersection point dictionaries with merge instructions
    """
    config = load_extension_config()
    settings = config.get("intersection_mapper", {})

    if not settings.get("enabled", False):
        return []

    intersections = []

    # Build mapping of files to batches
    batch_files = _build_batch_file_mapping(batch_plan)

    # Build mapping of batch dependencies
    batch_deps = _build_batch_dependencies(batch_plan, dependency_graph)

    # Analyze each batch for intersections with other batches
    batches = batch_plan.get("batches", {})

    for batch_id, batch_info in batches.items():
        batch_level = batch_info.get("level", 0)
        batch_tasks = batch_info.get("tasks", [])
        batch_file_list = batch_info.get("files", [])

        # Find file-level intersections
        for file_path in batch_file_list:
            file_intersections = _analyze_file_intersections(
                file_path, batch_id, batch_level, batch_files, batch_deps
            )
            intersections.extend(file_intersections)

        # Find import chain intersections
        import_intersections = _analyze_import_intersections(
            batch_id, batch_level, batch_tasks, batch_deps, batches
        )
        intersections.extend(import_intersections)

        # Find function handoff intersections
        handoff_intersections = _analyze_handoff_intersections(
            batch_id, batch_level, batch_tasks, batch_deps, batches
        )
        intersections.extend(handoff_intersections)

    # Deduplicate and prioritize intersections
    intersections = _deduplicate_intersections(intersections)
    intersections = _prioritize_intersections(intersections)

    # Persist intersection map
    dump_jsonl(
        ARTIFACT_DIR / "intersection_maps.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "batch_plan_id": batch_plan.get("metadata", {}).get("total_batches", 0),
            "intersections": intersections,
            "total_intersections": len(intersections),
        },
    )

    return intersections


def _build_batch_file_mapping(batch_plan: dict[str, Any]) -> dict[str, list[str]]:
    """
    Build mapping of file paths to batch IDs that modify them.

    Args:
        batch_plan: Batch plan with batches and files

    Returns:
        Dictionary: {file_path: [batch_ids]}
    """
    file_to_batches = defaultdict(list)

    batches = batch_plan.get("batches", {})
    for batch_id, batch_info in batches.items():
        for file_path in batch_info.get("files", []):
            file_to_batches[file_path].append(batch_id)

    return dict(file_to_batches)


def _build_batch_dependencies(
    batch_plan: dict[str, Any], dependency_graph: dict[str, Any]
) -> dict[str, list[str]]:
    """
    Build mapping of batch dependencies from task dependencies.

    Args:
        batch_plan: Batch plan with task assignments
        dependency_graph: Task dependency mapping

    Returns:
        Dictionary: {batch_id: [dependent_batch_ids]}
    """
    # Build task to batch mapping
    task_to_batch = {}
    batches = batch_plan.get("batches", {})

    for batch_id, batch_info in batches.items():
        for task_id in batch_info.get("tasks", []):
            task_to_batch[task_id] = batch_id

    # Build batch dependency graph
    batch_deps = defaultdict(set)

    for task_id, task_dependencies in dependency_graph.items():
        task_batch = task_to_batch.get(task_id)
        if not task_batch:
            continue

        for dep_task_id in task_dependencies:
            dep_batch = task_to_batch.get(dep_task_id)
            if dep_batch and dep_batch != task_batch:
                batch_deps[task_batch].add(dep_batch)

    # Convert sets to lists
    return {k: list(v) for k, v in batch_deps.items()}


def _analyze_file_intersections(
    file_path: str,
    batch_id: str,
    batch_level: int,
    batch_files: dict[str, list[str]],
    batch_deps: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """
    Analyze file for intersections with other batches.

    Args:
        file_path: Path to file being analyzed
        batch_id: Current batch ID
        batch_level: Current batch level
        batch_files: Mapping of files to batches
        batch_deps: Batch dependency graph

    Returns:
        List of file intersection dictionaries
    """
    intersections = []

    # Find all batches that modify this file
    modifying_batches = batch_files.get(file_path, [])

    # If multiple batches modify the same file, create merge intersection
    if len(modifying_batches) > 1:
        for other_batch_id in modifying_batches:
            if other_batch_id != batch_id:
                intersections.append(
                    {
                        "type": "file_merge",
                        "priority": "high",
                        "source_batch": batch_id,
                        "target_batch": other_batch_id,
                        "location": file_path,
                        "description": f"File {file_path} modified by both {batch_id} and {other_batch_id}",
                        "integration_pattern": "three_way_merge",
                        "requires_conflict_resolution": True,
                        "level": batch_level,
                    }
                )

    return intersections


def _analyze_import_intersections(
    batch_id: str,
    batch_level: int,
    batch_tasks: list[str],
    batch_deps: dict[str, list[str]],
    batches: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Analyze import chain dependencies between batches.

    Args:
        batch_id: Current batch ID
        batch_level: Current batch level
        batch_tasks: Tasks in current batch
        batch_deps: Batch dependency graph
        batches: All batches

    Returns:
        List of import intersection dictionaries
    """
    intersections = []

    # Find batches that this batch depends on
    dependencies = batch_deps.get(batch_id, [])

    for dep_batch_id in dependencies:
        dep_batch_info = batches.get(dep_batch_id, {})
        dep_files = dep_batch_info.get("files", [])

        # Check if any files create modules that this batch might import
        for dep_file in dep_files:
            if dep_file.endswith(".py") and "__init__" not in dep_file:
                intersections.append(
                    {
                        "type": "import_chain",
                        "priority": "medium",
                        "source_batch": dep_batch_id,
                        "target_batch": batch_id,
                        "location": dep_file,
                        "description": f"Batch {batch_id} may import modules from {dep_file} created by {dep_batch_id}",
                        "integration_pattern": "import_prediction",
                        "requires_conflict_resolution": False,
                        "level": batch_level,
                    }
                )

    return intersections


def _analyze_handoff_intersections(
    batch_id: str,
    batch_level: int,
    batch_tasks: list[str],
    batch_deps: dict[str, list[str]],
    batches: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Analyze function handoff points between batches.

    Args:
        batch_id: Current batch ID
        batch_level: Current batch level
        batch_tasks: Tasks in current batch
        batch_deps: Batch dependency graph
        batches: All batches

    Returns:
        List of handoff intersection dictionaries
    """
    intersections = []

    # Find batches that depend on this batch
    dependent_batches = [
        b_id for b_id, deps in batch_deps.items() if batch_id in deps
    ]

    for dep_batch_id in dependent_batches:
        dep_batch_info = batches.get(dep_batch_id, {})
        dep_level = dep_batch_info.get("level", 0)

        # If dependent batch is at a later level, create handoff intersection
        if dep_level > batch_level:
            intersections.append(
                {
                    "type": "function_handoff",
                    "priority": "high",
                    "source_batch": batch_id,
                    "target_batch": dep_batch_id,
                    "location": "function_interface",
                    "description": f"Batch {dep_batch_id} calls functions defined in {batch_id}",
                    "integration_pattern": "handoff_function",
                    "requires_conflict_resolution": False,
                    "level": dep_level,
                }
            )

    return intersections


def _deduplicate_intersections(
    intersections: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Remove duplicate intersections based on type, source, target, and location.

    Args:
        intersections: List of intersection dictionaries

    Returns:
        Deduplicated list of intersections
    """
    seen = set()
    deduplicated = []

    for intersection in intersections:
        key = (
            intersection.get("type"),
            intersection.get("source_batch"),
            intersection.get("target_batch"),
            intersection.get("location"),
        )

        if key not in seen:
            seen.add(key)
            deduplicated.append(intersection)

    return deduplicated


def _prioritize_intersections(
    intersections: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Sort intersections by priority and level.

    Priority order:
    1. High priority first
    2. Lower level (earlier) first
    3. Conflict resolution required first

    Args:
        intersections: List of intersection dictionaries

    Returns:
        Sorted list of intersections
    """
    priority_order = {"high": 0, "medium": 1, "low": 2}

    def sort_key(intersection: dict[str, Any]) -> tuple:
        priority = priority_order.get(intersection.get("priority", "medium"), 1)
        level = intersection.get("level", 999)
        requires_resolution = not intersection.get("requires_conflict_resolution", False)
        return (priority, level, requires_resolution)

    return sorted(intersections, key=sort_key)


def cli() -> None:
    """CLI entry point for intersection mapper."""
    print("Intersection Mapper - SUN TZU Squad")
    print("Run via elite_strategist.run() for full intersection mapping")
