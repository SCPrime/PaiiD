"""
ECHO SQUAD - Aggregation & Reporting
Mission: Collect all squad outputs, analyze health, generate insights
Risk Profile: <1% | Post-execution
"""

from modsquad.extensions import quality_inspector, review_aggregator

MEMBERS = [
    {"name": "review_aggregator", "module": review_aggregator, "role": "collector"},
    {"name": "quality_inspector", "module": quality_inspector, "role": "leader"},
]

_LAST_REPORT = None


def status():
    """Get ECHO SQUAD status."""
    return {
        "active": _LAST_REPORT is not None,
        "members": len(MEMBERS),
        "last_report": _LAST_REPORT,
        "risk": "<1%",
    }


def report():
    """Deploy ECHO SQUAD for aggregation and reporting."""
    global _LAST_REPORT

    results = {}

    # First, aggregate all reports
    try:
        aggregated = review_aggregator.run()
        results["review_aggregator"] = {
            "status": "success",
            "result": aggregated,
        }
    except Exception as e:
        results["review_aggregator"] = {
            "status": "error",
            "error": str(e),
        }

    # Then, inspect overall quality
    try:
        inspection = quality_inspector.run()
        results["quality_inspector"] = {
            "status": "success",
            "result": inspection,
        }
    except Exception as e:
        results["quality_inspector"] = {
            "status": "error",
            "error": str(e),
        }

    _LAST_REPORT = results

    # Extract overall health
    overall_health = "unknown"
    if results.get("quality_inspector", {}).get("status") == "success":
        inspection_result = results["quality_inspector"]["result"]
        overall_health = inspection_result.get("overall_status", "unknown")

    return {
        "squad": "echo",
        "reported": True,
        "results": results,
        "overall_health": overall_health,
    }


def get_latest_report():
    """Get the latest ECHO SQUAD report."""
    return _LAST_REPORT


__all__ = ["status", "report", "get_latest_report", "MEMBERS"]
