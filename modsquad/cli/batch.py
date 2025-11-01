"""CLI commands for SUN TZU + ARMANI batch execution."""

import argparse
import json
import sys
from pathlib import Path


def batch_plan_command(args):
    """Execute batch planning with SUN TZU squad."""
    from modsquad.squads import sun_tzu

    # Load tasks from file
    tasks_file = Path(args.tasks)
    if not tasks_file.exists():
        print(f"ERROR: Tasks file not found: {args.tasks}")
        sys.exit(1)

    with tasks_file.open("r") as f:
        tasks = json.load(f)

    # Execute planning
    print(f"[SUN TZU] Planning batch execution for {len(tasks)} tasks...")
    result = sun_tzu.plan(tasks)

    # Save plan if requested
    if args.output:
        output_file = Path(args.output)
        with output_file.open("w") as f:
            json.dump(result, f, indent=2)
        print(f"[SUN TZU] Batch plan saved to {args.output}")

    # Print summary
    if result.get("status") == "success":
        metadata = result["batch_plan"]["strategist_metadata"]
        print(f"  ✓ Batches: {metadata['total_batches']}")
        print(f"  ✓ Parallelization: {metadata['parallelization_factor']}%")
        print(f"  ✓ Estimated Speedup: {metadata['estimated_speedup']}")
        print(f"  ✓ Intersections: {metadata['total_intersections']}")
        sys.exit(0)
    else:
        print(f"  ✗ Planning failed: {result.get('reason', result.get('message', 'Unknown error'))}")
        sys.exit(1)


def batch_weave_command(args):
    """Execute integration weaving with ARMANI squad."""
    from modsquad.squads import armani

    # Load batch plan
    plan_file = Path(args.plan)
    if not plan_file.exists():
        print(f"ERROR: Batch plan not found: {args.plan}")
        sys.exit(1)

    with plan_file.open("r") as f:
        batch_plan_data = json.load(f)

    # Extract the batch_plan if wrapped in result structure
    if "batch_plan" in batch_plan_data:
        batch_plan = batch_plan_data["batch_plan"]
    else:
        batch_plan = batch_plan_data

    # Load batch results
    results_file = Path(args.results)
    if not results_file.exists():
        print(f"ERROR: Batch results not found: {args.results}")
        sys.exit(1)

    with results_file.open("r") as f:
        batch_results = json.load(f)

    # Execute weaving
    intersections = batch_plan.get("intersections", [])
    print(f"[ARMANI] Weaving {len(intersections)} intersection points...")
    result = armani.weave(batch_plan, batch_results)

    # Print summary
    if result.get("status") == "success":
        metadata = result["weave_result"]["weaver_metadata"]
        print(f"  ✓ Intersections Executed: {metadata['intersections_executed']}")
        print(f"  ✓ Conflicts Resolved: {metadata['conflicts_resolved']}")
        print(f"  ✓ Validations Passed: {metadata['validations_passed']}")
        sys.exit(0)
    else:
        print(f"  ✗ Weaving failed: {result.get('reason', result.get('message', 'Unknown error'))}")
        sys.exit(1)


def batch_rollback_command(args):
    """Rollback a failed batch execution."""
    from datetime import datetime

    # TODO: Implement rollback by restoring from backup directory
    backup_dir = Path("modsquad/logs/run-history/intersection_executor/backups")

    if not backup_dir.exists():
        print("ERROR: No backups found")
        sys.exit(1)

    # List available backups
    backups = sorted(backup_dir.glob("*.backup"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not backups:
        print("ERROR: No backup files found")
        sys.exit(1)

    print(f"Found {len(backups)} backup files:")
    for i, backup in enumerate(backups[:10]):
        # Get file modification time
        mtime = backup.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)
        print(f"  {i+1}. {backup.name} ({dt.strftime('%Y-%m-%d %H:%M:%S')})")

    # TODO: Implement restore logic
    print("\nRollback functionality coming soon!")
    print("Manual rollback instructions:")
    print("1. Identify the backup timestamp (e.g., 20251031_143522)")
    print("2. Restore files: cp modsquad/logs/run-history/intersection_executor/backups/<file>.<timestamp>.backup <original-path>")
    print("3. Verify restoration: python -m py_compile <file>")
    sys.exit(0)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MOD SQUAD Batch Execution CLI (SUN TZU + ARMANI)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # batch-plan command
    plan_parser = subparsers.add_parser("plan", help="Create batch execution plan with SUN TZU")
    plan_parser.add_argument("--tasks", required=True, help="Path to tasks JSON file")
    plan_parser.add_argument("--output", help="Path to save batch plan JSON")
    plan_parser.set_defaults(func=batch_plan_command)

    # batch-weave command
    weave_parser = subparsers.add_parser("weave", help="Execute integration weaving with ARMANI")
    weave_parser.add_argument("--plan", required=True, help="Path to batch plan JSON")
    weave_parser.add_argument("--results", required=True, help="Path to batch results JSON")
    weave_parser.set_defaults(func=batch_weave_command)

    # batch-rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback failed batch execution")
    rollback_parser.add_argument("--batch-id", help="Batch ID to rollback (optional)")
    rollback_parser.set_defaults(func=batch_rollback_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
