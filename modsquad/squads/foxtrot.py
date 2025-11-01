"""
FOXTROT SQUAD - Orchestration & Coordination
Mission: Schedule squad deployments, manage execution order, prevent conflicts
Risk Profile: <2% | Meta-coordination
"""

import threading
from datetime import UTC, datetime

from modsquad.extensions import guardrail_scheduler, runner, stream_coordinator

# Import other squads for orchestration
from . import alpha, bravo, charlie, delta, echo

# Batch execution lock (prevents concurrent orchestration and batching)
_batch_execution_lock = threading.Lock()

MEMBERS = [
    {"name": "guardrail_scheduler", "module": guardrail_scheduler, "role": "leader"},
    {
        "name": "stream_coordinator",
        "module": stream_coordinator,
        "role": "coordination",
    },
    {"name": "runner", "module": runner, "role": "cli"},
]

_LAST_ORCHESTRATION = None


def status():
    """Get FOXTROT SQUAD status."""
    return {
        "active": True,  # Always ready to orchestrate
        "members": len(MEMBERS),
        "last_orchestration": _LAST_ORCHESTRATION,
        "risk": "<2%",
    }


def orchestrate(squads_to_deploy=None, skip_slow=False):
    """
    Orchestrate deployment of specified squads in optimal order.

    Args:
        squads_to_deploy: List of squad names (e.g., ['bravo', 'charlie'])
                         If None, deploys all squads
        skip_slow: Skip slow operations (e.g., e2e tests)
    """
    global _LAST_ORCHESTRATION

    if squads_to_deploy is None:
        squads_to_deploy = ["bravo", "charlie", "delta", "echo"]

    results = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "squads_deployed": [],
        "squad_results": {},
    }

    # Deploy squads in optimal order
    deployment_order = _get_deployment_order(squads_to_deploy)

    for squad_name in deployment_order:
        try:
            if squad_name == "alpha":
                result = alpha.deploy()
            elif squad_name == "bravo":
                result = bravo.deploy(skip=["e2e"] if skip_slow else None)
            elif squad_name == "charlie":
                result = charlie.scan()
            elif squad_name == "delta":
                result = delta.monitor()
            elif squad_name == "echo":
                result = echo.report()
            else:
                result = {"status": "unknown_squad"}

            results["squad_results"][squad_name] = result
            results["squads_deployed"].append(squad_name)

        except Exception as e:
            results["squad_results"][squad_name] = {
                "status": "error",
                "error": str(e),
            }

    _LAST_ORCHESTRATION = results

    return results


def orchestrate_all(skip_slow=False):
    """Deploy all squads in full stack validation mode."""
    return orchestrate(
        squads_to_deploy=["bravo", "charlie", "delta", "echo"],
        skip_slow=skip_slow,
    )


def pre_deploy_check():
    """Run pre-deployment validation (BRAVO + CHARLIE squads)."""
    results = orchestrate(squads_to_deploy=["bravo", "charlie"])

    # Determine if deployment should proceed
    bravo_passed = (
        results["squad_results"].get("bravo", {}).get("overall_passed", False)
    )
    charlie_vulnerabilities = (
        results["squad_results"].get("charlie", {}).get("vulnerabilities_found", 0)
    )

    go_for_deploy = bravo_passed and charlie_vulnerabilities == 0

    return {
        "go_for_deploy": go_for_deploy,
        "bravo_passed": bravo_passed,
        "vulnerabilities": charlie_vulnerabilities,
        "results": results,
    }


def _get_deployment_order(squads):
    """
    Determine optimal deployment order based on dependencies.

    Order:
    1. BRAVO - Quality validation (no dependencies)
    2. CHARLIE - Security scanning (no dependencies)
    3. DELTA - Change monitoring (no dependencies)
    4. ECHO - Reporting (depends on all others)
    """
    ordered = []

    # Independent squads first (can run in parallel)
    for squad in ["bravo", "charlie", "delta"]:
        if squad in squads:
            ordered.append(squad)

    # ECHO last (aggregates all others)
    if "echo" in squads:
        ordered.append("echo")

    # ALPHA can run anytime (but usually always on)
    if "alpha" in squads:
        ordered.insert(0, "alpha")

    return ordered


def acquire_batch_lock(timeout: float = 60.0) -> bool:
    """
    Acquire exclusive batch execution lock.

    Prevents simultaneous orchestration and batch execution.

    Args:
        timeout: Maximum seconds to wait for lock (default: 60)

    Returns:
        True if lock acquired, False if timeout
    """
    return _batch_execution_lock.acquire(timeout=timeout)


def release_batch_lock() -> None:
    """Release batch execution lock."""
    try:
        _batch_execution_lock.release()
    except RuntimeError:
        pass  # Lock not held, safe to ignore


def is_batch_locked() -> bool:
    """Check if batch execution is currently locked."""
    acquired = _batch_execution_lock.acquire(blocking=False)
    if acquired:
        _batch_execution_lock.release()
        return False
    return True


__all__ = [
    "status",
    "orchestrate",
    "orchestrate_all",
    "pre_deploy_check",
    "acquire_batch_lock",
    "release_batch_lock",
    "is_batch_locked",
    "MEMBERS",
]
