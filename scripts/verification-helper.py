    import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict
import csv
import json

#!/usr/bin/env python3
"""
Verification Helper Tool
Interactive tool to process files marked as "needs verification" in the codebase inventory.
"""


class VerificationHelper:
    def __init__(self, base_dir: Path, inventory_csv: Path):
        self.base_dir = base_dir
        self.inventory_csv = inventory_csv
        self.verification_files = []
        self.decisions = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

    def load_verification_files(self):
        """Load files marked as 'needs verification' from inventory."""
        print("Loading files needing verification...")

        with open(self.inventory_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["status"] == "needs verification":
                    self.verification_files.append(row)

        print(f"Found {len(self.verification_files)} files needing verification")
        return self.verification_files

    def analyze_file_content(self, file_path: Path) -> Dict:
        """Analyze file content to provide decision hints."""
        analysis = {
            "size": 0,
            "lines": 0,
            "content_preview": "",
            "hints": [],
            "category": "unknown",
        }

        try:
            if not file_path.exists():
                analysis["hints"].append("File not found")
                return analysis

            # Get file size
            analysis["size"] = file_path.stat().st_size

            # Read content for analysis
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")
                analysis["lines"] = len(lines)

                # Preview first 5 lines
                analysis["content_preview"] = "\n".join(lines[:5])

                # Analyze content for hints
                content_lower = content.lower()

                # Check for common patterns
                if "import " in content or "from " in content:
                    analysis["hints"].append("Contains imports - likely active code")

                if "def " in content or "function " in content:
                    analysis["hints"].append("Contains functions - likely active code")

                if "class " in content:
                    analysis["hints"].append("Contains classes - likely active code")

                if "export " in content or "module.exports" in content:
                    analysis["hints"].append("Contains exports - likely active code")

                if "main" in content_lower and "entry" in content_lower:
                    analysis["hints"].append("Mentions main/entry - likely entry point")

                if "test" in content_lower:
                    analysis["hints"].append("Contains test-related content")

                if "deploy" in content_lower:
                    analysis["hints"].append("Contains deployment-related content")

                if "TODO" in content or "FIXME" in content:
                    analysis["hints"].append(
                        "Contains TODO/FIXME - may be work in progress"
                    )

                if "deprecated" in content_lower or "old" in content_lower:
                    analysis["hints"].append(
                        "Mentions deprecated/old - likely redundant"
                    )

                if "complete" in content_lower and file_path.suffix == ".md":
                    analysis["hints"].append(
                        "Markdown with 'complete' - likely status report"
                    )

                if (
                    file_path.suffix in [".ps1", ".sh"]
                    and "test" in file_path.name.lower()
                ):
                    analysis["hints"].append("Test script - may be entry point")

                if (
                    file_path.suffix in [".ps1", ".sh"]
                    and "deploy" in file_path.name.lower()
                ):
                    analysis["hints"].append("Deploy script - likely entry point")

                if (
                    file_path.suffix in [".ps1", ".sh"]
                    and "clean" in file_path.name.lower()
                ):
                    analysis["hints"].append("Clean script - likely utility")

                # Determine category
                if file_path.suffix in [".ts", ".tsx", ".js", ".jsx", ".py"]:
                    analysis["category"] = "code"
                elif file_path.suffix in [".md", ".txt"]:
                    analysis["category"] = "documentation"
                elif file_path.suffix in [".ps1", ".sh"]:
                    analysis["category"] = "script"
                else:
                    analysis["category"] = "other"

        except Exception as e:
            analysis["hints"].append(f"Error analyzing file: {str(e)}")

        return analysis

    def get_decision_recommendation(self, file_info: Dict, analysis: Dict) -> str:
        """Get AI recommendation based on file info and analysis."""
        path = file_info["path"]
        category = file_info["category"]
        references = int(file_info["references"])

        # Strong keep signals
        if references > 0:
            return "KEEP - Has active references"

        if "likely active code" in str(analysis["hints"]):
            return "KEEP - Active code detected"

        if "likely entry point" in str(analysis["hints"]):
            return "KEEP - Appears to be entry point"

        if "likely utility" in str(analysis["hints"]):
            return "KEEP - Utility script"

        # Strong archive signals
        if "likely status report" in str(analysis["hints"]):
            return "ARCHIVE - Status report"

        if "likely redundant" in str(analysis["hints"]):
            return "ARCHIVE - Appears redundant"

        if category == "documentation" and analysis["size"] < 1000:
            return "ARCHIVE - Small documentation file"

        # Default to review
        return "REVIEW - Needs manual inspection"

    def process_file_interactive(self, file_info: Dict) -> Dict:
        """Process a single file with interactive decision making."""
        file_path = self.base_dir / file_info["path"]

        print(f"\n{'=' * 80}")
        print(f"FILE: {file_info['path']}")
        print(f"{'=' * 80}")
        print(f"Category: {file_info['category']}")
        print(f"Size: {file_info['size']} bytes")
        print(f"References: {file_info['references']}")
        print(f"Notes: {file_info['notes']}")

        # Analyze content
        analysis = self.analyze_file_content(file_path)

        print("\nContent Analysis:")
        print(f"Lines: {analysis['lines']}")
        print(f"Size: {analysis['size']} bytes")
        print(f"Category: {analysis['category']}")

        if analysis["hints"]:
            print("\nHints:")
            for hint in analysis["hints"]:
                print(f"  - {hint}")

        if analysis["content_preview"]:
            print("\nContent Preview:")
            print("```")
            print(analysis["content_preview"])
            print("```")

        # Get AI recommendation
        recommendation = self.get_decision_recommendation(file_info, analysis)
        print(f"\nAI Recommendation: {recommendation}")

        # Get user decision
        while True:
            print("\nDecision options:")
            print("  [K]eep - File is active and needed")
            print("  [A]rchive - File is redundant but preserve")
            print("  [D]elete - File is truly orphaned")
            print("  [S]kip - Review later")
            print("  [Q]uit - Exit processing")

            choice = input("\nEnter choice (K/A/D/S/Q): ").upper().strip()

            if choice in ["K", "A", "D", "S", "Q"]:
                break
            print("Invalid choice. Please enter K, A, D, S, or Q.")

        if choice == "Q":
            return {"action": "quit", "file": file_info["path"]}

        decision_map = {"K": "keep", "A": "archive", "D": "delete", "S": "skip"}

        decision = {
            "file": file_info["path"],
            "action": decision_map[choice],
            "recommendation": recommendation,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
        }

        self.decisions.append(decision)
        return decision

    def process_batch_mode(self, batch_size: int = 10):
        """Process files in batch mode for efficiency."""
        print(f"\nProcessing {len(self.verification_files)} files in batch mode...")

        for i, file_info in enumerate(self.verification_files):
            if i >= batch_size:
                break

            print(f"\n[{i + 1}/{batch_size}] Processing: {file_info['path']}")

            # Quick analysis
            file_path = self.base_dir / file_info["path"]
            analysis = self.analyze_file_content(file_path)
            recommendation = self.get_decision_recommendation(file_info, analysis)

            # Auto-decision based on strong signals
            if "KEEP - Has active references" in recommendation:
                decision = "keep"
            elif "ARCHIVE" in recommendation and "status report" in recommendation:
                decision = "archive"
            elif "ARCHIVE" in recommendation and "redundant" in recommendation:
                decision = "archive"
            else:
                decision = "review"

            decision_record = {
                "file": file_info["path"],
                "action": decision,
                "recommendation": recommendation,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
            }

            self.decisions.append(decision_record)
            print(f"  Auto-decision: {decision.upper()}")

    def generate_action_report(self):
        """Generate report of all decisions."""
        report_path = self.base_dir / f"verification-decisions-{self.timestamp}.json"

        # Categorize decisions
        keep_files = [d for d in self.decisions if d["action"] == "keep"]
        archive_files = [d for d in self.decisions if d["action"] == "archive"]
        delete_files = [d for d in self.decisions if d["action"] == "delete"]
        review_files = [d for d in self.decisions if d["action"] == "review"]
        skip_files = [d for d in self.decisions if d["action"] == "skip"]

        report = {
            "timestamp": self.timestamp,
            "total_files": len(self.verification_files),
            "decisions_made": len(self.decisions),
            "summary": {
                "keep": len(keep_files),
                "archive": len(archive_files),
                "delete": len(delete_files),
                "review": len(review_files),
                "skip": len(skip_files),
            },
            "decisions": self.decisions,
            "files_by_action": {
                "keep": [d["file"] for d in keep_files],
                "archive": [d["file"] for d in archive_files],
                "delete": [d["file"] for d in delete_files],
                "review": [d["file"] for d in review_files],
                "skip": [d["file"] for d in skip_files],
            },
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"\nDecision report saved: {report_path}")

        # Print summary
        print(f"\n{'=' * 60}")
        print("VERIFICATION SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total files processed: {len(self.decisions)}")
        print(f"Keep: {len(keep_files)}")
        print(f"Archive: {len(archive_files)}")
        print(f"Delete: {len(delete_files)}")
        print(f"Review: {len(review_files)}")
        print(f"Skip: {len(skip_files)}")

        return report

    def run(self, mode: str = "interactive", batch_size: int = 10):
        """Run the verification helper."""
        print("=" * 80)
        print("VERIFICATION HELPER TOOL")
        print("=" * 80)

        # Load files needing verification
        self.load_verification_files()

        if not self.verification_files:
            print("No files need verification!")
            return

        if mode == "interactive":
            print(f"\nProcessing {len(self.verification_files)} files interactively...")
            for file_info in self.verification_files:
                decision = self.process_file_interactive(file_info)
                if decision.get("action") == "quit":
                    break
        elif mode == "batch":
            self.process_batch_mode(batch_size)
        else:
            print(f"Unknown mode: {mode}")
            return

        # Generate report
        self.generate_action_report()

def main():
    """Main execution."""

    parser = argparse.ArgumentParser(description="Process files needing verification")
    parser.add_argument(
        "--mode",
        choices=["interactive", "batch"],
        default="interactive",
        help="Processing mode",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of files to process in batch mode",
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
        print(f"Error: Inventory file not found: {inventory_path}")
        return 1

    # Run verification helper
    helper = VerificationHelper(base_dir, inventory_path)
    helper.run(mode=args.mode, batch_size=args.batch_size)

    return 0

if __name__ == "__main__":
    exit(main())
