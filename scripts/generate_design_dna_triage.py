"""Generate structured triage data for Design DNA violations.

This utility mirrors the validation logic from `design-dna-validator.py`
and writes a JSON summary that categorises each violating component as
either active or archived. The JSON artifact assists the orchestrator in
assigning remediation work across agent batches.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

APPROVED_COLORS = {
    "#16a394",
    "#00ACC1",
    "#7E57C2",
    "#45f0c0",
    "#0097A7",
    "#00C851",
    "#5E35B1",
    "#00BCD4",
    "#FF4444",
    "#F97316",
    "#64748b",
    "#FF8800",
    "#0f172a",
    "#1a2a3f",
    "#f1f5f9",
    "#cbd5e1",
    "#94a3b8",
    "#e2e8f0",
}

BANNED_PATTERNS = (
    (r"padding:\s*\d+px", "spacing_px"),
    (r"margin:\s*\d+px", "spacing_px"),
    (r"background:\s*(?!.*backdrop-filter)", "missing_glass_background"),
    (r"box-shadow:\s*\d+px\s+\d+px", "hard_shadow"),
)


HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{6}\b", re.IGNORECASE)
APPROVED_LOOKUP = {color.lower() for color in APPROVED_COLORS}


@dataclass(slots=True)
class ViolationRecord:
    file: str
    status: str
    issues: list[str]


def classify_status(relative_path: Path) -> str:
    """Determine whether the flagged component is active or archived."""

    lowered = str(relative_path).lower()
    if ".archived" in lowered or "claude_desktop_files" in lowered:
        return "archived"
    return "active"


def gather_violations(repo_root: Path) -> list[ViolationRecord]:
    """Collect violations across frontend components and pages."""

    frontend_dir = repo_root / "frontend"
    scan_targets = [frontend_dir / "components", frontend_dir / "pages"]
    violations: list[ViolationRecord] = []

    for target in scan_targets:
        if not target.exists():
            continue

        for tsx_path in target.rglob("*.tsx"):
            if any(part in {"node_modules", ".next"} for part in tsx_path.parts):
                continue

            issues: set[str] = set()
            content = tsx_path.read_text(encoding="utf-8")

            found_colors = {color.lower() for color in HEX_PATTERN.findall(content)}
            if any(color not in APPROVED_LOOKUP for color in found_colors):
                issues.add("unapproved_color")

            for pattern, label in BANNED_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    issues.add(label)

            for match in re.finditer(r"height:\s*(\d+)px", content):
                if int(match.group(1)) < 40:
                    issues.add("button_height_below_min")

            if issues:
                relative = tsx_path.relative_to(repo_root)
                violations.append(
                    ViolationRecord(
                        file=str(relative).replace("\\", "/"),
                        status=classify_status(relative),
                        issues=sorted(issues),
                    )
                )

    violations.sort(key=lambda record: record.file)
    return violations


def write_triage(violations: list[ViolationRecord], destination: Path) -> None:
    """Write the triage payload to disk as JSON."""

    payload = {
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "summary": {
            "total": len(violations),
            "active": sum(1 for record in violations if record.status == "active"),
            "archived": sum(1 for record in violations if record.status == "archived"),
        },
        "violations": [
            {
                "file": record.file,
                "status": record.status,
                "issues": record.issues,
            }
            for record in violations
        ],
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    violations = gather_violations(repo_root)
    destination = (
        repo_root / "modsquad" / "logs" / "run-history" / "design_dna_triage.json"
    )
    write_triage(violations, destination)
    print(f"[OK] Design DNA triage written to {destination}")


if __name__ == "__main__":
    main()
