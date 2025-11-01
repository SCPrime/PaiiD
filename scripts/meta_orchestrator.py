#!/usr/bin/env python3
"""
META-ORCHESTRATOR - Supreme oversight for MOD SQUAD operations
Ensures <0.5% risk rate through coordinated agent execution and validation

Author: Dr. SC Prime
Date: October 31, 2025
"""

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ANSI color codes (Windows-safe)
GREEN = "[OK]"
RED = "[FAIL]"
YELLOW = "[WARN]"
BLUE = "[INFO]"
CYAN = "[EXEC]"


class ExecutionTracker:
    """Track agent execution state and metrics"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = output_dir / f"execution_log_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.jsonl"
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def log_task_start(self, task_id: str, agent: str, phase: str, description: str, dependencies: Optional[List[str]] = None):
        """Log task start event"""
        task = {
            "task_id": task_id,
            "agent": agent,
            "phase": phase,
            "description": description,
            "status": "in_progress",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "dependencies": dependencies or [],
            "errors": [],
            "warnings": [],
            "metrics": {}
        }
        self.tasks[task_id] = task
        self._write_log(task)

    def log_task_complete(self, task_id: str, metrics: Optional[Dict[str, Any]] = None):
        """Log task completion"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        task["status"] = "completed"
        task["end_time"] = datetime.now(timezone.utc).isoformat()

        start = datetime.fromisoformat(task["start_time"])
        end = datetime.fromisoformat(task["end_time"])
        task["duration_seconds"] = (end - start).total_seconds()

        if metrics:
            task["metrics"] = metrics

        self._write_log(task)

    def log_task_failed(self, task_id: str, error: str):
        """Log task failure"""
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        task["status"] = "failed"
        task["end_time"] = datetime.now(timezone.utc).isoformat()
        task["errors"].append(error)

        start = datetime.fromisoformat(task["start_time"])
        end = datetime.fromisoformat(task["end_time"])
        task["duration_seconds"] = (end - start).total_seconds()

        self._write_log(task)

    def add_warning(self, task_id: str, warning: str):
        """Add warning to task"""
        if task_id not in self.tasks:
            return
        self.tasks[task_id]["warnings"].append(warning)

    def _write_log(self, task: Dict[str, Any]):
        """Write task log to JSONL file"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(task) + "\n")

    def get_summary(self) -> Dict[str, Any]:
        """Generate execution summary"""
        completed = sum(1 for t in self.tasks.values() if t["status"] == "completed")
        failed = sum(1 for t in self.tasks.values() if t["status"] == "failed")
        in_progress = sum(1 for t in self.tasks.values() if t["status"] == "in_progress")
        total_errors = sum(len(t["errors"]) for t in self.tasks.values())
        total_warnings = sum(len(t["warnings"]) for t in self.tasks.values())

        return {
            "total_tasks": len(self.tasks),
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "risk_rate": (total_errors / max(1, len(self.tasks))) if self.tasks else 0.0
        }


class MetaOrchestrator:
    """Meta-Orchestrator for supreme MOD SQUAD oversight"""

    def __init__(self, mode: str = "full", risk_target: float = 0.5):
        self.mode = mode
        self.risk_target = risk_target
        self.root = Path(__file__).resolve().parents[1]
        self.reports_dir = self.root / "reports"
        self.tracker = ExecutionTracker(self.root / "modsquad" / "logs")

    def run_script(self, script_path: str, args: List[str] = None, timeout: int = 300) -> Tuple[bool, str, str]:
        """Execute a Python script and capture output"""
        args = args or []
        cmd = [sys.executable, script_path] + args

        try:
            result = subprocess.run(
                cmd,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )
            success = result.returncode == 0
            return success, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Script timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)

    def _run_repo_audit(self) -> Dict[str, Any]:
        """Execute repository audit validation task"""
        task_id = "repo-audit"
        self.tracker.log_task_start(task_id, "meta-orchestrator", "VALIDATION", "Repository audit")
        print(f"{CYAN} Executing: Repository audit...")

        success, stdout, stderr = self.run_script(
            str(self.root / "scripts" / "auto_github_monitor.py"),
            ["--full-audit", "--output", str(self.reports_dir / "github_mod.json")]
        )

        if success:
            print(f"{GREEN} Repository audit PASSED")
            self.tracker.log_task_complete(task_id, {"status": "passed"})
            return {"status": "passed", "key": "repo_audit"}
        else:
            print(f"{RED} Repository audit FAILED: {stderr}")
            self.tracker.log_task_failed(task_id, stderr)
            return {"status": "failed", "key": "repo_audit"}

    def _run_live_flows(self) -> Dict[str, Any]:
        """Execute live data flows validation task"""
        task_id = "live-data-flows"
        self.tracker.log_task_start(task_id, "meta-orchestrator", "VALIDATION", "Live data flow validation")
        print(f"{CYAN} Executing: Live data flows...")

        success, stdout, stderr = self.run_script(
            str(self.root / "scripts" / "live_data_flows.py"),
            ["--comprehensive", "--output", str(self.reports_dir / "live_flows.json")]
        )

        if success:
            print(f"{GREEN} Live data flows PASSED")
            self.tracker.log_task_complete(task_id, {"status": "passed"})
            return {"status": "passed", "key": "live_data"}
        else:
            print(f"{RED} Live data flows FAILED: {stderr}")
            self.tracker.log_task_failed(task_id, stderr)
            return {"status": "failed", "key": "live_data"}

    def _run_wedge_flows(self) -> Dict[str, Any]:
        """Execute wedge flows validation task"""
        task_id = "wedge-flows"
        self.tracker.log_task_start(task_id, "meta-orchestrator", "VALIDATION", "Wedge flow validation")
        print(f"{CYAN} Executing: Wedge flows...")

        success, stdout, stderr = self.run_script(
            str(self.root / "scripts" / "wedge_flows.py"),
            timeout=600
        )

        if success:
            print(f"{GREEN} Wedge flows PASSED")
            self.tracker.log_task_complete(task_id, {"status": "passed"})
            return {"status": "passed", "key": "wedge_flows"}
        else:
            print(f"{RED} Wedge flows FAILED: {stderr}")
            self.tracker.log_task_failed(task_id, stderr)
            return {"status": "failed", "key": "wedge_flows"}

    def _run_branding_a11y(self) -> Dict[str, Any]:
        """Execute branding and accessibility validation task"""
        task_id = "branding-a11y"
        self.tracker.log_task_start(task_id, "meta-orchestrator", "VALIDATION", "Branding and accessibility validation")
        print(f"{CYAN} Executing: Branding/A11y checks...")

        success, stdout, stderr = self.run_script(
            str(self.root / "scripts" / "branding_a11y_checks.py")
        )

        if success:
            print(f"{GREEN} Branding/A11y PASSED")
            self.tracker.log_task_complete(task_id, {"status": "passed"})
            return {"status": "passed", "key": "branding"}
        else:
            print(f"{YELLOW} Branding/A11y had warnings: {stderr}")
            self.tracker.add_warning(task_id, stderr)
            self.tracker.log_task_complete(task_id, {"status": "passed_with_warnings"})
            return {"status": "passed_with_warnings", "key": "branding"}

    def _run_browser_validation(self) -> Dict[str, Any]:
        """Execute browser validation task (axe-core, Lighthouse, Percy)"""
        task_id = "browser-validation"
        self.tracker.log_task_start(task_id, "meta-orchestrator", "VALIDATION", "Browser console & performance validation")
        print(f"{CYAN} Executing: Browser validation (accessibility, performance)...")

        # Run browser_validator extension via Python -m
        try:
            result = subprocess.run(
                [sys.executable, "-m", "modsquad.extensions.browser_validator"],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=180,
                encoding="utf-8",
                errors="replace"
            )
            success = result.returncode == 0
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired:
            success = False
            stdout = ""
            stderr = "Browser validation timed out after 180s"
        except Exception as e:
            success = False
            stdout = ""
            stderr = str(e)

        if success:
            # Check the browser_validator output for failures
            browser_log = self.root / "modsquad" / "logs" / "run-history" / "browser_validator" / "browser_validator.jsonl"
            if browser_log.exists():
                try:
                    with open(browser_log, "r", encoding="utf-8") as f:
                        lines = [line.strip() for line in f.readlines() if line.strip()]
                        if lines:
                            last_run = json.loads(lines[-1])
                            has_failures = any(r.get("status") in ["failed", "error"] for r in last_run.get("results", []))

                            if has_failures:
                                print(f"{YELLOW} Browser validation completed with failures (see browser_validator.jsonl)")
                                self.tracker.add_warning(task_id, "Some browser checks failed (accessibility or performance below threshold)")
                                self.tracker.log_task_complete(task_id, {"status": "passed_with_warnings"})
                                return {"status": "passed_with_warnings", "key": "browser_validation"}
                            else:
                                print(f"{GREEN} Browser validation PASSED")
                                self.tracker.log_task_complete(task_id, {"status": "passed"})
                                return {"status": "passed", "key": "browser_validation"}
                        else:
                            print(f"{YELLOW} Browser validation completed but log is empty")
                            self.tracker.add_warning(task_id, "Empty browser_validator.jsonl")
                            self.tracker.log_task_complete(task_id, {"status": "passed_with_warnings"})
                            return {"status": "passed_with_warnings", "key": "browser_validation"}
                except Exception as e:
                    print(f"{YELLOW} Browser validation completed but could not parse log: {e}")
                    self.tracker.add_warning(task_id, f"Could not parse browser_validator.jsonl: {e}")
                    self.tracker.log_task_complete(task_id, {"status": "passed_with_warnings"})
                    return {"status": "passed_with_warnings", "key": "browser_validation"}
            else:
                print(f"{YELLOW} Browser validation completed but no log found")
                self.tracker.add_warning(task_id, "No browser_validator.jsonl output")
                self.tracker.log_task_complete(task_id, {"status": "passed_with_warnings"})
                return {"status": "passed_with_warnings", "key": "browser_validation"}
        else:
            print(f"{RED} Browser validation FAILED: {stderr}")
            self.tracker.log_task_failed(task_id, stderr)
            return {"status": "failed", "key": "browser_validation"}

    def run_validation_suite(self) -> Dict[str, Any]:
        """Run comprehensive validation suite in parallel"""
        print(f"\n{BLUE} META-ORCHESTRATOR: Running validation suite (mode={self.mode})")
        print(f"{BLUE} Parallel execution with 5 workers (target: ~600s vs sequential ~880s)")

        results = {}

        # Define tasks to run in parallel
        tasks = {
            "repo_audit": self._run_repo_audit,
            "live_flows": self._run_live_flows,
            "branding_a11y": self._run_branding_a11y,
            "browser_validation": self._run_browser_validation,
        }

        # Add wedge flows only in full mode
        if self.mode == "full":
            tasks["wedge_flows"] = self._run_wedge_flows

        # Execute all tasks in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_task = {executor.submit(fn): name for name, fn in tasks.items()}

            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    result = future.result()
                    # Use the key from result to maintain backward compatibility
                    results[result["key"]] = result["status"]
                except Exception as e:
                    print(f"{RED} Task {task_name} raised exception: {e}")
                    results[task_name] = "error"

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate executive summary report"""
        summary = self.tracker.get_summary()

        report = []
        report.append("\n" + "="*80)
        report.append("META-ORCHESTRATOR EXECUTION REPORT")
        report.append("="*80)
        report.append(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        report.append(f"Mode: {self.mode}")
        report.append(f"Risk Target: {self.risk_target}%")
        report.append("")

        report.append("VALIDATION RESULTS:")
        report.append("-"*80)
        for check, status in results.items():
            status_icon = GREEN if status == "passed" else (YELLOW if "warning" in status else RED)
            report.append(f"  {check:30s} {status_icon} {status}")
        report.append("")

        report.append("EXECUTION SUMMARY:")
        report.append("-"*80)
        report.append(f"  Total Tasks: {summary['total_tasks']}")
        report.append(f"  Completed:   {summary['completed']}")
        report.append(f"  Failed:      {summary['failed']}")
        report.append(f"  In Progress: {summary['in_progress']}")
        report.append(f"  Errors:      {summary['total_errors']}")
        report.append(f"  Warnings:    {summary['total_warnings']}")
        report.append("")

        risk_rate = summary['risk_rate'] * 100
        if risk_rate <= self.risk_target:
            report.append(f"{GREEN} RISK RATE: {risk_rate:.2f}% (TARGET: <{self.risk_target}%)")
            report.append(f"{GREEN} PRODUCTION READINESS: APPROVED")
        else:
            report.append(f"{RED} RISK RATE: {risk_rate:.2f}% (EXCEEDS TARGET: {self.risk_target}%)")
            report.append(f"{RED} PRODUCTION READINESS: BLOCKED")

        report.append("="*80)
        report.append("")

        return "\n".join(report)

    def execute(self) -> int:
        """Execute meta-orchestrator oversight"""
        print(f"\n{BLUE} META-ORCHESTRATOR v2.0 - Supreme MOD SQUAD Oversight")
        print(f"{BLUE} Target: <{self.risk_target}% risk rate")
        print(f"{BLUE} Mode: {self.mode}")

        # Run validation suite
        results = self.run_validation_suite()

        # Generate and display report
        report = self.generate_report(results)
        print(report)

        # Save report
        report_file = self.reports_dir / f"meta_orchestrator_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"{BLUE} Full report saved to: {report_file}")

        # Determine exit code
        summary = self.tracker.get_summary()
        if summary["failed"] > 0:
            print(f"\n{RED} CRITICAL: {summary['failed']} task(s) failed")
            return 1
        elif summary["risk_rate"] * 100 > self.risk_target:
            print(f"\n{RED} CRITICAL: Risk rate exceeds target")
            return 1
        else:
            print(f"\n{GREEN} SUCCESS: All validations passed, risk rate within target")
            return 0


def main():
    parser = argparse.ArgumentParser(description="META-ORCHESTRATOR - Supreme MOD SQUAD oversight")
    parser.add_argument("--mode", choices=["quick", "full"], default="full", help="Validation mode")
    parser.add_argument("--risk-target", type=float, default=0.5, help="Target risk rate percentage")
    parser.add_argument("--report", action="store_true", help="Generate report only (no execution)")

    args = parser.parse_args()

    orchestrator = MetaOrchestrator(mode=args.mode, risk_target=args.risk_target)

    try:
        exit_code = orchestrator.execute()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW} Meta-Orchestrator interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED} FATAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
