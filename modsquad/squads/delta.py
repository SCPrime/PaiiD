"""
DELTA SQUAD - Change Detection & Monitoring
Mission: Track code changes, documentation, live data performance
Risk Profile: <1% | Continuous/Scheduled
"""

from modsquad.extensions import component_diff_reporter, data_latency_tracker, docs_sync

MEMBERS = [
    {
        "name": "component_diff_reporter",
        "module": component_diff_reporter,
        "role": "leader",
    },
    {"name": "docs_sync", "module": docs_sync, "role": "documentation"},
    {
        "name": "data_latency_tracker",
        "module": data_latency_tracker,
        "role": "performance",
    },
]

_LAST_MONITOR = None


def status():
    """Get DELTA SQUAD status."""
    return {
        "active": _LAST_MONITOR is not None,
        "members": len(MEMBERS),
        "last_monitor": _LAST_MONITOR,
        "risk": "<1%",
    }


def monitor():
    """Deploy DELTA SQUAD for change detection and monitoring."""
    global _LAST_MONITOR

    results = {}

    for member in MEMBERS:
        try:
            result = member["module"].run()
            results[member["name"]] = {
                "status": "success",
                "result": result,
            }
        except Exception as e:
            results[member["name"]] = {
                "status": "error",
                "error": str(e),
            }

    _LAST_MONITOR = results

    return {
        "squad": "delta",
        "monitored": True,
        "results": results,
        "changes_detected": _count_changes(results),
    }


def _count_changes(results):
    """Count total changes detected."""
    count = 0

    diff_result = results.get("component_diff_reporter", {}).get("result", {})
    if "changes" in diff_result:
        count += len(diff_result["changes"])

    return count


__all__ = ["status", "monitor", "MEMBERS"]
