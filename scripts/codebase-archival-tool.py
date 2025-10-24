#!/usr/bin/env python3
"""
Codebase Archival Tool
Safely archives redundant files identified by the inventory analyzer.
"""

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ArchivalTool:
    def __init__(self, base_dir: Path, dry_run: bool = True):
        self.base_dir = base_dir
        self.dry_run = dry_run
        self.timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        self.archive_dir = base_dir / f"archive/cleanup-{self.timestamp}"
        self.manifest = []
        self.stats = {
            "files_archived": 0,
            "bytes_archived": 0,
            "errors": [],
        }

    def load_inventory(self, csv_path: Path) -> List[Dict]:
        """Load the inventory CSV and filter for redundant files."""
        redundant_files = []

        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "redundant":
                    redundant_files.append(row)

        return redundant_files

    def archive_file(self, file_info: Dict) -> bool:
        """Archive a single file, preserving directory structure."""
        source_path = self.base_dir / file_info["path"]

        if not source_path.exists():
            error = f"File not found: {file_info['path']}"
            self.stats["errors"].append(error)
            print(f"  ⚠️  {error}")
            return False

        # Preserve directory structure in archive
        rel_path = Path(file_info["path"])
        target_path = self.archive_dir / rel_path

        try:
            if self.dry_run:
                print(f"  [DRY RUN] Would move: {file_info['path']}")
                print(f"            Target: {target_path.relative_to(self.base_dir)}")
            else:
                # Create target directory
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(source_path), str(target_path))
                print(f"  ✓ Archived: {file_info['path']}")

            # Record in manifest
            self.manifest.append(
                {
                    "original_path": file_info["path"],
                    "archive_path": str(target_path.relative_to(self.base_dir)),
                    "size": int(file_info["size"]),
                    "category": file_info["category"],
                    "notes": file_info["notes"],
                }
            )

            self.stats["files_archived"] += 1
            self.stats["bytes_archived"] += int(file_info["size"])

            return True

        except Exception as e:
            error = f"Error archiving {file_info['path']}: {str(e)}"
            self.stats["errors"].append(error)
            print(f"  ❌ {error}")
            return False

    def generate_manifest(self):
        """Generate manifest file documenting the archival."""
        manifest_path = self.archive_dir / "ARCHIVAL_MANIFEST.json"

        manifest_data = {
            "timestamp": self.timestamp,
            "dry_run": self.dry_run,
            "statistics": {
                "files_archived": self.stats["files_archived"],
                "bytes_archived": self.stats["bytes_archived"],
                "size_mb": round(self.stats["bytes_archived"] / 1024 / 1024, 2),
                "errors_count": len(self.stats["errors"]),
            },
            "files": self.manifest,
            "errors": self.stats["errors"],
        }

        if not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)
            print(f"\n📋 Manifest saved: {manifest_path.relative_to(self.base_dir)}")
        else:
            print(f"\n📋 [DRY RUN] Manifest would be saved to: {manifest_path.relative_to(self.base_dir)}")

        return manifest_data

    def generate_rollback_script(self):
        """Generate PowerShell script to rollback the archival if needed."""
        rollback_path = self.archive_dir / "ROLLBACK.ps1"

        script_lines = [
            "# Rollback Script - Restore Archived Files",
            f"# Generated: {self.timestamp}",
            "# Run this script from the repository root to restore archived files",
            "",
            "$ErrorActionPreference = 'Stop'",
            "",
            'Write-Host "=" * 70',
            'Write-Host "Rollback: Restoring Archived Files"',
            'Write-Host "=" * 70',
            "",
            "$restoredCount = 0",
            "$errorCount = 0",
            "",
        ]

        for item in self.manifest:
            archive_rel = item["archive_path"].replace("\\", "/")
            original_rel = item["original_path"].replace("\\", "/")

            script_lines.extend(
                [
                    f"# Restore: {original_rel}",
                    f'if (Test-Path "{archive_rel}") {{',
                    f'    try {{',
                    f'        $targetDir = Split-Path "{original_rel}" -Parent',
                    f'        if ($targetDir -and !(Test-Path $targetDir)) {{',
                    f'            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null',
                    f'        }}',
                    f'        Move-Item -Path "{archive_rel}" -Destination "{original_rel}" -Force',
                    f'        Write-Host "✓ Restored: {original_rel}"',
                    f"        $restoredCount++",
                    f"    }} catch {{",
                    f'        Write-Host "❌ Error restoring {original_rel}: $_" -ForegroundColor Red',
                    f"        $errorCount++",
                    f"    }}",
                    f"}} else {{",
                    f'    Write-Host "⚠️  Not found in archive: {archive_rel}" -ForegroundColor Yellow',
                    f"}}",
                    "",
                ]
            )

        script_lines.extend(
            [
                'Write-Host "=" * 70',
                'Write-Host "Rollback Complete"',
                'Write-Host "Files Restored: $restoredCount"',
                'Write-Host "Errors: $errorCount"',
                'Write-Host "=" * 70',
            ]
        )

        if not self.dry_run:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            with open(rollback_path, "w", encoding="utf-8") as f:
                f.write("\n".join(script_lines))
            print(f"🔄 Rollback script saved: {rollback_path.relative_to(self.base_dir)}")
        else:
            print(f"🔄 [DRY RUN] Rollback script would be saved to: {rollback_path.relative_to(self.base_dir)}")

    def run(self, inventory_csv: Path):
        """Execute the archival process."""
        print("=" * 70)
        if self.dry_run:
            print("[DRY RUN MODE] - No files will be moved")
        else:
            print("[LIVE MODE] - Files will be archived")
        print("=" * 70)

        # Load redundant files from inventory
        print(f"\nLoading inventory from: {inventory_csv.name}")
        redundant_files = self.load_inventory(inventory_csv)
        print(f"   Found {len(redundant_files)} redundant files to archive")

        # Archive files
        print(f"\nArchiving to: {self.archive_dir.relative_to(self.base_dir)}\n")

        for file_info in redundant_files:
            self.archive_file(file_info)

        # Generate manifest and rollback script
        manifest_data = self.generate_manifest()
        self.generate_rollback_script()

        # Summary
        print("\n" + "=" * 70)
        print("📊 ARCHIVAL SUMMARY")
        print("=" * 70)
        print(f"Files Archived: {self.stats['files_archived']}")
        print(
            f"Space Reclaimed: {self.stats['bytes_archived'] / 1024 / 1024:.2f} MB"
        )
        print(f"Errors: {len(self.stats['errors'])}")

        if self.stats["errors"]:
            print("\n⚠️  Errors encountered:")
            for error in self.stats["errors"][:10]:
                print(f"  - {error}")
            if len(self.stats["errors"]) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")

        if self.dry_run:
            print("\n" + "=" * 70)
            print("✅ DRY RUN COMPLETE - No files were moved")
            print("   Run with --execute to perform actual archival")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("✅ ARCHIVAL COMPLETE")
            print(f"   Archive Location: {self.archive_dir.relative_to(self.base_dir)}")
            print(f"   To rollback, run: {self.archive_dir.relative_to(self.base_dir)}/ROLLBACK.ps1")
            print("=" * 70)

        return manifest_data


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Archive redundant codebase files")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute archival (default is dry-run)",
    )
    parser.add_argument(
        "--inventory",
        type=str,
        default="codebase-inventory.csv",
        help="Path to inventory CSV file",
    )

    args = parser.parse_args()

    base_dir = Path(r"C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD")
    inventory_path = base_dir / args.inventory

    if not inventory_path.exists():
        print(f"❌ Error: Inventory file not found: {inventory_path}")
        return 1

    # Run archival tool
    tool = ArchivalTool(base_dir, dry_run=not args.execute)
    tool.run(inventory_path)

    return 0


if __name__ == "__main__":
    exit(main())

