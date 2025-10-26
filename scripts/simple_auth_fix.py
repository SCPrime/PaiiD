#!/usr/bin/env python3
"""
Simple Auth Fix - Manually updates each file with straightforward replacements
"""

import sys
from pathlib import Path

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# File-specific fixes
FILES_TO_FIX = {
    "backend/app/routers/ai.py": {
        "imports_to_add": ["from ..core.auth import require_bearer", "from ..core.unified_auth import get_current_user_unified"],
        "imports_to_remove": ["from ..core.auth import get_current_user_id, require_bearer"],
        "replacements": [
            ("Depends(get_current_user_id)", "Depends(get_current_user_unified)"),
        ]
    },
    "backend/app/routers/ml_sentiment.py": {
        "imports_to_add": ["from ..core.unified_auth import get_current_user_unified"],
        "imports_to_remove": ["from ..core.auth import get_current_user_id_id"],
        "replacements": [
            ("Depends(get_current_user_id_id)", "Depends(get_current_user_unified)"),
        ]
    },
    # ... (would need to add all 17 files manually)
}

def main():
    root = Path(__file__).parent.parent

    for file_path, fixes in FILES_TO_FIX.items():
        full_path = root / file_path
        print(f"Processing: {file_path}")

        if not full_path.exists():
            print(f"  SKIP: File not found")
            continue

        content = full_path.read_text(encoding="utf-8")
        original_content = content

        # Remove old imports
        for old_import in fixes.get("imports_to_remove", []):
            if old_import in content:
                content = content.replace(old_import + "\n", "")
                print(f"  Removed: {old_import}")

        # Add new imports (after other imports)
        for new_import in fixes.get("imports_to_add", []):
            if new_import not in content:
                # Find last import line and add after it
                lines = content.split("\n")
                last_import_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith("from") or line.startswith("import"):
                        last_import_idx = i
                lines.insert(last_import_idx + 1, new_import)
                content = "\n".join(lines)
                print(f"  Added: {new_import}")

        # Apply replacements
        for old, new in fixes.get("replacements", []):
            count = content.count(old)
            if count > 0:
                content = content.replace(old, new)
                print(f"  Replaced {count}x: {old} -> {new}")

        if content != original_content:
            full_path.write_text(content, encoding="utf-8")
            print(f"  ✅ Updated successfully")
        else:
            print(f"  No changes needed")
        print()

if __name__ == "__main__":
    main()
