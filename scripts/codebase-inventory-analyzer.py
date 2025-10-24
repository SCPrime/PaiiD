#!/usr/bin/env python3
"""
Codebase Inventory Analyzer
Analyzes the PaiiD codebase to classify files and detect usage patterns.
"""

import csv
import os
import re
from collections import defaultdict
from pathlib import Path

# Base directory
BASE_DIR = Path(r"C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD")

# Directories to analyze
ANALYZE_DIRS = ["frontend", "backend", "db"]

# File classification patterns
CODE_EXTENSIONS = {
    ".ts",
    ".tsx",
    ".js",
    ".jsx",  # TypeScript/JavaScript
    ".py",  # Python
    ".sh",
    ".ps1",  # Scripts
    ".sql",  # SQL
    ".yml",
    ".yaml",
    ".json",  # Config files
}

DOC_EXTENSIONS = {".md", ".txt"}

# Patterns that suggest redundancy
REDUNDANT_PATTERNS = [
    r"OLD_",
    r"BACKUP",
    r"DEPRECATED",
    r"ARCHIVE",
    r"COMPLETE\.md$",
    r"SUMMARY\.md$",
    r"REPORT.*\.md$",
    r"STATUS.*\.md$",
    r"VERIFICATION.*\.md$",
    r"DEPLOYMENT.*\.md$",
    r"-\d{8}",  # Date patterns like -20251023
    r"_\d{4}-\d{2}-\d{2}",  # Date patterns like _2025-10-23
    r"test-report-",
    r"health-report-",
    r"deployment-report-",
]

# Directories to exclude from analysis
EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "coverage",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    "test-results",
    "playwright-report",
    ".next",
    "archive",
}


class CodebaseAnalyzer:
    def __init__(self):
        self.files_data = []
        self.reference_cache = {}
        self.stats = defaultdict(int)

    def should_analyze_file(self, file_path: Path) -> bool:
        """Determine if a file should be analyzed."""
        # Skip excluded directories
        for part in file_path.parts:
            if part in EXCLUDE_DIRS:
                return False

        # Only analyze files in target directories or root
        rel_path = file_path.relative_to(BASE_DIR)
        if len(rel_path.parts) > 1:
            if rel_path.parts[0] not in ANALYZE_DIRS:
                return False

        return True

    def classify_file(self, file_path: Path) -> str:
        """Classify file as code, documentation, or other."""
        ext = file_path.suffix.lower()

        if ext in CODE_EXTENSIONS:
            return "Code"
        elif ext in DOC_EXTENSIONS:
            return "Documentation"
        else:
            return "Other"

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        try:
            return file_path.stat().st_size
        except:
            return 0

    def search_references(self, file_path: Path) -> int:
        """Search for references to this file in the codebase."""
        # Get relative path for searching
        rel_path = file_path.relative_to(BASE_DIR)
        file_name = file_path.name
        stem = file_path.stem

        # Search patterns
        patterns = [
            file_name,  # Exact filename
            stem,  # Filename without extension
        ]

        # For code files, add import patterns
        if file_path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            # TypeScript/JavaScript import patterns
            patterns.extend(
                [
                    f"from.*['\"].*{stem}",
                    f"import.*['\"].*{stem}",
                    f"require.*['\"].*{stem}",
                ]
            )
        elif file_path.suffix == ".py":
            # Python import patterns
            patterns.extend(
                [
                    f"from.*{stem}",
                    f"import.*{stem}",
                ]
            )

        reference_count = 0
        search_dirs = [BASE_DIR / d for d in ANALYZE_DIRS]

        # Search for references
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for pattern in patterns:
                # Count files that reference this pattern
                for search_file in search_dir.rglob("*"):
                    if not search_file.is_file():
                        continue
                    if search_file == file_path:
                        continue
                    if not self.should_analyze_file(search_file):
                        continue

                    # Only search in code files
                    if search_file.suffix not in CODE_EXTENSIONS:
                        continue

                    try:
                        content = search_file.read_text(
                            encoding="utf-8", errors="ignore"
                        )
                        if re.search(pattern, content, re.IGNORECASE):
                            reference_count += 1
                            break  # Count each file only once
                    except:
                        continue

        return reference_count

    def is_potentially_redundant(self, file_path: Path) -> bool:
        """Check if file matches redundancy patterns."""
        file_str = str(file_path)

        for pattern in REDUNDANT_PATTERNS:
            if re.search(pattern, file_str, re.IGNORECASE):
                return True

        return False

    def tag_artifact(self, file_path: Path, reference_count: int, category: str) -> str:
        """Tag artifact as current, redundant, or needs verification."""

        # Documentation files with no references
        if category == "Documentation":
            if reference_count > 0:
                return "current"
            elif self.is_potentially_redundant(file_path):
                return "redundant"
            else:
                return "needs verification"

        # Code files
        if category == "Code":
            if reference_count > 0:
                return "current"

            # Check if it's an entry point or standalone script
            name_lower = file_path.name.lower()
            if any(
                x in name_lower
                for x in ["main", "index", "app", "start", "deploy", "test"]
            ):
                return "needs verification"

            if self.is_potentially_redundant(file_path):
                return "redundant"

            return "needs verification"

        # Other files
        return "needs verification"

    def analyze_file(self, file_path: Path):
        """Analyze a single file."""
        if not self.should_analyze_file(file_path):
            return

        try:
            rel_path = file_path.relative_to(BASE_DIR)
            category = self.classify_file(file_path)
            file_size = self.get_file_size(file_path)

            # For documentation and other files, always search references
            # For code files, search selectively (expensive operation)
            if category in ["Documentation", "Other"]:
                reference_count = self.search_references(file_path)
            else:
                # For code files, do a quick check
                reference_count = self.search_references(file_path)

            status_tag = self.tag_artifact(file_path, reference_count, category)

            # Determine notes
            notes = []
            if self.is_potentially_redundant(file_path):
                notes.append("Matches redundancy pattern")
            if reference_count == 0 and category == "Code":
                notes.append("No references found - may be entry point")

            self.files_data.append(
                {
                    "path": str(rel_path).replace("\\", "/"),
                    "category": category,
                    "extension": file_path.suffix,
                    "size": file_size,
                    "status": status_tag,
                    "references": reference_count,
                    "notes": "; ".join(notes),
                }
            )

            # Update stats
            self.stats[f"{category}_total"] += 1
            self.stats[f"{status_tag}_total"] += 1

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def collect_files(self):
        """Collect all files to analyze."""
        print("Collecting files...")

        # Analyze root directory files
        for item in BASE_DIR.iterdir():
            if item.is_file():
                self.analyze_file(item)

        # Analyze target directories
        for dir_name in ANALYZE_DIRS:
            dir_path = BASE_DIR / dir_name
            if not dir_path.exists():
                continue

            print(f"Analyzing {dir_name}/...")
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    self.analyze_file(file_path)

        print(f"Collected {len(self.files_data)} files")

    def generate_csv(self, output_path: Path):
        """Generate CSV inventory."""
        print(f"Generating CSV: {output_path}")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "path",
                    "category",
                    "extension",
                    "size",
                    "status",
                    "references",
                    "notes",
                ],
            )
            writer.writeheader()

            # Sort by status (redundant first), then by category, then by path
            sorted_data = sorted(
                self.files_data,
                key=lambda x: (
                    {"redundant": 0, "needs verification": 1, "current": 2}[
                        x["status"]
                    ],
                    x["category"],
                    x["path"],
                ),
            )

            for row in sorted_data:
                writer.writerow(row)

        print(f"CSV generated with {len(self.files_data)} entries")

    def generate_report(self, output_path: Path):
        """Generate markdown report."""
        print(f"Generating report: {output_path}")

        # Calculate statistics
        redundant_files = [f for f in self.files_data if f["status"] == "redundant"]
        needs_verification = [
            f for f in self.files_data if f["status"] == "needs verification"
        ]
        current_files = [f for f in self.files_data if f["status"] == "current"]

        code_files = [f for f in self.files_data if f["category"] == "Code"]
        doc_files = [f for f in self.files_data if f["category"] == "Documentation"]
        other_files = [f for f in self.files_data if f["category"] == "Other"]

        # Calculate total size
        total_size = sum(f["size"] for f in self.files_data)
        redundant_size = sum(f["size"] for f in redundant_files)

        report = f"""# Codebase Inventory Report
Generated: {os.popen("date /t").read().strip()} {os.popen("time /t").read().strip()}

## Executive Summary

### Overall Statistics
- **Total Files Analyzed**: {len(self.files_data)}
- **Total Size**: {total_size / 1024 / 1024:.2f} MB
- **Code Files**: {len(code_files)}
- **Documentation Files**: {len(doc_files)}
- **Other Files**: {len(other_files)}

### Status Breakdown
- **Current** (actively referenced): {len(current_files)} ({len(current_files) / len(self.files_data) * 100:.1f}%)
- **Redundant** (archival candidates): {len(redundant_files)} ({len(redundant_files) / len(self.files_data) * 100:.1f}%)
- **Needs Verification**: {len(needs_verification)} ({len(needs_verification) / len(self.files_data) * 100:.1f}%)

### Potential Space Savings
- **Redundant File Size**: {redundant_size / 1024 / 1024:.2f} MB
- **Archival Candidates**: {len(redundant_files)} files

---

## Redundant Files (Archival Candidates)

These files match redundancy patterns and have no active references:

### Documentation ({len([f for f in redundant_files if f["category"] == "Documentation"])})
"""

        # List redundant documentation
        redundant_docs = [
            f for f in redundant_files if f["category"] == "Documentation"
        ]
        for file_data in sorted(redundant_docs, key=lambda x: x["path"])[:50]:
            report += f"- `{file_data['path']}` ({file_data['size'] / 1024:.1f} KB)\n"

        if len(redundant_docs) > 50:
            report += f"\n... and {len(redundant_docs) - 50} more (see CSV for complete list)\n"

        report += f"\n### Code Files ({len([f for f in redundant_files if f['category'] == 'Code'])})\n"

        # List redundant code
        redundant_code = [f for f in redundant_files if f["category"] == "Code"]
        for file_data in sorted(redundant_code, key=lambda x: x["path"])[:30]:
            report += f"- `{file_data['path']}` ({file_data['size'] / 1024:.1f} KB) - {file_data['notes']}\n"

        if len(redundant_code) > 30:
            report += f"\n... and {len(redundant_code) - 30} more (see CSV for complete list)\n"

        report += f"""

---

## Files Needing Verification

These files have no clear references but don't match redundancy patterns. 
They may be entry points, standalone scripts, or truly orphaned files.

### High Priority (Code Files - {len([f for f in needs_verification if f["category"] == "Code"])})
"""

        # List code files needing verification
        verify_code = [f for f in needs_verification if f["category"] == "Code"]
        for file_data in sorted(verify_code, key=lambda x: x["path"])[:30]:
            report += f"- `{file_data['path']}` (refs: {file_data['references']})\n"

        if len(verify_code) > 30:
            report += (
                f"\n... and {len(verify_code) - 30} more (see CSV for complete list)\n"
            )

        report += f"\n### Medium Priority (Documentation - {len([f for f in needs_verification if f['category'] == 'Documentation'])})\n"

        # List docs needing verification
        verify_docs = [
            f for f in needs_verification if f["category"] == "Documentation"
        ]
        for file_data in sorted(verify_docs, key=lambda x: x["path"])[:20]:
            report += f"- `{file_data['path']}`\n"

        if len(verify_docs) > 20:
            report += (
                f"\n... and {len(verify_docs) - 20} more (see CSV for complete list)\n"
            )

        report += f"""

---

## Current Files

{len(current_files)} files are actively referenced and in use.

### By Category
- **Code**: {len([f for f in current_files if f["category"] == "Code"])} files
- **Documentation**: {len([f for f in current_files if f["category"] == "Documentation"])} files
- **Other**: {len([f for f in current_files if f["category"] == "Other"])} files

See CSV file for complete listing.

---

## Recommendations

### Immediate Actions
1. **Archive Redundant Files**: Move {len(redundant_files)} redundant files to `archive/` directory
   - Estimated space savings: {redundant_size / 1024 / 1024:.2f} MB
   - Focus on dated reports, COMPLETE.md files, and OLD_* files

2. **Review High Priority Files**: Verify {len([f for f in needs_verification if f["category"] == "Code"])} code files with no references
   - These may be entry points or truly orphaned code
   - Determine if they can be deleted or need to be archived

3. **Clean Documentation**: Review {len([f for f in needs_verification if f["category"] == "Documentation"])} documentation files
   - Update README files to reference current documentation
   - Archive or delete outdated guides

### Long-term Actions
1. **Establish Naming Conventions**: Prevent future redundancy by:
   - Using consistent naming for active vs archived files
   - Implementing automatic archival of dated reports
   - Creating a single source of truth for each topic

2. **Regular Audits**: Schedule quarterly codebase inventories to prevent accumulation

3. **Documentation Standards**: Maintain a documentation index that tracks:
   - Active documentation
   - Deprecated/archived documentation
   - Ownership and last update dates

---

## Next Steps

1. Review this report with project leads
2. Get approval for archival candidates listed above
3. Execute archival plan using the CSV file as reference
4. Update project documentation index

For detailed information on each file, refer to: `codebase-inventory.csv`
"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"Report generated: {output_path}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("PaiiD Codebase Inventory Analyzer")
    print("=" * 70)

    analyzer = CodebaseAnalyzer()

    # Collect and analyze files
    analyzer.collect_files()

    # Generate outputs
    csv_path = BASE_DIR / "codebase-inventory.csv"
    report_path = BASE_DIR / "CODEBASE_INVENTORY_REPORT.md"

    analyzer.generate_csv(csv_path)
    analyzer.generate_report(report_path)

    print("=" * 70)
    print("Analysis Complete!")
    print(f"CSV: {csv_path}")
    print(f"Report: {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
