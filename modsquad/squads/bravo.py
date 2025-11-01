"""
BRAVO SQUAD - Quality Validation & Testing
Mission: Comprehensive testing across all layers
Risk Profile: <3% with circuit breakers | On-Demand & Scheduled
"""

import sys

from modsquad.extensions import (
    browser_validator,
    bundle_analyzer,
    contract_enforcer,
    infra_health,
    runtime_error_monitor,
    test_orchestrator,
    visual_regression_advanced,
)

MEMBERS = [
    {"name": "test_orchestrator", "module": test_orchestrator, "role": "leader"},
    {"name": "browser_validator", "module": browser_validator, "role": "visual_core"},
    {
        "name": "visual_regression_advanced",
        "module": visual_regression_advanced,
        "role": "visual_advanced",
    },
    {"name": "contract_enforcer", "module": contract_enforcer, "role": "api"},
    {"name": "bundle_analyzer", "module": bundle_analyzer, "role": "bundle"},
    {
        "name": "runtime_error_monitor",
        "module": runtime_error_monitor,
        "role": "runtime",
    },
    {"name": "infra_health", "module": infra_health, "role": "infrastructure"},
]

_LAST_DEPLOYMENT = None


def status():
    """Get BRAVO SQUAD status."""
    return {
        "active": _LAST_DEPLOYMENT is not None,
        "members": len(MEMBERS),
        "last_deployment": _LAST_DEPLOYMENT,
        "risk": "<3%",
    }


def deploy(tests=None, skip=None, enforce_guardrails=True):
    """
    Deploy BRAVO SQUAD for quality validation.

    Args:
        tests: List of specific tests to run (e.g., ['frontend', 'backend'])
        skip: List of tests to skip (e.g., ['e2e'])
        enforce_guardrails: If True, exit with code 1 if any guardrail check fails
    """
    global _LAST_DEPLOYMENT

    results = {}
    guardrail_failures = []

    # Always run test orchestrator (leader)
    try:
        result = test_orchestrator.run()
        results["test_orchestrator"] = {
            "status": "success"
            if result.get("summary", {}).get("overall_passed")
            else "failed",
            "result": result,
        }
    except SystemExit as e:
        # Guardrail enforcement triggered exit
        results["test_orchestrator"] = {
            "status": "guardrail_failed",
            "exit_code": e.code,
        }
        guardrail_failures.append(("test_orchestrator", e.code))
    except Exception as e:
        results["test_orchestrator"] = {
            "status": "error",
            "error": str(e),
        }

    # Run other members if not skipped
    for member in MEMBERS[1:]:  # Skip leader (already ran)
        member_name = member["name"]

        if skip and member_name in skip:
            results[member_name] = {"status": "skipped"}
            continue

        if tests and member_name not in tests:
            continue

        try:
            result = member["module"].run()
            results[member_name] = {
                "status": "success",
                "result": result,
            }
        except SystemExit as e:
            # Guardrail enforcement triggered exit
            results[member_name] = {
                "status": "guardrail_failed",
                "exit_code": e.code,
            }
            guardrail_failures.append((member_name, e.code))
        except Exception as e:
            results[member_name] = {
                "status": "error",
                "error": str(e),
            }

    _LAST_DEPLOYMENT = results

    # GUARDRAIL ENFORCEMENT: Propagate failures to squad level
    if enforce_guardrails and guardrail_failures:
        print(f"\nBRAVO SQUAD GUARDRAIL FAILURES: {len(guardrail_failures)}")
        for member_name, exit_code in guardrail_failures:
            print(f"   FAIL {member_name}: exited with code {exit_code}")
        print("   Blocking deployment due to guardrail policy\n")
        sys.exit(1)

    return {
        "squad": "bravo",
        "deployed": True,
        "results": results,
        "overall_passed": all(
            r.get("status") in ["success", "skipped"] for r in results.values()
        ),
    }


def quick_check():
    """Quick validation for pre-commit hooks."""
    try:
        result = test_orchestrator.run()
        return result.get("summary", {}).get("overall_passed", False)
    except Exception:
        return False


__all__ = ["status", "deploy", "quick_check", "MEMBERS"]
