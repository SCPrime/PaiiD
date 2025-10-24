#!/usr/bin/env python3
"""
🚨 Critical Issues Checker
Scans for P0 issues and security concerns
"""
import json
import sys
from pathlib import Path


def check_critical_issues():
    """Check for critical issues in monitor data"""
    print("🚨 Checking for critical issues...")
    
    monitor_file = Path("monitor-data.json")
    if not monitor_file.exists():
        print("✅ No monitor data found, assuming fresh start")
        return True
    
    monitor_data = json.loads(monitor_file.read_text())
    counters = monitor_data.get("counters", {})
    
    # Check for errors
    errors = counters.get("errors", 0)
    if errors > 5:
        print(f"❌ CRITICAL: {errors} errors detected!")
        return False
    
    # Check for open issues (warning only)
    open_issues = counters.get("open_issues", 0)
    if open_issues > 10:
        print(f"⚠️  WARNING: {open_issues} open issues")
    else:
        print(f"✅ Open issues: {open_issues}")
    
    # Check workflow runs
    workflow_runs = counters.get("workflow_runs", 0)
    print(f"✅ Workflow runs: {workflow_runs}")
    
    print("✅ No critical issues detected")
    return True


if __name__ == "__main__":
    success = check_critical_issues()
    sys.exit(0 if success else 1)

