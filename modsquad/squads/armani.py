"""
ARMANI SQUAD - Integration Weaving
Mission: Haute Couture Code Integration - Weave parallel batches into seamless whole
Risk Profile: <3% with conflict resolution & validation | On-Demand Weaving
"""

from typing import Any

from modsquad.extensions import (
    conflict_resolver,
    elite_weaver,
    glue_code_generator,
    integration_validator,
    interface_predictor,
    intersection_executor,
)

MEMBERS = [
    {"name": "elite_weaver", "module": elite_weaver, "role": "leader"},
    {
        "name": "interface_predictor",
        "module": interface_predictor,
        "role": "interface_analysis",
    },
    {
        "name": "glue_code_generator",
        "module": glue_code_generator,
        "role": "code_generation",
    },
    {
        "name": "conflict_resolver",
        "module": conflict_resolver,
        "role": "conflict_resolution",
    },
    {
        "name": "intersection_executor",
        "module": intersection_executor,
        "role": "execution",
    },
    {
        "name": "integration_validator",
        "module": integration_validator,
        "role": "validation",
    },
]

_LAST_WEAVE_RESULT = None


def status():
    """Get ARMANI SQUAD status."""
    return {
        "active": _LAST_WEAVE_RESULT is not None,
        "members": len(MEMBERS),
        "last_weave": _LAST_WEAVE_RESULT,
        "risk": "<3%",
        "mission": "Integration Weaving",
    }


def weave(batch_plan: dict[str, Any], batch_results: dict[str, Any]) -> dict[str, Any]:
    """
    Weave parallel batch results into seamless integrated codebase.

    Args:
        batch_plan: Output from SUN TZU squad (with intersections)
        batch_results: Completed batch execution results

    Returns:
        Weave result with:
        - intersections_executed: List of successful integrations
        - conflicts_resolved: List of resolved conflicts
        - validations: Validation results for each intersection
        - overall_status: 'success' or 'failed'
    """
    global _LAST_WEAVE_RESULT

    if not batch_plan or not batch_results:
        return {
            "squad": "armani",
            "status": "insufficient_input",
            "message": "Both batch_plan and batch_results required",
        }

    # Try to read intersections from cache first (lock-free read)
    from modsquad.universal_loader import REGISTRY

    plan_id = batch_plan.get("metadata", {}).get("plan_id")
    cached_intersections = None

    if plan_id:
        cached_intersections = REGISTRY.cache_get(f"intersections:{plan_id}")
        if cached_intersections:
            print(f"   [OK] Loaded intersections from cache: {plan_id}")

    intersections = cached_intersections or batch_plan.get("intersections", [])
    if not intersections:
        return {
            "squad": "armani",
            "status": "no_intersections",
            "message": "No intersection points to weave",
        }

    print(f"\n[ARMANI SQUAD] Weaving {len(intersections)} intersection points...")

    # Deploy elite weaver (leader) to orchestrate integration
    try:
        weave_result = elite_weaver.run(batch_plan, batch_results)

        _LAST_WEAVE_RESULT = weave_result

        # Print summary
        metadata = weave_result.get("weaver_metadata", {})
        print(f"   Intersections Executed: {metadata.get('intersections_executed', 0)}")
        print(f"   Conflicts Resolved: {metadata.get('conflicts_resolved', 0)}")
        print(f"   Validations Passed: {metadata.get('validations_passed', 0)}")
        print(f"   Overall Status: {weave_result.get('status', 'unknown').upper()}")

        return {
            "squad": "armani",
            "status": "success",
            "weave_result": weave_result,
            "members_deployed": [m["name"] for m in MEMBERS],
        }

    except Exception as e:
        print(f"   [ERROR] Integration weaving failed: {str(e)}")
        return {
            "squad": "armani",
            "status": "error",
            "error": str(e),
        }


def execute_intersection(
    intersection: dict[str, Any],
    glue_code: dict[str, Any],
    resolutions: list[dict[str, Any]],
) -> dict[str, Any]:
    """Execute a single intersection point."""
    try:
        result = intersection_executor.execute(intersection, glue_code, resolutions)
        return {
            "status": "success",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def validate_integration(integration_result: dict[str, Any]) -> dict[str, Any]:
    """Validate a completed integration."""
    try:
        validation = integration_validator.validate(integration_result)
        return {
            "status": "success",
            "validation": validation,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


def resolve_conflicts(
    batch_a_changes: dict[str, Any], batch_b_changes: dict[str, Any]
) -> dict[str, Any]:
    """Resolve conflicts between parallel batch changes."""
    try:
        resolution = conflict_resolver.resolve(batch_a_changes, batch_b_changes)
        return {
            "status": "success",
            "resolution": resolution,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


__all__ = [
    "status",
    "weave",
    "execute_intersection",
    "validate_integration",
    "resolve_conflicts",
    "MEMBERS",
]
