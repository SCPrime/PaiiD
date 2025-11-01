"""
CHARLIE SQUAD - Security & Dependency Management
Mission: Vulnerability scanning, dependency tracking, patch advisory
Risk Profile: <2% with circuit breakers | Scheduled (daily/weekly)
"""

from modsquad.extensions import dependency_tracker, security_patch_advisor

MEMBERS = [
    {
        "name": "security_patch_advisor",
        "module": security_patch_advisor,
        "role": "leader",
    },
    {
        "name": "dependency_tracker",
        "module": dependency_tracker,
        "role": "architecture",
    },
]

_LAST_SCAN = None


def status():
    """Get CHARLIE SQUAD status."""
    return {
        "active": _LAST_SCAN is not None,
        "members": len(MEMBERS),
        "last_scan": _LAST_SCAN,
        "risk": "<2%",
    }


def scan():
    """Deploy CHARLIE SQUAD for security scanning."""
    global _LAST_SCAN

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

    _LAST_SCAN = results

    return {
        "squad": "charlie",
        "scanned": True,
        "results": results,
        "vulnerabilities_found": _count_vulnerabilities(results),
    }


def _count_vulnerabilities(results):
    """Count total vulnerabilities from scan results."""
    count = 0
    advisor_result = results.get("security_patch_advisor", {}).get("result", {})

    if "python_audit" in advisor_result:
        count += advisor_result["python_audit"].get("vulnerabilities", 0)

    if "npm_audit" in advisor_result:
        count += advisor_result["npm_audit"].get("total_vulnerabilities", 0)

    return count


__all__ = ["status", "scan", "MEMBERS"]
