#!/usr/bin/env python3
"""Design DNA validator for MOD SQUAD.

Enforces brand compliance per frontend/DESIGN_DNA.md.
Runs as pre-commit hook and CI check.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Approved color palette (hex codes from DESIGN_DNA.md)
APPROVED_COLORS = {
    "#16a394",  # Teal primary
    "#00ACC1",  # Teal secondary
    "#7E57C2",  # Purple accent
    "#45f0c0",  # AI glow cyan
    "#0097A7",  # Dark teal
    "#00C851",  # Green success
    "#5E35B1",  # Deep purple
    "#00BCD4",  # Cyan
    "#FF4444",  # Red danger
    "#F97316",  # Orange
    "#64748b",  # Slate gray
    "#FF8800",  # Orange warning
    "#0f172a",  # Base dark
    "#1a2a3f",  # Gradient dark
    "#f1f5f9",  # Primary text
    "#cbd5e1",  # Muted text
    "#94a3b8",  # Secondary muted
    "#e2e8f0",  # Light text
}

# Banned patterns
BANNED_PATTERNS = [
    (r"padding:\s*\d+px", "Use Tailwind spacing classes (p-1, p-2, etc.) instead of px values"),
    (r"margin:\s*\d+px", "Use Tailwind spacing classes (m-1, m-2, etc.) instead of px values"),
    (
        r"background:\s*(?!.*backdrop-filter)",
        "Solid backgrounds require backdrop-filter for glassmorphic effect",
    ),
    (r"box-shadow:\s*\d+px\s+\d+px", "Use glow effects (0 0 20px rgba...) not hard shadows"),
]


def check_file(file_path: Path) -> list[str]:
    """Check a single file for DNA violations."""
    violations = []
    content = file_path.read_text(encoding="utf-8")

    # Check for unapproved colors
    hex_pattern = r"#[0-9a-fA-F]{6}\b"
    found_colors = set(re.findall(hex_pattern, content, re.IGNORECASE))
    for color in found_colors:
        if color.lower() not in {c.lower() for c in APPROVED_COLORS}:
            violations.append(
                f"  ❌ Unapproved color {color} (use teal/purple palette from DESIGN_DNA.md)"
            )

    # Check for banned patterns
    for pattern, message in BANNED_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            violations.append(f"  ❌ {message}")

    # Check button height (minimum 40px)
    button_height_pattern = r"height:\s*(\d+)px"
    for match in re.finditer(button_height_pattern, content):
        height = int(match.group(1))
        if height < 40:
            violations.append(
                f"  ❌ Button height {height}px below minimum 40px (line near: {match.group(0)})"
            )

    return violations


def main() -> int:
    """Run validator on staged files or all components."""
    repo_root = Path(__file__).resolve().parents[1]
    frontend_dir = repo_root / "frontend"

    if not frontend_dir.exists():
        print("⚠️  Frontend directory not found; skipping DNA validation")
        return 0

    component_dirs = [
        frontend_dir / "components",
        frontend_dir / "pages",
    ]

    all_violations = []
    files_checked = 0

    for component_dir in component_dirs:
        if not component_dir.exists():
            continue

        for tsx_file in component_dir.rglob("*.tsx"):
            # Skip node_modules, .next
            if "node_modules" in str(tsx_file) or ".next" in str(tsx_file):
                continue

            violations = check_file(tsx_file)
            if violations:
                all_violations.append((tsx_file.relative_to(repo_root), violations))
            files_checked += 1

    if all_violations:
        print("\n🚨 Design DNA Violations Detected:\n")
        for file_path, violations in all_violations:
            print(f"📄 {file_path}")
            for violation in violations:
                print(violation)
            print()
        print(f"❌ {len(all_violations)} file(s) violated Design DNA rules")
        print(f"📖 See frontend/DESIGN_DNA.md for approved palette and patterns\n")
        return 1

    print(f"✅ Design DNA validation passed ({files_checked} files checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

