"""
SUN TZU SQUAD - Strategic Batch Planning
Mission: The Art of Parallel Warfare - Optimize task batching for maximum parallelization
Risk Profile: <2% with constraint satisfaction | On-Demand Planning
"""

from typing import Any

from modsquad.extensions import (
    batch_optimizer,
    elite_strategist,
    intersection_mapper,
    risk_profiler,
    task_graph_analyzer,
)

MEMBERS = [
    {"name": "elite_strategist", "module": elite_strategist, "role": "leader"},
    {
        "name": "task_graph_analyzer",
        "module": task_graph_analyzer,
        "role": "dependency_analysis",
    },
    {"name": "risk_profiler", "module": risk_profiler, "role": "collision_detection"},
    {"name": "batch_optimizer", "module": batch_optimizer, "role": "parallelization"},
    {
        "name": "intersection_mapper",
        "module": intersection_mapper,
        "role": "integration_planning",
    },
]

_LAST_BATCH_PLAN = None


def status():
    """Get SUN TZU SQUAD status."""
    return {
        "active": _LAST_BATCH_PLAN is not None,
        "members": len(MEMBERS),
        "last_batch_plan": _LAST_BATCH_PLAN,
        "risk": "<2%",
        "mission": "Strategic Batch Planning",
    }


def plan(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Create strategic batch plan for parallel task execution.

    Args:
        tasks: List of task dicts with 'id', 'description', 'files', 'dependencies'

    Returns:
        Batch plan with:
        - batches: Optimized parallel task groups
        - intersections: Predetermined merge points
        - metadata: Parallelization metrics and estimated speedup
    """
    global _LAST_BATCH_PLAN

    if not tasks:
        return {
            "squad": "sun_tzu",
            "status": "no_tasks",
            "message": "No tasks provided for batching",
        }

    print(f"\n[SUN TZU SQUAD] Planning batch execution for {len(tasks)} tasks...")

    # Deploy elite strategist (leader) to orchestrate planning
    try:
        batch_plan = elite_strategist.run(tasks)

        _LAST_BATCH_PLAN = batch_plan

        # Cache batch plan for ARMANI squad (lock-free handoff)
        from modsquad.universal_loader import REGISTRY
        import uuid

        plan_id = batch_plan.get("metadata", {}).get("plan_id", str(uuid.uuid4()))
        REGISTRY.cache_set(f"batch_plan:{plan_id}", batch_plan)
        REGISTRY.cache_set(f"intersections:{plan_id}", batch_plan.get("intersections", []))

        # Print summary
        metadata = batch_plan.get("strategist_metadata", {})
        print(f"   Total Tasks: {metadata.get('total_tasks', len(tasks))}")
        print(f"   Batches Created: {metadata.get('total_batches', 0)}")
        print(f"   Parallelization: {metadata.get('parallelization_factor', 0)}%")
        print(f"   Estimated Speedup: {metadata.get('estimated_speedup', '0%')}")
        print(f"   Intersection Points: {metadata.get('total_intersections', 0)}")
        print(f"   [OK] Cached to registry: batch_plan:{plan_id}")

        return {
            "squad": "sun_tzu",
            "status": "success",
            "batch_plan": batch_plan,
            "plan_id": plan_id,
            "members_deployed": [m["name"] for m in MEMBERS],
        }

    except Exception as e:
        print(f"   [ERROR] Batch planning failed: {str(e)}")
        return {
            "squad": "sun_tzu",
            "status": "error",
            "error": str(e),
        }


def analyze_dependencies(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Quick dependency analysis without full batch planning."""
    try:
        dependency_graph = task_graph_analyzer.analyze(tasks)
        return {
            "status": "success",
            "dependency_graph": dependency_graph,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def calculate_risk(
    tasks: list[dict[str, Any]], dependency_graph: dict[str, Any]
) -> dict[str, Any]:
    """Quick risk calculation for task parallelization."""
    try:
        risk_profiles = risk_profiler.calculate(tasks, dependency_graph)
        return {
            "status": "success",
            "risk_profiles": risk_profiles,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


__all__ = ["status", "plan", "analyze_dependencies", "calculate_risk", "MEMBERS"]
