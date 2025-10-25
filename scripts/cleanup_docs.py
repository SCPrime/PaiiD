#!/usr/bin/env python3
"""
🗑️ Documentation Cleanup Script
Archives redundant deployment documentation while preserving essential files.
"""
import shutil
from datetime import datetime
from pathlib import Path

# Essential files to KEEP (never touch these!)
ESSENTIAL_FILES = {
    "DEPLOYMENT_STATUS_LIVE.md",  # NEW single source of truth
    "DEPLOYMENT_AUDIT_REPORT.md",  # Audit findings
    "DEPLOYMENT.md",  # Main deployment guide
    "README.md",  # Project README
    "TODO.md",  # Task tracking
    "LICENSE",  # Copyright
    "render.yaml",  # Master config (root only)
    "STRATEGIC_NEXT_BATCHES.md",  # Roadmap
    "LIVE_PLATFORM_TEST.md",  # Testing guide
    "GITHUB_MONITOR_PLAN.md",  # Monitor docs
    "MONITOR_COMPLETE_GUIDE.md",  # Monitor guide
    "PROGRESS_DASHBOARD.html",  # Progress dashboard
    "progress-data.json",  # Progress data
}

# Files to ARCHIVE (redundant but keep for history)
TO_ARCHIVE = [
    "FRONTEND_DEPLOYMENT_GUIDE.md",  # Redundant with DEPLOYMENT.md
    "FRONTEND_ENV_VARS.md",  # Redundant with DEPLOYMENT_STATUS_LIVE.md
    "DEPLOYMENT_LIVE_STATUS.md",  # Old version if exists
    "PHASE_2_ML_STRATEGY_PLAN.md",  # Completed
    "ML_API_DOCUMENTATION.md",  # Redundant (in /docs)
    "BATCH_ADCB_COMPLETE_REPORT.md",  # Historical
    "AUTH_FIX_REPORT.md",  # Historical
]

# Patterns to archive (regex-style glob patterns)
ARCHIVE_PATTERNS = [
    "**/DEPLOYMENT_STATUS_*.md",  # Old deployment status files
    "**/BATCH_*_COMPLETE*.md",  # Old batch reports
    "**/PHASE_*_REPORT.md",  # Old phase reports
]


def main():
    """Main cleanup function"""
    root = Path(__file__).parent.parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = root / "archive" / f"cleanup-{timestamp}"
    archive_dir.mkdir(parents=True, exist_ok=True)

    print("[CLEANUP] PaiiD Documentation Cleanup")
    print("=" * 50)
    print(f"Archive directory: {archive_dir}")
    print()

    archived_count = 0
    kept_count = 0

    # Archive specific files
    for filename in TO_ARCHIVE:
        file_path = root / filename
        if file_path.exists() and file_path.is_file():
            dest = archive_dir / filename
            shutil.move(str(file_path), str(dest))
            print(f"[ARCHIVED] {filename}")
            archived_count += 1

    # Archive files matching patterns
    for pattern in ARCHIVE_PATTERNS:
        for file_path in root.glob(pattern):
            if file_path.is_file() and file_path.name not in ESSENTIAL_FILES:
                # Create subdirectory structure in archive
                rel_path = file_path.relative_to(root)
                dest = archive_dir / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest))
                print(f"[ARCHIVED] {rel_path}")
                archived_count += 1

    # Report essential files kept
    for essential in ESSENTIAL_FILES:
        file_path = root / essential
        if file_path.exists():
            kept_count += 1

    print()
    print("[SUCCESS] Cleanup Complete!")
    print(f"[ARCHIVED] {archived_count} files")
    print(f"[KEPT] {kept_count} essential files")
    print()
    print("Essential files remaining:")
    for essential in sorted(ESSENTIAL_FILES):
        file_path = root / essential
        if file_path.exists():
            print(f"  [OK] {essential}")

    # Create archive summary
    summary_file = archive_dir / "ARCHIVE_SUMMARY.md"
    summary_file.write_text(
        f"""# Documentation Cleanup Archive

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Files Archived**: {archived_count}

## Why These Were Archived:

These files were redundant with the new single source of truth:
- `DEPLOYMENT_STATUS_LIVE.md` - THE definitive deployment status
- `DEPLOYMENT.md` - Main deployment guide
- `DEPLOYMENT_AUDIT_REPORT.md` - Recent audit findings

## What Was Kept:

Essential documentation files ({kept_count} files):
{chr(10).join(f'- {f}' for f in sorted(ESSENTIAL_FILES) if (root / f).exists())}

## Files Archived:

{chr(10).join(f'- {f}' for f in TO_ARCHIVE if (archive_dir / f).exists())}

---

**Archived by**: Documentation Cleanup Script  
**Purpose**: Eliminate redundancy after deployment audit  
**Safe to delete**: Yes (if no longer needed after 30 days)
"""
    )

    print(f"\n[SUMMARY] Archive summary: {summary_file}")


if __name__ == "__main__":
    main()

