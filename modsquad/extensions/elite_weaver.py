"""Elite Weaver - ARMANI Squad Leader for Strategic Integration.

The Art of Seamless Weaving: Orchestrates the integration of parallel batch results,
coordinates interface prediction, glue code generation, and conflict resolution to
produce unified, production-ready code.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

# Import ARMANI squad members at module level (prevent circular import issues)
from . import (
    interface_predictor,
    glue_code_generator,
    conflict_resolver,
    intersection_executor,
    integration_validator,
)

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "elite_weaver"

__all__ = ["run"]


def run(
    batch_plan: dict[str, Any],
    batch_results: dict[str, Any],
) -> dict[str, Any]:
    """
    Orchestrate integration of parallel batch results into cohesive codebase.

    Integration phases:
    1. Extract intersection points from batch plan
    2. Monitor batch completion and identify ready intersections
    3. Predict interfaces at intersection points
    4. Generate glue code for handoffs
    5. Resolve conflicts for file merges
    6. Execute integrations at intersection points
    7. Validate integrated code

    Args:
        batch_plan: Batch plan from elite_strategist with intersections
        batch_results: Results from executed batches {batch_id: result}

    Returns:
        Integration status with completed intersections, conflicts, and validations
    """
    config = load_extension_config()
    settings = config.get("elite_weaver", {})

    if not settings.get("enabled", False):
        return {"status": "disabled", "reason": "Elite weaver not enabled"}

    # Phase 1: Extract intersections from batch plan
    intersections = _extract_intersections(batch_plan)

    # Phase 2: Monitor batch completion and identify ready intersections
    ready_intersections = _monitor_batch_completion(intersections, batch_results)

    # Phase 3: Predict interfaces at ready intersections
    interface_predictions = _predict_interfaces(ready_intersections, batch_results)

    # Phase 4: Generate glue code for handoffs
    glue_code = _generate_glue_code(interface_predictions, batch_results)

    # Phase 5: Resolve conflicts for file merges
    conflict_resolutions = _resolve_conflicts(glue_code, batch_results)

    # Phase 6: Execute integrations at intersection points
    integration_results = _execute_intersections(
        ready_intersections, glue_code, conflict_resolutions
    )

    # Phase 7: Validate integrated code
    validation_results = _validate_integrations(integration_results)

    # Compile comprehensive status
    status = _compile_status(
        intersections, integration_results, validation_results, conflict_resolutions
    )

    # Persist integration results
    dump_jsonl(
        ARTIFACT_DIR / "integration_results.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "status": status,
            "total_intersections": len(intersections),
            "completed_integrations": len(integration_results.get("completed", [])),
            "failed_integrations": len(integration_results.get("failed", [])),
            "validation_passed": validation_results.get("passed", False),
        },
    )

    return status


def _extract_intersections(batch_plan: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Extract intersection points from batch plan.

    Args:
        batch_plan: Batch plan with intersections from elite_strategist

    Returns:
        List of intersection dictionaries
    """
    return batch_plan.get("intersections", [])


def _monitor_batch_completion(
    intersections: list[dict[str, Any]], batch_results: dict[str, Any]
) -> list[dict[str, Any]]:
    """
    Monitor batch completion and identify intersections ready for weaving.

    An intersection is ready when:
    1. Source batch has completed successfully
    2. Target batch has completed successfully (for merges)
    3. All dependent batches are complete

    Args:
        intersections: List of intersection dictionaries
        batch_results: Completed batch results {batch_id: result}

    Returns:
        List of ready intersections
    """
    ready = []

    for intersection in intersections:
        source_batch = intersection.get("source_batch")
        target_batch = intersection.get("target_batch")
        intersection_type = intersection.get("type")

        # Check if source batch is complete
        source_complete = source_batch in batch_results and batch_results[
            source_batch
        ].get("status") == "success"

        if not source_complete:
            continue

        # For file merges, both batches must be complete
        if intersection_type == "file_merge":
            target_complete = target_batch in batch_results and batch_results[
                target_batch
            ].get("status") == "success"

            if not target_complete:
                continue

        # For import chains and handoffs, only source needs to be complete
        ready.append(intersection)

    return ready


def _predict_interfaces(
    ready_intersections: list[dict[str, Any]], batch_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Predict interfaces at ready intersection points.

    Args:
        ready_intersections: Intersections ready for weaving
        batch_results: Completed batch results

    Returns:
        Dictionary mapping intersection IDs to predicted interfaces
    """
    from . import interface_predictor

    predictions = {}

    for intersection in ready_intersections:
        intersection_id = _get_intersection_id(intersection)

        # Skip file merges (no interface prediction needed)
        if intersection.get("type") == "file_merge":
            continue

        # Predict interface for import chains and handoffs
        source_batch = intersection.get("source_batch")
        batch_output = batch_results.get(source_batch, {})

        predicted_interface = interface_predictor.predict(intersection, batch_output)
        predictions[intersection_id] = predicted_interface

    return predictions


def _generate_glue_code(
    interface_predictions: dict[str, Any], batch_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate glue code for handoff intersections.

    Args:
        interface_predictions: Predicted interfaces from interface_predictor
        batch_results: Completed batch results

    Returns:
        Dictionary mapping intersection IDs to generated glue code
    """
    from . import glue_code_generator

    glue_code = {}

    for intersection_id, predicted_interface in interface_predictions.items():
        intersection = predicted_interface.get("intersection", {})

        generated_code = glue_code_generator.generate(intersection, predicted_interface)
        glue_code[intersection_id] = generated_code

    return glue_code


def _resolve_conflicts(
    glue_code: dict[str, Any], batch_results: dict[str, Any]
) -> dict[str, Any]:
    """
    Resolve conflicts for file merge intersections.

    Args:
        glue_code: Generated glue code (may include conflicts)
        batch_results: Completed batch results

    Returns:
        Dictionary mapping intersection IDs to conflict resolutions
    """
    from . import conflict_resolver

    resolutions = {}

    # Find all file merge intersections from batch results
    for batch_id, result in batch_results.items():
        modified_files = result.get("modified_files", [])

        for file_path in modified_files:
            # Check if any other batch also modified this file
            conflicting_batches = [
                other_id
                for other_id, other_result in batch_results.items()
                if other_id != batch_id
                and file_path in other_result.get("modified_files", [])
            ]

            if conflicting_batches:
                for other_batch_id in conflicting_batches:
                    intersection_id = f"merge_{batch_id}_{other_batch_id}_{Path(file_path).name}"

                    batch_a_changes = result.get("changes", {}).get(file_path, {})
                    batch_b_changes = (
                        batch_results.get(other_batch_id, {})
                        .get("changes", {})
                        .get(file_path, {})
                    )

                    resolution = conflict_resolver.resolve(
                        batch_a_changes, batch_b_changes
                    )
                    resolutions[intersection_id] = resolution

    return resolutions


def _execute_intersections(
    ready_intersections: list[dict[str, Any]],
    glue_code: dict[str, Any],
    conflict_resolutions: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute integrations at intersection points.

    Args:
        ready_intersections: Intersections ready for weaving
        glue_code: Generated glue code
        conflict_resolutions: Resolved conflicts

    Returns:
        Execution results with completed and failed integrations
    """
    from . import intersection_executor

    return intersection_executor.execute(
        ready_intersections, glue_code, conflict_resolutions
    )


def _validate_integrations(integration_results: dict[str, Any]) -> dict[str, Any]:
    """
    Validate integrated code for correctness and compatibility.

    Args:
        integration_results: Results from intersection_executor

    Returns:
        Validation results with pass/fail status
    """
    from . import integration_validator

    return integration_validator.validate(integration_results)


def _compile_status(
    intersections: list[dict[str, Any]],
    integration_results: dict[str, Any],
    validation_results: dict[str, Any],
    conflict_resolutions: dict[str, Any],
) -> dict[str, Any]:
    """
    Compile comprehensive integration status.

    Args:
        intersections: All intersections
        integration_results: Execution results
        validation_results: Validation results
        conflict_resolutions: Conflict resolutions

    Returns:
        Comprehensive status dictionary
    """
    completed = integration_results.get("completed", [])
    failed = integration_results.get("failed", [])

    return {
        "status": "success" if validation_results.get("passed", False) else "partial",
        "total_intersections": len(intersections),
        "completed_integrations": len(completed),
        "failed_integrations": len(failed),
        "validation_passed": validation_results.get("passed", False),
        "conflict_resolutions": len(conflict_resolutions),
        "completed_intersection_ids": [_get_intersection_id(i) for i in completed],
        "failed_intersection_ids": [f.get("intersection_id") for f in failed],
        "validation_errors": validation_results.get("errors", []),
        "metadata": {
            "total_glue_code_generated": len(
                integration_results.get("glue_code", {})
            ),
            "total_conflicts_resolved": len(conflict_resolutions),
            "auto_merged_conflicts": len(
                [
                    r
                    for r in conflict_resolutions.values()
                    if r.get("strategy") == "auto_merge"
                ]
            ),
            "manual_review_required": len(
                [
                    r
                    for r in conflict_resolutions.values()
                    if r.get("strategy") == "manual_review"
                ]
            ),
        },
    }


def _get_intersection_id(intersection: dict[str, Any]) -> str:
    """Generate unique ID for intersection."""
    return (
        f"{intersection.get('type', 'unknown')}_"
        f"{intersection.get('source_batch', 'unknown')}_"
        f"{intersection.get('target_batch', 'unknown')}"
    )


def cli() -> None:
    """CLI entry point for elite weaver."""
    print("Elite Weaver - ARMANI Squad Leader")
    print("Run via run(batch_plan, batch_results) for full integration")
