"""Conflict Resolver - Detects and merges parallel modifications to same file.

Part of ARMANI Squad for strategic integration. Performs intelligent conflict detection
and resolution using multiple strategies: auto-merge (imports, comments), three-way
merge (compatible changes), and manual review flagging (incompatible changes).
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "conflict_resolver"

__all__ = ["resolve", "Resolution", "ResolutionStrategy", "ChangeType", "Conflict"]


class ResolutionStrategy(Enum):
    """Conflict resolution strategy."""

    AUTO_MERGE = "auto_merge"
    THREE_WAY_MERGE = "three_way_merge"
    MANUAL_REVIEW = "manual_review"
    FAIL = "fail"


class ChangeType(Enum):
    """Type of change detected."""

    IMPORT = "import"
    COMMENT = "comment"
    FUNCTION_DEF = "function_def"
    CLASS_DEF = "class_def"
    VARIABLE = "variable"
    DOCSTRING = "docstring"
    CODE_BLOCK = "code_block"
    UNKNOWN = "unknown"


@dataclass
class Change:
    """Represents a change to a file."""

    change_type: ChangeType
    line_start: int
    line_end: int
    old_content: str
    new_content: str
    context: str


@dataclass
class Conflict:
    """Represents a conflict between two changes."""

    change_a: Change
    change_b: Change
    conflict_type: str
    resolution: str
    strategy: ResolutionStrategy
    confidence: str
    metadata: dict[str, Any]


@dataclass
class Resolution:
    """Complete resolution for a file conflict."""

    file_path: str
    conflicts: list[Conflict]
    resolved_content: str
    strategy: ResolutionStrategy
    success: bool
    manual_review_required: bool
    metadata: dict[str, Any]


def resolve(
    batch_a_changes: dict[str, Any], batch_b_changes: dict[str, Any]
) -> Resolution:
    """
    Resolve conflicts between parallel modifications from two batches.

    Resolution strategies:
    1. AUTO_MERGE: Imports, comments (always safe)
    2. THREE_WAY_MERGE: Compatible changes (non-overlapping)
    3. MANUAL_REVIEW: Function signatures, incompatible changes
    4. FAIL: Incompatible changes that cannot be merged

    Args:
        batch_a_changes: Changes from batch A {content, old_content, file_path}
        batch_b_changes: Changes from batch B {content, old_content, file_path}

    Returns:
        Resolution object with merged content and conflict details
    """
    config = load_extension_config()
    settings = config.get("conflict_resolver", {})

    if not settings.get("enabled", False):
        return Resolution(
            file_path="",
            conflicts=[],
            resolved_content="",
            strategy=ResolutionStrategy.FAIL,
            success=False,
            manual_review_required=True,
            metadata={"status": "disabled"},
        )

    file_path = batch_a_changes.get("file_path", batch_b_changes.get("file_path", ""))
    old_content = batch_a_changes.get("old_content", "")
    content_a = batch_a_changes.get("content", "")
    content_b = batch_b_changes.get("content", "")

    # Analyze changes in both batches
    changes_a = _analyze_changes(old_content, content_a)
    changes_b = _analyze_changes(old_content, content_b)

    # Detect conflicts
    conflicts = _detect_conflicts(changes_a, changes_b)

    # Resolve each conflict
    resolved_conflicts = []
    manual_review_required = False

    for conflict in conflicts:
        resolved_conflict = _resolve_conflict(conflict, old_content)
        resolved_conflicts.append(resolved_conflict)

        if resolved_conflict.strategy == ResolutionStrategy.MANUAL_REVIEW:
            manual_review_required = True

    # Merge resolved changes into final content
    resolved_content = _merge_changes(
        old_content, changes_a, changes_b, resolved_conflicts
    )

    # Determine overall strategy
    overall_strategy = _determine_overall_strategy(resolved_conflicts)

    success = overall_strategy != ResolutionStrategy.FAIL

    resolution = Resolution(
        file_path=file_path,
        conflicts=resolved_conflicts,
        resolved_content=resolved_content,
        strategy=overall_strategy,
        success=success,
        manual_review_required=manual_review_required,
        metadata={
            "total_conflicts": len(resolved_conflicts),
            "auto_merged": len(
                [c for c in resolved_conflicts if c.strategy == ResolutionStrategy.AUTO_MERGE]
            ),
            "manual_review": len(
                [c for c in resolved_conflicts if c.strategy == ResolutionStrategy.MANUAL_REVIEW]
            ),
            "failed": len(
                [c for c in resolved_conflicts if c.strategy == ResolutionStrategy.FAIL]
            ),
        },
    )

    # Persist resolution
    dump_jsonl(
        ARTIFACT_DIR / "resolutions.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "file_path": file_path,
            "strategy": overall_strategy.value,
            "success": success,
            "total_conflicts": len(resolved_conflicts),
        },
    )

    return resolution


def _analyze_changes(old_content: str, new_content: str) -> list[Change]:
    """
    Analyze changes between old and new content.

    Args:
        old_content: Original content
        new_content: Modified content

    Returns:
        List of Change objects
    """
    changes = []

    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    # Use difflib to identify changed lines
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace" or tag == "insert" or tag == "delete":
            old_chunk = "\n".join(old_lines[i1:i2])
            new_chunk = "\n".join(new_lines[j1:j2])

            # Classify change type
            change_type = _classify_change_type(new_chunk if tag != "delete" else old_chunk)

            # Get context (surrounding lines)
            context_start = max(0, i1 - 2)
            context_end = min(len(old_lines), i2 + 2)
            context = "\n".join(old_lines[context_start:context_end])

            changes.append(
                Change(
                    change_type=change_type,
                    line_start=i1,
                    line_end=i2,
                    old_content=old_chunk,
                    new_content=new_chunk,
                    context=context,
                )
            )

    return changes


def _classify_change_type(content: str) -> ChangeType:
    """
    Classify the type of change based on content.

    Args:
        content: Changed content

    Returns:
        ChangeType enum
    """
    content = content.strip()

    # Import statement
    if re.match(r"^(import\s+|from\s+.+import)", content):
        return ChangeType.IMPORT

    # Comment
    if re.match(r"^#", content):
        return ChangeType.COMMENT

    # Docstring
    if re.match(r'^("""|\'\'\')', content):
        return ChangeType.DOCSTRING

    # Function definition
    if re.match(r"^(async\s+)?def\s+\w+\s*\(", content):
        return ChangeType.FUNCTION_DEF

    # Class definition
    if re.match(r"^class\s+\w+", content):
        return ChangeType.CLASS_DEF

    # Variable assignment
    if re.match(r"^\w+\s*[=:]", content):
        return ChangeType.VARIABLE

    # Code block
    return ChangeType.CODE_BLOCK


def _detect_conflicts(
    changes_a: list[Change], changes_b: list[Change]
) -> list[Conflict]:
    """
    Detect conflicts between two sets of changes.

    Conflicts occur when:
    1. Same line range modified by both batches
    2. Overlapping line ranges with different content
    3. Incompatible changes (different function signatures)

    Args:
        changes_a: Changes from batch A
        changes_b: Changes from batch B

    Returns:
        List of Conflict objects
    """
    conflicts = []

    for change_a in changes_a:
        for change_b in changes_b:
            # Check for line range overlap
            if _ranges_overlap(
                change_a.line_start, change_a.line_end,
                change_b.line_start, change_b.line_end
            ):
                # Conflict detected
                conflict_type = _determine_conflict_type(change_a, change_b)

                conflicts.append(
                    Conflict(
                        change_a=change_a,
                        change_b=change_b,
                        conflict_type=conflict_type,
                        resolution="",
                        strategy=ResolutionStrategy.MANUAL_REVIEW,
                        confidence="low",
                        metadata={},
                    )
                )

    return conflicts


def _ranges_overlap(start1: int, end1: int, start2: int, end2: int) -> bool:
    """Check if two line ranges overlap."""
    return not (end1 < start2 or end2 < start1)


def _determine_conflict_type(change_a: Change, change_b: Change) -> str:
    """
    Determine the type of conflict.

    Args:
        change_a: Change from batch A
        change_b: Change from batch B

    Returns:
        Conflict type string
    """
    if change_a.change_type == change_b.change_type:
        return f"same_type_{change_a.change_type.value}"
    else:
        return f"different_type_{change_a.change_type.value}_vs_{change_b.change_type.value}"


def _resolve_conflict(conflict: Conflict, old_content: str) -> Conflict:
    """
    Resolve a single conflict using appropriate strategy.

    Args:
        conflict: Conflict to resolve
        old_content: Original content for three-way merge

    Returns:
        Resolved Conflict object
    """
    change_a = conflict.change_a
    change_b = conflict.change_b

    # Strategy 1: Auto-merge imports
    if change_a.change_type == ChangeType.IMPORT and change_b.change_type == ChangeType.IMPORT:
        conflict.resolution = _merge_imports(change_a, change_b)
        conflict.strategy = ResolutionStrategy.AUTO_MERGE
        conflict.confidence = "high"
        return conflict

    # Strategy 2: Auto-merge comments
    if change_a.change_type == ChangeType.COMMENT and change_b.change_type == ChangeType.COMMENT:
        conflict.resolution = _merge_comments(change_a, change_b)
        conflict.strategy = ResolutionStrategy.AUTO_MERGE
        conflict.confidence = "high"
        return conflict

    # Strategy 3: Auto-merge docstrings
    if change_a.change_type == ChangeType.DOCSTRING and change_b.change_type == ChangeType.DOCSTRING:
        conflict.resolution = _merge_docstrings(change_a, change_b)
        conflict.strategy = ResolutionStrategy.AUTO_MERGE
        conflict.confidence = "medium"
        return conflict

    # Strategy 4: Three-way merge for compatible changes
    if _are_changes_compatible(change_a, change_b):
        conflict.resolution = _three_way_merge(old_content, change_a, change_b)
        conflict.strategy = ResolutionStrategy.THREE_WAY_MERGE
        conflict.confidence = "medium"
        return conflict

    # Strategy 5: Manual review for incompatible changes
    conflict.resolution = _format_manual_review(change_a, change_b)
    conflict.strategy = ResolutionStrategy.MANUAL_REVIEW
    conflict.confidence = "low"

    return conflict


def _merge_imports(change_a: Change, change_b: Change) -> str:
    """
    Merge import statements from both changes.

    Args:
        change_a: Import change from batch A
        change_b: Import change from batch B

    Returns:
        Merged import statements
    """
    imports_a = set(change_a.new_content.splitlines())
    imports_b = set(change_b.new_content.splitlines())

    # Combine and sort imports
    all_imports = sorted(imports_a | imports_b)

    return "\n".join(all_imports)


def _merge_comments(change_a: Change, change_b: Change) -> str:
    """
    Merge comments from both changes.

    Args:
        change_a: Comment change from batch A
        change_b: Comment change from batch B

    Returns:
        Merged comments
    """
    # Combine comments with review marker
    return (
        f"{change_a.new_content}\n"
        f"# NOTE: Additional comment from parallel batch:\n"
        f"{change_b.new_content}"
    )


def _merge_docstrings(change_a: Change, change_b: Change) -> str:
    """
    Merge docstrings from both changes.

    Args:
        change_a: Docstring change from batch A
        change_b: Docstring change from batch B

    Returns:
        Merged docstring
    """
    # Use longer docstring with note about alternative
    if len(change_a.new_content) >= len(change_b.new_content):
        return change_a.new_content
    else:
        return change_b.new_content


def _are_changes_compatible(change_a: Change, change_b: Change) -> bool:
    """
    Check if two changes are compatible for three-way merge.

    Compatible changes:
    - Don't modify the same lines
    - Don't create conflicting function/class definitions
    - Don't create incompatible variable assignments

    Args:
        change_a: Change from batch A
        change_b: Change from batch B

    Returns:
        True if compatible, False otherwise
    """
    # Check if exact same content
    if change_a.new_content == change_b.new_content:
        return True

    # Check if different types (usually compatible)
    if change_a.change_type != change_b.change_type:
        return False

    # Variables and code blocks are usually incompatible
    if change_a.change_type in (ChangeType.VARIABLE, ChangeType.CODE_BLOCK):
        return False

    return False


def _three_way_merge(old_content: str, change_a: Change, change_b: Change) -> str:
    """
    Perform three-way merge of compatible changes.

    Args:
        old_content: Original content
        change_a: Change from batch A
        change_b: Change from batch B

    Returns:
        Merged content
    """
    # If changes are identical, use either
    if change_a.new_content == change_b.new_content:
        return change_a.new_content

    # Otherwise, combine both changes
    return f"{change_a.new_content}\n{change_b.new_content}"


def _format_manual_review(change_a: Change, change_b: Change) -> str:
    """
    Format conflict for manual review with markers.

    Args:
        change_a: Change from batch A
        change_b: Change from batch B

    Returns:
        Formatted conflict with markers
    """
    return f"""
<<<<<<< BATCH_A
{change_a.new_content}
=======
{change_b.new_content}
>>>>>>> BATCH_B
"""


def _merge_changes(
    old_content: str,
    changes_a: list[Change],
    changes_b: list[Change],
    resolved_conflicts: list[Conflict],
) -> str:
    """
    Merge all changes into final content.

    Args:
        old_content: Original content
        changes_a: Changes from batch A
        changes_b: Changes from batch B
        resolved_conflicts: Resolved conflicts

    Returns:
        Final merged content
    """
    lines = old_content.splitlines()

    # Build mapping of line ranges to resolved content
    resolutions = {}
    for conflict in resolved_conflicts:
        key = (conflict.change_a.line_start, conflict.change_a.line_end)
        resolutions[key] = conflict.resolution

    # Apply non-conflicting changes from batch A
    for change in changes_a:
        key = (change.line_start, change.line_end)
        if key not in resolutions:
            # Apply change
            for i in range(change.line_start, min(change.line_end, len(lines))):
                if i < len(lines):
                    lines[i] = change.new_content

    # Apply non-conflicting changes from batch B
    for change in changes_b:
        key = (change.line_start, change.line_end)
        if key not in resolutions:
            # Apply change
            for i in range(change.line_start, min(change.line_end, len(lines))):
                if i < len(lines):
                    lines[i] = change.new_content

    # Apply resolved conflicts
    for (start, end), resolution in resolutions.items():
        for i in range(start, min(end, len(lines))):
            if i < len(lines):
                lines[i] = resolution

    return "\n".join(lines)


def _determine_overall_strategy(conflicts: list[Conflict]) -> ResolutionStrategy:
    """
    Determine overall resolution strategy from individual conflicts.

    Args:
        conflicts: List of resolved conflicts

    Returns:
        Overall ResolutionStrategy
    """
    if not conflicts:
        return ResolutionStrategy.AUTO_MERGE

    strategies = [c.strategy for c in conflicts]

    # If any conflict requires manual review, overall requires manual review
    if ResolutionStrategy.MANUAL_REVIEW in strategies:
        return ResolutionStrategy.MANUAL_REVIEW

    # If any conflict failed, overall fails
    if ResolutionStrategy.FAIL in strategies:
        return ResolutionStrategy.FAIL

    # If all auto-merged
    if all(s == ResolutionStrategy.AUTO_MERGE for s in strategies):
        return ResolutionStrategy.AUTO_MERGE

    # Otherwise, three-way merge
    return ResolutionStrategy.THREE_WAY_MERGE


def cli() -> None:
    """CLI entry point for conflict resolver."""
    print("Conflict Resolver - ARMANI Squad")
    print("Run via elite_weaver.run() for full conflict resolution")
