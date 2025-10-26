#!/usr/bin/env python3
"""
Universal Backend Authentication Fixer

This script automatically updates all backend router files to use unified authentication
instead of JWT-only auth, resolving "Invalid token: Not enough segments" errors.

Changes:
- Replace: from ..core.jwt import get_current_user
- With: from ..core.unified_auth import get_current_user_unified
- Update all Depends(get_current_user) to Depends(get_current_user_unified)
- Fix typo: get_current_user_id_id -> get_current_user_unified

Author: Claude Code
Date: 2025-10-25
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Files to update (relative to backend/app/routers/)
ROUTER_FILES = [
    "market_data.py",
    "news.py",
    "stock.py",
    "stream.py",
    "portfolio.py",
    "positions.py",
    "screening.py",
    "strategies.py",
    "proposals.py",
    "claude.py",
    "health.py",
    "monitor.py",
    "scheduler.py",
    "settings.py",
    "users.py",
    "ml_sentiment.py",
    "ai.py",
]

# Files that should NOT be changed
EXCLUDE_FILES = [
    "auth.py",  # Auth router uses different pattern
    "options.py",  # Already uses unified auth
    "orders.py",  # Already uses unified auth
]


def find_backend_dir() -> Path:
    """Find the backend directory from current location."""
    current = Path(__file__).parent
    # Script is in scripts/, backend is sibling to scripts/
    backend_dir = current.parent / "backend"

    if not backend_dir.exists():
        raise FileNotFoundError(
            f"Backend directory not found at {backend_dir}. "
            f"Please run this script from the PaiiD repository root."
        )

    return backend_dir


def backup_file(file_path: Path) -> Path:
    """Create a backup of the original file."""
    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
    backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def fix_imports(content: str) -> Tuple[str, List[str]]:
    """Fix import statements to use unified auth."""
    changes = []

    # Pattern 1: JWT-only import
    old_jwt_import = r"from \.\.core\.jwt import get_current_user"
    new_unified_import = "from ..core.unified_auth import get_current_user_unified"

    if re.search(old_jwt_import, content):
        content = re.sub(old_jwt_import, new_unified_import, content)
        changes.append("Updated import: jwt.get_current_user → unified_auth.get_current_user_unified")

    # Pattern 2: Legacy auth import
    old_auth_import = r"from \.\.core\.auth import get_current_user_id"

    if re.search(old_auth_import, content):
        # Check if unified import already exists
        if "from ..core.unified_auth import get_current_user_unified" not in content:
            # Add unified import after the legacy import
            content = re.sub(
                old_auth_import,
                f"{old_auth_import}\n{new_unified_import}",
                content
            )
        changes.append("Added unified auth import alongside legacy auth")

    # Pattern 3: Typo fix (get_current_user_id_id)
    typo_pattern = r"get_current_user_id_id"
    if re.search(typo_pattern, content):
        content = re.sub(typo_pattern, "get_current_user_unified", content)
        changes.append("Fixed typo: get_current_user_id_id → get_current_user_unified")

    return content, changes


def fix_dependencies(content: str) -> Tuple[str, List[str]]:
    """Fix Depends() calls to use unified auth."""
    changes = []

    # Pattern 1: Depends(get_current_user) with type annotation
    pattern1 = r"current_user:\s*User\s*=\s*Depends\(get_current_user\)"
    replacement1 = "current_user: User = Depends(get_current_user_unified)"

    matches = len(re.findall(pattern1, content))
    if matches > 0:
        content = re.sub(pattern1, replacement1, content)
        changes.append(f"Updated {matches} Depends(get_current_user) → Depends(get_current_user_unified)")

    # Pattern 2: Depends(get_current_user) without type annotation
    pattern2 = r"Depends\(get_current_user\)"
    # Only replace if not already replaced by pattern1
    if re.search(pattern2, content) and "get_current_user_unified" not in content:
        content = re.sub(pattern2, "Depends(get_current_user_unified)", content)
        changes.append("Updated bare Depends(get_current_user) calls")

    # Pattern 3: Legacy auth dependency
    pattern3 = r"user_id:\s*int\s*=\s*Depends\(get_current_user_id\)"
    replacement3 = "current_user: User = Depends(get_current_user_unified)"

    if re.search(pattern3, content):
        content = re.sub(pattern3, replacement3, content)
        changes.append("Updated legacy Depends(get_current_user_id) → Depends(get_current_user_unified)")

    return content, changes


def process_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Process a single router file.

    Returns:
        (success: bool, changes: List[str])
    """
    try:
        # Read original content
        original_content = file_path.read_text(encoding="utf-8")

        # Skip if file already uses unified auth exclusively
        if (
            "from ..core.unified_auth import get_current_user_unified" in original_content
            and "from ..core.jwt import get_current_user" not in original_content
            and "get_current_user_id_id" not in original_content
        ):
            return True, ["Already using unified auth - no changes needed"]

        # Create backup
        backup_path = backup_file(file_path)

        # Apply fixes
        content = original_content
        all_changes = []

        content, import_changes = fix_imports(content)
        all_changes.extend(import_changes)

        content, dep_changes = fix_dependencies(content)
        all_changes.extend(dep_changes)

        # Only write if changes were made
        if all_changes and content != original_content:
            file_path.write_text(content, encoding="utf-8")
            all_changes.insert(0, f"✅ Backup created: {backup_path.name}")
            return True, all_changes
        else:
            # Remove backup if no changes
            backup_path.unlink()
            return True, ["No changes needed"]

    except Exception as e:
        return False, [f"❌ Error: {str(e)}"]


def main():
    """Main execution function."""
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == "win32":
        import codecs
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 80)
    print("🔧 UNIVERSAL BACKEND AUTHENTICATION FIXER")
    print("=" * 80)
    print()

    # Find backend directory
    try:
        backend_dir = find_backend_dir()
        routers_dir = backend_dir / "app" / "routers"
        print(f"📁 Backend directory: {backend_dir}")
        print(f"📁 Routers directory: {routers_dir}")
        print()
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return 1

    # Process each file
    results = {}
    total_files = len(ROUTER_FILES)

    print(f"📝 Processing {total_files} router files...")
    print()

    for filename in ROUTER_FILES:
        file_path = routers_dir / filename

        if not file_path.exists():
            print(f"⚠️  {filename} - File not found, skipping")
            results[filename] = (False, ["File not found"])
            continue

        print(f"🔍 Processing: {filename}")
        success, changes = process_file(file_path)
        results[filename] = (success, changes)

        for change in changes:
            print(f"   {change}")
        print()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)

    successful = sum(1 for success, _ in results.values() if success)
    failed = total_files - successful

    print(f"✅ Successful: {successful}/{total_files}")
    print(f"❌ Failed: {failed}/{total_files}")
    print()

    if failed > 0:
        print("Failed files:")
        for filename, (success, changes) in results.items():
            if not success:
                print(f"  - {filename}: {changes[0]}")
        print()

    # List backup files
    backup_files = list(routers_dir.glob("*.backup"))
    if backup_files:
        print(f"💾 {len(backup_files)} backup files created in {routers_dir}")
        print("   To restore a file: mv <file>.backup <file>")
        print("   To remove backups: rm *.backup")
        print()

    print("✨ Next steps:")
    print("   1. Run: cd backend && ruff check app/routers/")
    print("   2. Test: python -m uvicorn app.main:app --reload --port 8001")
    print("   3. Verify with Thunder Client or browser debugging")
    print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
